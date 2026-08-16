"""
Lean 2.0 Maturity API -- Industry 5.0 Extended Dimensions (DB-Backed)

Five dimensions: Operations(O), Digital(D), Green(G), Resilience(R), Human-centric(H)
Supports radar chart data, composite index, and comparison with baseline.

Endpoints:
- POST   /lean20/assessments                    -- create assessment
- GET    /lean20/assessments                    -- list assessments
- GET    /lean20/assessments/{id}               -- assessment detail
- PUT    /lean20/assessments/{id}/dimension-scores -- save dimension scores
- POST   /lean20/assessments/{id}/complete      -- complete and compute composite
- GET    /lean20/radar/{assessment_id}          -- radar chart data
- GET    /lean20/trends                         -- composite index trends
- GET    /lean20/benchmark                      -- industry benchmark
- GET    /lean20/latest                         -- latest assessment summary (for dashboard)
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user
from app.models.lean20 import (
    Lean20Assessment,
    Lean20ChecklistItem,
    Lean20ChecklistResponse,
    Lean20DimensionScore,
)

router = APIRouter()

# ---------------------------------------------------------------------------
# Dimension constants
# ---------------------------------------------------------------------------

LEAN20_DIMENSIONS = {
    "O": {"name": "Operational Lean", "weight": Decimal("0.30"), "max_level": 5},
    "D": {"name": "Digital Lean", "weight": Decimal("0.25"), "max_level": 5},
    "G": {"name": "Green Lean", "weight": Decimal("0.20"), "max_level": 5},
    "R": {"name": "Resilience", "weight": Decimal("0.15"), "max_level": 5},
    "H": {"name": "Human-Centric", "weight": Decimal("0.10"), "max_level": 5},
}

DIMENSION_LEVEL_DESCRIPTIONS = {
    "O": {
        1: "Initial / Ad-hoc",
        2: "Developing / Basic",
        3: "Defined / Systematic",
        4: "Managed / Proactive",
        5: "Optimizing / World-class",
    },
    "D": {
        1: "Paper-based records",
        2: "Electronic records",
        3: "Data integrated / Real-time visibility",
        4: "Intelligent analysis / AI-driven",
        5: "Autonomous optimization",
    },
    "G": {
        1: "Unaware / No environmental focus",
        2: "Compliance-driven",
        3: "Green Kaizen active",
        4: "Low-carbon operations",
        5: "Carbon competitive advantage",
    },
    "R": {
        1: "Fragile / Zero buffer",
        2: "Basic buffering",
        3: "Proactive resilience",
        4: "Digital resilience",
        5: "Adaptive resilience",
    },
    "H": {
        1: "Command-and-control",
        2: "Participatory improvement",
        3: "Empowerment-driven",
        4: "Human-AI collaboration",
        5: "Human-AI symbiosis",
    },
}

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class DimensionScoreInput(BaseModel):
    dimension_code: str = Field(..., pattern=r"^[ODGRH]$", description="O/D/G/R/H")
    level: Decimal = Field(..., ge=1, le=5, description="Score 1.0 - 5.0")
    notes: Optional[str] = None


class AssessmentCreateInput(BaseModel):
    assessment_date: date = Field(default_factory=date.today)
    weight_overrides: Optional[dict[str, float]] = Field(
        None,
        description="Override default weights, e.g. {'O': 0.25, 'D': 0.30}",
    )


class AssessmentCompleteInput(BaseModel):
    summary: Optional[str] = None
    recommendations: Optional[str] = None


class DimensionScoreOutput(BaseModel):
    dimension_code: str
    dimension_name: str
    level: Decimal
    weight: Decimal
    weighted_score: Decimal
    level_description: str
    notes: Optional[str] = None


class RadarPoint(BaseModel):
    dimension_code: str
    dimension_name: str
    level: Decimal
    max_level: Decimal = Decimal("5")
    level_description: str


class AssessmentOutput(BaseModel):
    id: int
    assessment_date: date
    status: str
    composite_index: Optional[Decimal] = None
    overall_level: Optional[str] = None
    dimensions: list[DimensionScoreOutput] = []
    summary: Optional[str] = None
    recommendations: Optional[str] = None


class TrendPoint(BaseModel):
    assessment_date: date
    composite_index: Decimal
    o: Optional[Decimal] = None
    d: Optional[Decimal] = None
    g: Optional[Decimal] = None
    r: Optional[Decimal] = None
    h: Optional[Decimal] = None


class BenchmarkData(BaseModel):
    dimension_code: str
    dimension_name: str
    industry_average: Decimal
    industry_top10: Decimal
    your_level: Optional[Decimal] = None


class LatestAssessmentSummary(BaseModel):
    """Summary for dashboard consumption."""
    has_data: bool = False
    assessment_id: Optional[int] = None
    assessment_date: Optional[date] = None
    composite_index: Optional[Decimal] = None
    overall_level: Optional[str] = None
    dimensions: list[DimensionScoreOutput] = []
    weakest_dimension: Optional[str] = None
    strongest_dimension: Optional[str] = None


# ---------------------------------------------------------------------------
# Helper: compute composite index
# ---------------------------------------------------------------------------


def compute_composite(scores: dict[str, Decimal], weights: dict[str, Decimal]) -> Decimal:
    """Weighted sum of dimension levels."""
    total = Decimal("0")
    for code, level in scores.items():
        total += level * weights.get(code, Decimal("0"))
    return total.quantize(Decimal("0.01"))


def level_label(composite: Decimal) -> str:
    if composite >= 4.3:
        return "L5 - Optimizing / World-class"
    if composite >= 3.3:
        return "L4 - Managed / Proactive"
    if composite >= 2.4:
        return "L3 - Defined / Systematic"
    if composite >= 1.6:
        return "L2 - Developing / Basic"
    return "L1 - Initial / Ad-hoc"


def _scores_from_db(dim_scores: list[Lean20DimensionScore]) -> dict[str, Decimal]:
    """Extract dimension_code -> level mapping from DB rows."""
    return {ds.dimension_code: ds.level for ds in dim_scores}


def _build_dimension_outputs(
    scores_map: dict[str, Decimal],
    notes_map: dict[str, Optional[str]] | None = None,
    weights_map: dict[str, Decimal] | None = None,
) -> list[DimensionScoreOutput]:
    """Build DimensionScoreOutput list from score map."""
    result = []
    for code, info in LEAN20_DIMENSIONS.items():
        level = scores_map.get(code)
        if level is not None:
            weight = (weights_map or {}).get(code, info["weight"])
            desc_key = int(level)
            result.append(DimensionScoreOutput(
                dimension_code=code,
                dimension_name=info["name"],
                level=level,
                weight=weight,
                weighted_score=(level * weight).quantize(Decimal("0.01")),
                level_description=DIMENSION_LEVEL_DESCRIPTIONS[code].get(desc_key, ""),
                notes=(notes_map or {}).get(code) if notes_map else None,
            ))
    return result


async def _get_assessment_or_404(
    assessment_id: int, db: AsyncSession
) -> Lean20Assessment:
    """Load assessment with dimension scores, or raise 404."""
    result = await db.execute(
        select(Lean20Assessment)
        .options(selectinload(Lean20Assessment.dimension_scores))
        .where(Lean20Assessment.id == assessment_id)
    )
    record = result.unique().scalar_one_or_none()
    if not record:
        from fastapi import HTTPException
        raise HTTPException(404, "Assessment not found")
    return record


def _to_output(record: Lean20Assessment) -> AssessmentOutput:
    """Convert DB model to API output."""
    scores_map = _scores_from_db(record.dimension_scores)
    notes_map = {ds.dimension_code: ds.notes for ds in record.dimension_scores}
    weights_map = record.weights if isinstance(record.weights, dict) else None

    return AssessmentOutput(
        id=record.id,
        assessment_date=record.assessment_date,
        status=record.status,
        composite_index=record.composite_index,
        overall_level=record.overall_level,
        dimensions=_build_dimension_outputs(scores_map, notes_map, weights_map),
        summary=record.summary,
        recommendations=record.recommendations,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("/assessments", response_model=AssessmentOutput)
async def create_assessment(
    body: AssessmentCreateInput,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    weights = {k: float(v["weight"]) for k, v in LEAN20_DIMENSIONS.items()}
    if body.weight_overrides:
        for k, v in body.weight_overrides.items():
            if k in weights:
                weights[k] = round(v, 2)

    record = Lean20Assessment(
        assessment_date=body.assessment_date,
        factory_id=user.factory_id,
        assessor_id=user.id,
        status="draft",
        weights=weights,
    )
    db.add(record)
    await db.flush()
    return _to_output(record)


@router.get("/assessments", response_model=list[AssessmentOutput])
async def list_assessments(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Lean20Assessment)
        .options(selectinload(Lean20Assessment.dimension_scores))
        .where(Lean20Assessment.factory_id == user.factory_id)
        .order_by(desc(Lean20Assessment.id))
    )
    if status:
        query = query.where(Lean20Assessment.status == status)

    result = await db.execute(query)
    items = result.unique().scalars().all()

    start = (page - 1) * page_size
    return [_to_output(a) for a in items[start : start + page_size]]


@router.get("/assessments/{assessment_id}", response_model=AssessmentOutput)
async def get_assessment(
    assessment_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    record = await _get_assessment_or_404(assessment_id, db)
    return _to_output(record)


@router.put("/assessments/{assessment_id}/dimension-scores", response_model=AssessmentOutput)
async def save_dimension_scores(
    assessment_id: int,
    body: list[DimensionScoreInput],
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    record = await _get_assessment_or_404(assessment_id, db)

    # Build a map of existing scores for upsert
    existing_map = {ds.dimension_code: ds for ds in record.dimension_scores}
    weights_map = record.weights if isinstance(record.weights, dict) else {k: float(v["weight"]) for k, v in LEAN20_DIMENSIONS.items()}

    for item in body:
        weight = Decimal(str(weights_map.get(item.dimension_code, 0.20)))
        if item.dimension_code in existing_map:
            ds = existing_map[item.dimension_code]
            ds.level = item.level
            ds.weight = weight
            ds.weighted_score = (item.level * weight).quantize(Decimal("0.01"))
            ds.notes = item.notes
        else:
            ds = Lean20DimensionScore(
                assessment_id=assessment_id,
                dimension_code=item.dimension_code,
                level=item.level,
                weight=weight,
                weighted_score=(item.level * weight).quantize(Decimal("0.01")),
                notes=item.notes,
            )
            db.add(ds)

    await db.flush()

    # Reload
    record = await _get_assessment_or_404(assessment_id, db)
    return _to_output(record)


@router.post("/assessments/{assessment_id}/complete", response_model=AssessmentOutput)
async def complete_assessment(
    assessment_id: int,
    body: AssessmentCompleteInput,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    record = await _get_assessment_or_404(assessment_id, db)

    scores_map = _scores_from_db(record.dimension_scores)
    if len(scores_map) < 5:
        from fastapi import HTTPException
        raise HTTPException(400, "All 5 dimension scores required before completing")

    weights_map = {k: Decimal(str(v)) for k, v in (record.weights or {}).items()}
    if not weights_map:
        weights_map = {k: v["weight"] for k, v in LEAN20_DIMENSIONS.items()}

    record.composite_index = compute_composite(scores_map, weights_map)
    record.overall_level = level_label(record.composite_index)
    record.status = "completed"
    record.summary = body.summary
    record.recommendations = body.recommendations

    from datetime import datetime
    record.completed_at = datetime.now()

    await db.flush()
    return _to_output(record)


@router.get("/radar/{assessment_id}", response_model=list[RadarPoint])
async def radar_data(
    assessment_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    record = await _get_assessment_or_404(assessment_id, db)
    scores_map = _scores_from_db(record.dimension_scores)

    points = []
    for code, info in LEAN20_DIMENSIONS.items():
        level = scores_map.get(code, Decimal("0"))
        desc_key = int(level) if level >= 1 else 1
        points.append(RadarPoint(
            dimension_code=code,
            dimension_name=info["name"],
            level=level if level >= 1 else Decimal("0"),
            level_description=DIMENSION_LEVEL_DESCRIPTIONS[code].get(desc_key, ""),
        ))
    return points


@router.get("/trends", response_model=list[TrendPoint])
async def trends(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Lean20Assessment)
        .options(selectinload(Lean20Assessment.dimension_scores))
        .where(
            Lean20Assessment.factory_id == user.factory_id,
            Lean20Assessment.status == "completed",
        )
        .order_by(Lean20Assessment.assessment_date)
    )
    items = result.unique().scalars().all()
    return [
        TrendPoint(
            assessment_date=a.assessment_date,
            composite_index=a.composite_index,
            o=next((ds.level for ds in a.dimension_scores if ds.dimension_code == "O"), None),
            d=next((ds.level for ds in a.dimension_scores if ds.dimension_code == "D"), None),
            g=next((ds.level for ds in a.dimension_scores if ds.dimension_code == "G"), None),
            r=next((ds.level for ds in a.dimension_scores if ds.dimension_code == "R"), None),
            h=next((ds.level for ds in a.dimension_scores if ds.dimension_code == "H"), None),
        )
        for a in items
    ]


@router.get("/benchmark", response_model=list[BenchmarkData])
async def benchmark(
    assessment_id: Optional[int] = Query(None),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Industry benchmark data (placeholder -- replace with real data source)."""
    industry_data = {
        "O": {"avg": Decimal("2.80"), "top10": Decimal("4.20")},
        "D": {"avg": Decimal("2.10"), "top10": Decimal("3.80")},
        "G": {"avg": Decimal("1.90"), "top10": Decimal("3.50")},
        "R": {"avg": Decimal("2.30"), "top10": Decimal("3.70")},
        "H": {"avg": Decimal("2.20"), "top10": Decimal("3.60")},
    }
    your_scores: dict[str, Decimal] = {}
    if assessment_id:
        record = await _get_assessment_or_404(assessment_id, db)
        your_scores = _scores_from_db(record.dimension_scores)

    result = []
    for code, info in LEAN20_DIMENSIONS.items():
        result.append(BenchmarkData(
            dimension_code=code,
            dimension_name=info["name"],
            industry_average=industry_data[code]["avg"],
            industry_top10=industry_data[code]["top10"],
            your_level=your_scores.get(code),
        ))
    return result


@router.get("/latest", response_model=LatestAssessmentSummary)
async def latest_assessment(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the latest completed assessment summary for dashboard."""
    result = await db.execute(
        select(Lean20Assessment)
        .options(selectinload(Lean20Assessment.dimension_scores))
        .where(
            Lean20Assessment.factory_id == user.factory_id,
            Lean20Assessment.status == "completed",
        )
        .order_by(desc(Lean20Assessment.assessment_date))
        .limit(1)
    )
    record = result.unique().scalar_one_or_none()

    if not record:
        return LatestAssessmentSummary(has_data=False)

    scores_map = _scores_from_db(record.dimension_scores)
    notes_map = {ds.dimension_code: ds.notes for ds in record.dimension_scores}
    weights_map = record.weights if isinstance(record.weights, dict) else None

    dim_outputs = _build_dimension_outputs(scores_map, notes_map, weights_map)

    # Find weakest and strongest
    weakest = None
    strongest = None
    min_score = Decimal("6")
    max_score = Decimal("0")
    for code, level in scores_map.items():
        if level < min_score:
            min_score = level
            weakest = code
        if level > max_score:
            max_score = level
            strongest = code

    return LatestAssessmentSummary(
        has_data=True,
        assessment_id=record.id,
        assessment_date=record.assessment_date,
        composite_index=record.composite_index,
        overall_level=record.overall_level,
        dimensions=dim_outputs,
        weakest_dimension=weakest,
        strongest_dimension=strongest,
    )


# ---------------------------------------------------------------------------
# A1: Assessment -> Project creation
# ---------------------------------------------------------------------------

# Dimension-to-project-type mapping for fast one-click creation
DIMENSION_PROJECT_TEMPLATES = {
    "O": {
        "name": "Operations Excellence - {weakest_area}",
        "project_type": "kaizen_event",
        "description": "Based on Lean 2.0 assessment, Operations dimension scored {score}. This project targets improvement in operational lean practices.",
        "objectives": "Raise Operations maturity from L{current_level} to L{target_level} within 6 months",
    },
    "D": {
        "name": "Digital Transformation - {weakest_area}",
        "project_type": "kaizen_event",
        "description": "Based on Lean 2.0 assessment, Digital Lean dimension scored {score}. This project targets digital capability building.",
        "objectives": "Raise Digital maturity from L{current_level} to L{target_level} within 6 months",
    },
    "G": {
        "name": "Green Lean Initiative - {weakest_area}",
        "project_type": "kaizen_event",
        "description": "Based on Lean 2.0 assessment, Green Lean dimension scored {score}. This project targets environmental sustainability improvement.",
        "objectives": "Raise Green maturity from L{current_level} to L{target_level} within 6 months",
    },
    "R": {
        "name": "Resilience Building - {weakest_area}",
        "project_type": "kaizen_event",
        "description": "Based on Lean 2.0 assessment, Resilience dimension scored {score}. This project targets supply chain and operational resilience.",
        "objectives": "Raise Resilience maturity from L{current_level} to L{target_level} within 6 months",
    },
    "H": {
        "name": "Human-Centric Transformation - {weakest_area}",
        "project_type": "training_program",
        "description": "Based on Lean 2.0 assessment, Human-Centric dimension scored {score}. This project targets workforce empowerment and human-AI collaboration.",
        "objectives": "Raise Human-Centric maturity from L{current_level} to L{target_level} within 6 months",
    },
}

# Level descriptions for naming
LEVEL_AREA_NAMES = {
    "O": {1: "5S & Standard Work", 2: "Kanban & Pull", 3: "TPM & Six Sigma", 4: "Lean Culture", 5: "World-class Ops"},
    "D": {1: "Paper to Digital", 2: "MES & IoT", 3: "Real-time Analytics", 4: "AI-driven Ops", 5: "Autonomous"},
    "G": {1: "Compliance Basics", 2: "Energy Management", 3: "Green Kaizen", 4: "Low-carbon Ops", 5: "Carbon Leader"},
    "R": {1: "Safety Stock", 2: "Dual-sourcing", 3: "Anomaly Response", 4: "Digital Twin", 5: "Adaptive"},
    "H": {1: "Suggestion System", 2: "Team Building", 3: "Empowerment", 4: "Human-AI Collab", 5: "Symbiosis"},
}


class ProjectFromAssessmentInput(BaseModel):
    """Create improvement projects from assessment results."""
    dimension_codes: list[str] = Field(
        ...,
        description="Dimension codes to create projects for, e.g. ['G', 'D']. Leave empty to auto-select weakest dimensions.",
    )
    priority: str = Field("high", description="Project priority")


class CreatedProjectSummary(BaseModel):
    dimension_code: str
    dimension_name: str
    project_id: int
    project_name: str
    current_level: int
    target_level: int


class AssessmentProjectsOutput(BaseModel):
    assessment_id: int
    composite_index: Decimal
    overall_level: str
    created_projects: list[CreatedProjectSummary]


@router.post("/assessments/{assessment_id}/create-projects", response_model=AssessmentProjectsOutput)
async def create_projects_from_assessment(
    assessment_id: int,
    body: ProjectFromAssessmentInput,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    A1: Create improvement projects from a completed Lean 2.0 assessment.
    
    For each selected (or auto-selected weakest) dimension, generates a project
    with appropriate template, links it back to the source assessment.
    """
    record = await _get_assessment_or_404(assessment_id, db)
    if record.status != "completed":
        from fastapi import HTTPException
        raise HTTPException(400, "Assessment must be completed before creating projects")

    scores_map = _scores_from_db(record.dimension_scores)

    # Determine which dimensions to create projects for
    target_dims = body.dimension_codes
    if not target_dims:
        # Auto-select: dimensions below industry average
        industry_avg = {"O": Decimal("2.80"), "D": Decimal("2.10"), "G": Decimal("1.90"), "R": Decimal("2.30"), "H": Decimal("2.20")}
        target_dims = [code for code, level in scores_map.items() if level < industry_avg.get(code, Decimal("3"))]
        if not target_dims:
            # If all above avg, pick the weakest
            target_dims = [min(scores_map, key=scores_map.get)]

    from app.models.project import Project
    from app.models.enums import ProjectPriority

    created = []
    for code in target_dims:
        if code not in DIMENSION_PROJECT_TEMPLATES:
            continue
        level = scores_map.get(code, Decimal("1"))
        current_level = int(level)
        target_level = min(current_level + 1, 5)
        area_name = LEVEL_AREA_NAMES.get(code, {}).get(current_level, "Improvement")

        template = DIMENSION_PROJECT_TEMPLATES[code]
        project = Project(
            name=template["name"].format(weakest_area=area_name),
            description=template["description"].format(score=float(level)),
            project_type=template["project_type"],
            owner_id=user.id,
            factory_id=user.factory_id,
            status="planning",
            priority=body.priority,
            objectives=template["objectives"].format(current_level=current_level, target_level=target_level),
            lean20_dimensions=[code],
            source_assessment_id=assessment_id,
        )
        db.add(project)
        await db.flush()

        # Add owner as project member
        from app.models.project import ProjectMember
        member = ProjectMember(project_id=project.id, user_id=user.id, role="owner")
        db.add(member)

        created.append(CreatedProjectSummary(
            dimension_code=code,
            dimension_name=LEAN20_DIMENSIONS[code]["name"],
            project_id=project.id,
            project_name=project.name,
            current_level=current_level,
            target_level=target_level,
        ))

    await db.flush()

    return AssessmentProjectsOutput(
        assessment_id=assessment_id,
        composite_index=record.composite_index or Decimal("0"),
        overall_level=record.overall_level or "",
        created_projects=created,
    )


# ---------------------------------------------------------------------------
# A3: Re-assessment from project completion
# ---------------------------------------------------------------------------

class ReassessmentSuggestion(BaseModel):
    """Suggest re-assessment based on project completion."""
    project_id: int
    project_name: str
    dimensions: list[str]
    source_assessment_id: Optional[int] = None
    source_assessment_date: Optional[date] = None
    message: str


# ---------------------------------------------------------------------------
# Better-Faster-Closer Report
# ---------------------------------------------------------------------------

PILLAR_DIM_MAP = {
    "better": {
        "O": ("品质运营", Decimal("0.35")),
        "D": ("数据驱动质量", Decimal("0.20")),
        "G": ("绿色品质", Decimal("0.20")),
        "R": ("韧性品质", Decimal("0.10")),
        "H": ("工匠精神", Decimal("0.15")),
    },
    "faster": {
        "O": ("流动效率", Decimal("0.30")),
        "D": ("实时可视", Decimal("0.25")),
        "G": ("绿色流程效率", Decimal("0.10")),
        "R": ("响应速度", Decimal("0.20")),
        "H": ("组织敏捷", Decimal("0.15")),
    },
    "closer": {
        "O": ("需求响应", Decimal("0.25")),
        "D": ("客户数字接口", Decimal("0.15")),
        "G": ("碳数据服务", Decimal("0.15")),
        "R": ("供应保障", Decimal("0.25")),
        "H": ("客户共创", Decimal("0.20")),
    },
}

PILLAR_TARGETS = {
    "better": Decimal("3.80"),
    "faster": Decimal("3.50"),
    "closer": Decimal("3.20"),
}

PILLAR_NAMES = {
    "better": "品质卓越",
    "faster": "敏捷交付",
    "closer": "客户亲密",
}


class PillarReportDimension(BaseModel):
    dimension_code: str
    dimension_name: str
    focus_area: str
    weight: Decimal
    level: Decimal
    weighted_score: Decimal
    level_description: str


class PillarReportSection(BaseModel):
    pillar_code: str
    pillar_name: str
    composite: Decimal
    target: Decimal
    gap: Decimal
    dimensions: list[PillarReportDimension]
    weakest_dimension: Optional[str] = None
    improvement_suggestion: Optional[str] = None


class BFCReport(BaseModel):
    """Better-Faster-Closer full report from assessment."""
    assessment_id: int
    assessment_date: date
    overall_composite: Decimal
    overall_level: str
    pillars: list[PillarReportSection]
    weakest_pillar: Optional[str] = None
    overall_suggestion: Optional[str] = None


IMPROVEMENT_SUGGESTIONS_REPORT = {
    "better": {
        "O": "5S+TPM专项整治，提升OEE至85%+，部署Poka-Yoke零缺陷防线",
        "D": "部署AI视觉检测系统，目标检测准确率99%+，缺陷逃逸率降低90%",
        "G": "启动碳足迹VSM，建立能耗基线，推进CBAM合规数据链",
        "R": "建立关键物料双源策略，设置安全库存水位，缩短MTTR",
        "H": "推行技能矩阵+OJT体系，目标多技能率提升至60%+",
    },
    "faster": {
        "O": "VSM识别七大浪费，Kanban拉动+SMED换模，目标Lead Time缩短30%",
        "D": "MES+IoT实时数据采集，安灯系统自动预警，数据延迟<1分钟",
        "G": "工艺能耗优化，热处理余热回收，目标能耗/单位降低15%",
        "R": "建立异常感知-预警-响应三级体系，目标恢复时间<2小时",
        "H": "推行赋权框架+敏捷站会，目标变革周期缩短40%",
    },
    "closer": {
        "O": "实施Leagile解耦点策略，延迟差异化，定制件交付周期缩短25%",
        "D": "搭建客户门户+EDI对接，在线下单率提升至80%+",
        "G": "建立产品碳标签体系，发布EPD，满足客户碳数据需求",
        "R": "建立客户分级+VMI体系，关键客户零缺供",
        "H": "启动客户Gemba+联合Kaizen，目标NPS提升至60+",
    },
}


@router.get("/report/{assessment_id}", response_model=BFCReport)
async def bfc_report(
    assessment_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a Better-Faster-Closer report from a Lean 2.0 assessment.

    Maps the 5 dimensions (O/D/G/R/H) into three value pillars
    with weighted composites and improvement suggestions.
    """
    record = await _get_assessment_or_404(assessment_id, db)
    if record.status != "completed":
        from fastapi import HTTPException
        raise HTTPException(400, "Assessment must be completed before generating report")

    scores_map = _scores_from_db(record.dimension_scores)

    pillars = []
    for pillar_code, dim_map in PILLAR_DIM_MAP.items():
        dim_sections = []
        for dim_code, (focus, weight) in dim_map.items():
            level = scores_map.get(dim_code, Decimal("0"))
            desc_key = int(level) if level >= 1 else 1
            dim_sections.append(PillarReportDimension(
                dimension_code=dim_code,
                dimension_name=LEAN20_DIMENSIONS[dim_code]["name"],
                focus_area=focus,
                weight=weight,
                level=level,
                weighted_score=(level * weight).quantize(Decimal("0.01")),
                level_description=DIMENSION_LEVEL_DESCRIPTIONS[dim_code].get(desc_key, ""),
            ))

        composite = sum(ds.weighted_score for ds in dim_sections).quantize(Decimal("0.01"))
        target = PILLAR_TARGETS[pillar_code]
        gap = (target - composite).quantize(Decimal("0.01"))

        scored = [d for d in dim_sections if d.level > 0]
        weakest = min(scored, key=lambda d: d.level).dimension_code if scored else None

        suggestion = None
        if weakest:
            suggestion = IMPROVEMENT_SUGGESTIONS_REPORT.get(pillar_code, {}).get(weakest)

        pillars.append(PillarReportSection(
            pillar_code=pillar_code,
            pillar_name=PILLAR_NAMES[pillar_code],
            composite=composite,
            target=target,
            gap=gap,
            dimensions=dim_sections,
            weakest_dimension=weakest,
            improvement_suggestion=suggestion,
        ))

    overall = sum(p.composite for p in pillars) / Decimal("3")
    overall = overall.quantize(Decimal("0.01"))

    weakest_pillar = min(pillars, key=lambda p: p.composite).pillar_code

    # Overall suggestion based on weakest pillar
    overall_suggestion_map = {
        "better": "品质卓越是最大短板。聚焦零缺陷运营和绿色品质，优先投入5S+TPM+碳足迹VSM",
        "faster": "敏捷交付是最大短板。聚焦流动效率和实时可视，优先投入VSM+Kanban+MES",
        "closer": "客户亲密是最大短板。聚焦供应保障和客户共创，优先投入客户分级+VMI+联合Kaizen",
    }

    return BFCReport(
        assessment_id=assessment_id,
        assessment_date=record.assessment_date,
        overall_composite=overall,
        overall_level=level_label(overall),
        pillars=pillars,
        weakest_pillar=weakest_pillar,
        overall_suggestion=overall_suggestion_map.get(weakest_pillar),
    )


@router.get("/reassessment-suggestions", response_model=list[ReassessmentSuggestion])
async def reassessment_suggestions(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    A3: Find completed projects with lean20 dimensions that haven't triggered a re-assessment.
    
    Returns projects completed after the last assessment, suggesting a re-evaluation
    of the dimensions those projects were targeting.
    """
    from app.models.project import Project

    # Get the latest assessment date
    latest_result = await db.execute(
        select(func.max(Lean20Assessment.assessment_date))
        .where(Lean20Assessment.factory_id == user.factory_id)
    )
    latest_assessment_date = latest_result.scalar()

    # Find completed projects with lean20 dimensions
    query = (
        select(Project)
        .where(
            Project.factory_id == user.factory_id,
            Project.status == "completed",
            Project.lean20_dimensions.isnot(None),
            Project.is_deleted == False,
        )
        .order_by(desc(Project.actual_end_date))
    )

    # If we have a latest assessment, only suggest for projects completed after it
    if latest_assessment_date:
        query = query.where(Project.actual_end_date > latest_assessment_date)

    result = await db.execute(query)
    projects = result.scalars().all()

    suggestions = []
    for p in projects:
        dims = p.lean20_dimensions if isinstance(p.lean20_dimensions, list) else []
        if not dims:
            continue

        dim_names = [LEAN20_DIMENSIONS.get(d, {}).get("name", d) for d in dims]
        msg = (
            f"Project '{p.name}' (completed {p.actual_end_date}) targeted "
            f"{', '.join(dim_names)} dimensions. "
            f"Re-assess to measure improvement impact."
        )

        suggestions.append(ReassessmentSuggestion(
            project_id=p.id,
            project_name=p.name,
            dimensions=dims,
            source_assessment_id=p.source_assessment_id,
            source_assessment_date=latest_assessment_date,
            message=msg,
        ))

    return suggestions


# ---------------------------------------------------------------------------
# Checklist endpoints (for migrated webapp assessment pages)
# ---------------------------------------------------------------------------

class ChecklistItemOutput(BaseModel):
    """清单条目输出。"""
    id: int
    dimension_code: str
    item_code: str
    item_name: str
    item_weight: float
    l1_desc: str
    l2_desc: str
    l3_desc: str
    l4_desc: str
    l5_desc: str
    sort_order: int


class ChecklistResponseInput(BaseModel):
    """清单响应输入。"""
    item_id: int
    score: int = Field(1, ge=1, le=5)
    evidence: Optional[str] = None


@router.get("/checklist", response_model=list[ChecklistItemOutput])
async def list_checklist(
    dimension: Optional[str] = Query(None, pattern="^[ODGRH]$"),
    db: AsyncSession = Depends(get_db),
):
    """获取 Lean 2.0 评估清单（可按维度过滤）。"""
    query = select(Lean20ChecklistItem).order_by(
        Lean20ChecklistItem.dimension_code,
        Lean20ChecklistItem.sort_order,
    )
    if dimension:
        query = query.where(Lean20ChecklistItem.dimension_code == dimension)
    result = await db.execute(query)
    items = result.scalars().all()
    return [
        ChecklistItemOutput(
            id=i.id,
            dimension_code=i.dimension_code,
            item_code=i.item_code,
            item_name=i.item_name,
            item_weight=float(i.item_weight),
            l1_desc=i.l1_desc,
            l2_desc=i.l2_desc,
            l3_desc=i.l3_desc,
            l4_desc=i.l4_desc,
            l5_desc=i.l5_desc,
            sort_order=i.sort_order,
        )
        for i in items
    ]


@router.post("/assessments/checklist", response_model=dict)
async def save_checklist_responses(
    assessment_id: int,
    body: list[ChecklistResponseInput],
    db: AsyncSession = Depends(get_db),
):
    """保存评估清单响应（覆盖式）。"""
    # 校验评估存在
    assessment = await db.get(Lean20Assessment, assessment_id)
    if not assessment:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Assessment not found")

    # 删除旧响应，插入新响应
    await db.execute(
        __import__("sqlalchemy").delete(Lean20ChecklistResponse).where(
            Lean20ChecklistResponse.assessment_id == assessment_id
        )
    )
    for item in body:
        db.add(Lean20ChecklistResponse(
            assessment_id=assessment_id,
            item_id=item.item_id,
            score=item.score,
            evidence=item.evidence,
        ))
    await db.commit()
    return {"ok": True, "saved": len(body)}
