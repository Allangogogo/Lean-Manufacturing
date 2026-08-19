"""
Automation Maturity & ROI API

Endpoints:
- GET    /automation/checklist-template     -- Default checklist items
- POST   /automation/assessments            -- Create assessment
- GET    /automation/assessments             -- List assessments
- GET    /automation/assessments/{id}       -- Assessment detail
- PUT    /automation/assessments/{id}       -- Update assessment scores
- POST   /automation/assessments/{id}/complete -- Complete & compute composite
- GET    /automation/radar/{id}             -- Radar chart data
- GET    /automation/trends                 -- Score trends
- GET    /automation/latest                 -- Latest assessment summary
- POST   /automation/projects               -- Create automation project
- GET    /automation/projects               -- List projects
- GET    /automation/projects/{id}          -- Project detail
- PUT    /automation/projects/{id}         -- Update project
- POST   /automation/projects/{id}/review   -- Add PDCA review
- GET    /automation/projects/{id}/reviews  -- List reviews
- GET    /automation/roi-summary            -- ROI summary across all projects
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user

router = APIRouter(tags=["automation"])

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DIMENSIONS = {
    "quality":       {"name": "AI视觉质检",         "max": 5, "weight": Decimal("0.30")},
    "tooling":       {"name": "快速换模自动化",     "max": 5, "weight": Decimal("0.25")},
    "feeding":       {"name": "自动上料系统",       "max": 5, "weight": Decimal("0.20")},
    "heat_treatment":{"name": "热处理AI优化",       "max": 5, "weight": Decimal("0.15")},
    "logistics":     {"name": "AGV物料搬运",        "max": 5, "weight": Decimal("0.10")},
}

CHECKLIST_TEMPLATE = [
    # Quality (quality × 5)
    {"dimension": "quality", "sort_order": 1,  "item_text": "是否有AI视觉检测系统上线？" },
    {"dimension": "quality", "sort_order": 2,  "item_text": "视觉检测是否覆盖主要缺陷类型（表面裂纹/毛刺/尺寸偏差）？" },
    {"dimension": "quality", "sort_order": 3,  "item_text": "视觉检测漏检率是否<1%？" },
    {"dimension": "quality", "sort_order": 4,  "item_text": "视觉检测数据是否对接MES？" },
    {"dimension": "quality", "sort_order": 5,  "item_text": "误报率是否<5%？" },
    # Tooling (tooling × 5)
    {"dimension": "tooling", "sort_order": 6,  "item_text": "是否有换模参数数据库？" },
    {"dimension": "tooling", "sort_order": 7,  "item_text": "是否有触摸屏调机界面？" },
    {"dimension": "tooling", "sort_order": 8,  "item_text": "平均换模时间是否<20分钟？" },
    {"dimension": "tooling", "sort_order": 9,  "item_text": "是否有模具全生命周期管理？" },
    {"dimension": "tooling", "sort_order": 10, "item_text": "换模参数是否有版本记录和追溯？" },
    # Feeding (feeding × 5)
    {"dimension": "feeding", "sort_order": 11, "item_text": "机加工设备是否配备断料检测？" },
    {"dimension": "feeding", "sort_order": 12, "item_text": "精加工设备是否配备断丝检测？" },
    {"dimension": "feeding", "sort_order": 13, "item_text": "断料检测响应时间是否<500ms？" },
    {"dimension": "feeding", "sort_order": 14, "item_text": "是否有自动上料系统替代人工上料？" },
    {"dimension": "feeding", "sort_order": 15, "item_text": "自动上料可靠性是否>95%？" },
    # Heat treatment (heat_treatment × 5)
    {"dimension": "heat_treatment", "sort_order": 16, "item_text": "热处理是否有温度自动记录？" },
    {"dimension": "heat_treatment", "sort_order": 17, "item_text": "是否有AI温控优化系统？" },
    {"dimension": "heat_treatment", "sort_order": 18, "item_text": "碳势控制精度是否<±0.1%C？" },
    {"dimension": "heat_treatment", "sort_order": 19, "item_text": "是否有能耗实时监控？" },
    {"dimension": "heat_treatment", "sort_order": 20, "item_text": "是否与MES打通工艺下达？" },
    # Logistics (logistics × 5)
    {"dimension": "logistics", "sort_order": 21, "item_text": "是否部署AGV/AMR？" },
    {"dimension": "logistics", "sort_order": 22, "item_text": "AGV路径是否经过验证可行？" },
    {"dimension": "logistics", "sort_order": 23, "item_text": "是否有人货分流措施？" },
    {"dimension": "logistics", "sort_order": 24, "item_text": "AGV是否与MES/ERP系统对接？" },
    {"dimension": "logistics", "sort_order": 25, "item_text": "是否有备用电池/换电桩配置？" },
]

DIMENSION_LEVEL_DESCRIPTIONS = {
    "quality":        {1:"无视觉检测", 2:"人工抽检+Excel", 3:"AI试点", 4:"AI全检对接MES", 5:"AI+预测+自适应"},
    "tooling":        {1:"纸质参数", 2:"电子参数表", 3:"触摸屏界面", 4:"参数库+RFID", 5:"AI辅助调参+一键换模"},
    "feeding":        {1:"人工上料", 2:"半自动上料", 3:"自动上料无检测", 4:"上料+断料检测", 5:"智能上料+自动调整"},
    "heat_treatment": {1:"人工抄表", 2:"自动记录报警", 3:"PLC控制", 4:"AI优化试点", 5:"AI全控+自适应"},
    "logistics":      {1:"叉车+人工", 2:"部分区域AGV", 3:"AGV部署但未对接MES", 4:"AGV全厂+MES对接", 5:"AMR+智能调度"},
}

# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class ChecklistItemCreate(BaseModel):
    item_text: str
    dimension: str
    sort_order: int = 0

class ChecklistItemResponse(BaseModel):
    id: int
    dimension: str
    item_text: str
    sort_order: int
    is_checked: bool
    evidence: str | None

    class Config:
        from_attributes = True

class AssessmentScoreUpdate(BaseModel):
    quality_score: Optional[float] = None
    tooling_score: Optional[float] = None
    feeding_score: Optional[float] = None
    heat_treatment_score: Optional[float] = None
    logistics_score: Optional[float] = None
    notes: Optional[str] = None

class AssessmentCreate(BaseModel):
    factory_id: Optional[int] = None
    assessor_name: Optional[str] = None

class AssessmentResponse(BaseModel):
    id: int
    factory_id: Optional[int]
    assessor_name: Optional[str]
    quality_score: float
    tooling_score: float
    feeding_score: float
    heat_treatment_score: float
    logistics_score: float
    composite_score: Optional[float]
    maturity_level: Optional[int]
    is_completed: bool
    created_at: str
    completed_at: Optional[str]
    items: list[ChecklistItemResponse]

    class Config:
        from_attributes = True

class RadarPoint(BaseModel):
    dimension: str
    name: str
    score: float
    max: float
    level_desc: str

class RadarResponse(BaseModel):
    assessment_id: int
    composite_score: float
    maturity_level: int
    points: list[RadarPoint]
    created_at: str

class ProjectCreate(BaseModel):
    assessment_id: Optional[int] = None
    project_name: str
    category: str
    priority: str = "P1"
    investment_amount: float
    investment_breakdown: Optional[str] = None
    expected_annual_benefit: float
    expected_roi: Optional[float] = None
    expected_payback_months: Optional[float] = None
    start_date: Optional[str] = None
    target_date: Optional[str] = None
    owner: Optional[str] = None
    notes: Optional[str] = None

class ProjectUpdate(BaseModel):
    pdca_phase: Optional[str] = None
    status: Optional[str] = None
    actual_annual_benefit: Optional[float] = None
    actual_roi: Optional[float] = None
    actual_payback_months: Optional[float] = None
    completed_date: Optional[str] = None
    notes: Optional[str] = None

class ReviewCreate(BaseModel):
    pdca_phase: str
    cycle_number: int = 1
    reviewer: Optional[str] = None
    plan_goals: Optional[str] = None
    plan_actions: Optional[str] = None
    do_progress: Optional[str] = None
    do_issues: Optional[str] = None
    check_results: Optional[str] = None
    check_roi_actual: Optional[float] = None
    act_decision: Optional[str] = None
    act_next_steps: Optional[str] = None
    review_date: Optional[str] = None

class ROISummary(BaseModel):
    total_investment: float
    total_expected_benefit: float
    avg_expected_roi: float
    projects_by_status: dict
    projects_by_priority: dict
    top_roi_projects: list

# ---------------------------------------------------------------------------
# Lazy import to avoid circular dependency
# ---------------------------------------------------------------------------

def _get_model(name: str):
    from app.models.automation import AutomationMaturity, AutomationChecklistItem, AutomationProject, AutomationReview
    return {"AutomationMaturity": AutomationMaturity,
            "AutomationChecklistItem": AutomationChecklistItem,
            "AutomationProject": AutomationProject,
            "AutomationReview": AutomationReview}[name]

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/checklist-template", response_model=list[dict])
async def get_checklist_template():
    """Return the default 25-item automation maturity checklist."""
    return CHECKLIST_TEMPLATE

@router.post("/assessments", response_model=dict)
async def create_assessment(body: AssessmentCreate, db: AsyncSession = Depends(get_db)):
    from app.models.automation import AutomationMaturity, AutomationChecklistItem
    model_m = _get_model("AutomationMaturity")
    model_i = _get_model("AutomationChecklistItem")

    assessment = model_m(
        factory_id=body.factory_id,
        assessor_name=body.assessor_name or "anonymous",
        quality_score=Decimal("0"), tooling_score=Decimal("0"),
        feeding_score=Decimal("0"), heat_treatment_score=Decimal("0"),
        logistics_score=Decimal("0"), is_completed=False,
    )
    db.add(assessment)
    await db.flush()

    for item in CHECKLIST_TEMPLATE:
        db.add(model_i(
            assessment_id=assessment.id,
            dimension=item["dimension"],
            item_text=item["item_text"],
            sort_order=item["sort_order"],
            is_checked=False,
        ))
    await db.commit()
    await db.refresh(assessment)
    return {"id": assessment.id, "message": "Assessment created with 25 checklist items"}

@router.get("/assessments", response_model=list[dict])
async def list_assessments(
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
):
    from app.models.automation import AutomationMaturity
    model = _get_model("AutomationMaturity")
    result = await db.execute(
        select(model).order_by(desc(model.id)).limit(limit)
    )
    rows = result.scalars().all()
    return [
        {"id": r.id, "composite_score": float(r.composite_score) if r.composite_score else None,
         "maturity_level": r.maturity_level, "is_completed": r.is_completed,
         "assessor_name": r.assessor_name, "created_at": str(r.created_at)}
        for r in rows
    ]

@router.get("/assessments/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(assessment_id: int, db: AsyncSession = Depends(get_db)):
    from app.models.automation import AutomationMaturity, AutomationChecklistItem
    model_m = _get_model("AutomationMaturity")
    model_i = _get_model("AutomationChecklistItem")
    result = await db.execute(
        select(model_m).where(model_m.id == assessment_id).options(selectinload(model_m.items))
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return AssessmentResponse(
        id=assessment.id,
        factory_id=assessment.factory_id,
        assessor_name=assessment.assessor_name,
        quality_score=float(assessment.quality_score),
        tooling_score=float(assessment.tooling_score),
        feeding_score=float(assessment.feeding_score),
        heat_treatment_score=float(assessment.heat_treatment_score),
        logistics_score=float(assessment.logistics_score),
        composite_score=float(assessment.composite_score) if assessment.composite_score else None,
        maturity_level=assessment.maturity_level,
        is_completed=assessment.is_completed,
        created_at=str(assessment.created_at),
        completed_at=str(assessment.completed_at) if assessment.completed_at else None,
        items=[
            ChecklistItemResponse(id=i.id, dimension=i.dimension, item_text=i.item_text,
                                  sort_order=i.sort_order, is_checked=i.is_checked, evidence=i.evidence)
            for i in sorted(assessment.items, key=lambda x: x.sort_order)
        ],
    )

@router.put("/assessments/{assessment_id}")
async def update_assessment_scores(
    assessment_id: int, body: AssessmentScoreUpdate, db: AsyncSession = Depends(get_db)
):
    from app.models.automation import AutomationMaturity
    model = _get_model("AutomationMaturity")
    result = await db.execute(select(model).where(model.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if body.quality_score is not None:
        assessment.quality_score = Decimal(str(body.quality_score))
    if body.tooling_score is not None:
        assessment.tooling_score = Decimal(str(body.tooling_score))
    if body.feeding_score is not None:
        assessment.feeding_score = Decimal(str(body.feeding_score))
    if body.heat_treatment_score is not None:
        assessment.heat_treatment_score = Decimal(str(body.heat_treatment_score))
    if body.logistics_score is not None:
        assessment.logistics_score = Decimal(str(body.logistics_score))
    if body.notes is not None:
        assessment.notes = body.notes

    await db.commit()
    return {"message": "Scores updated"}

@router.post("/assessments/{assessment_id}/complete")
async def complete_assessment(assessment_id: int, db: AsyncSession = Depends(get_db)):
    from app.models.automation import AutomationMaturity
    model = _get_model("AutomationMaturity")
    result = await db.execute(select(model).where(model.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    total = Decimal("0")
    for dim, info in DIMENSIONS.items():
        score = getattr(assessment, f"{dim}_score", Decimal("0"))
        total += score * info["weight"]

    assessment.composite_score = total
    assessment.is_completed = True
    assessment.completed_at = datetime.utcnow()

    level = int(total)
    assessment.maturity_level = max(1, min(5, level))

    await db.commit()
    return {
        "id": assessment.id,
        "composite_score": float(total),
        "maturity_level": assessment.maturity_level,
        "level_desc": DIMENSION_LEVEL_DESCRIPTIONS.get("quality", {}).get(assessment.maturity_level, ""),
    }

@router.get("/radar/{assessment_id}", response_model=RadarResponse)
async def get_radar(assessment_id: int, db: AsyncSession = Depends(get_db)):
    from app.models.automation import AutomationMaturity
    model = _get_model("AutomationMaturity")
    result = await db.execute(select(model).where(model.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    points = []
    for dim, info in DIMENSIONS.items():
        score = float(getattr(assessment, f"{dim}_score", 0))
        level_key = max(1, min(5, int(score)))
        points.append(RadarPoint(
            dimension=dim,
            name=info["name"],
            score=score,
            max=info["max"],
            level_desc=DIMENSION_LEVEL_DESCRIPTIONS.get(dim, {}).get(level_key, ""),
        ))

    return RadarResponse(
        assessment_id=assessment.id,
        composite_score=float(assessment.composite_score) if assessment.composite_score else 0,
        maturity_level=assessment.maturity_level or 0,
        points=points,
        created_at=str(assessment.created_at),
    )

@router.get("/trends", response_model=list[dict])
async def get_trends(limit: int = Query(20, le=100), db: AsyncSession = Depends(get_db)):
    from app.models.automation import AutomationMaturity
    model = _get_model("AutomationMaturity")
    result = await db.execute(
        select(model)
        .where(model.is_completed == True)
        .order_by(desc(model.completed_at))
        .limit(limit)
    )
    rows = result.scalars().all()
    return [
        {"id": r.id, "composite_score": float(r.composite_score),
         "quality": float(r.quality_score), "tooling": float(r.tooling_score),
         "feeding": float(r.feeding_score), "heat_treatment": float(r.heat_treatment_score),
         "logistics": float(r.logistics_score),
         "maturity_level": r.maturity_level, "assessed_at": str(r.completed_at)}
        for r in rows
    ]

@router.get("/latest", response_model=dict)
async def get_latest(db: AsyncSession = Depends(get_db)):
    from app.models.automation import AutomationMaturity
    model = _get_model("AutomationMaturity")
    result = await db.execute(
        select(model).where(model.is_completed == True).order_by(desc(model.id)).limit(1)
    )
    row = result.scalar_one_or_none()
    if not row:
        return {"message": "No completed assessment found"}
    return {
        "id": row.id, "composite_score": float(row.composite_score),
        "maturity_level": row.maturity_level,
        "assessor_name": row.assessor_name, "assessed_at": str(row.completed_at),
    }

# ---- Projects ----

@router.post("/projects", response_model=dict)
async def create_project(body: ProjectCreate, db: AsyncSession = Depends(get_db)):
    from app.models.automation import AutomationProject
    model = _get_model("AutomationProject")
    expected_roi = body.expected_roi or (body.expected_annual_benefit / body.investment_amount * 100 if body.investment_amount else 0)
    payback = body.expected_payback_months or (body.investment_amount / body.expected_annual_benefit * 12 if body.expected_annual_benefit else 0)

    project = model(
        assessment_id=body.assessment_id,
        project_name=body.project_name,
        category=body.category,
        priority=body.priority,
        investment_amount=Decimal(str(body.investment_amount)),
        investment_breakdown=body.investment_breakdown,
        expected_annual_benefit=Decimal(str(body.expected_annual_benefit)),
        expected_roi=Decimal(str(expected_roi)),
        expected_payback_months=Decimal(str(payback)),
        start_date=body.start_date,
        target_date=body.target_date,
        owner=body.owner,
        notes=body.notes,
        status="planned",
        pdca_phase="plan",
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return {"id": project.id, "message": "Project created"}

@router.get("/projects", response_model=list[dict])
async def list_projects(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    from app.models.automation import AutomationProject
    model = _get_model("AutomationProject")
    query = select(model)
    if status:
        query = query.where(model.status == status)
    if priority:
        query = query.where(model.priority == priority)
    result = await db.execute(query.order_by(desc(model.id)).limit(limit))
    rows = result.scalars().all()
    return [
        {"id": r.id, "project_name": r.project_name, "category": r.category,
         "priority": r.priority, "status": r.status,
         "investment": float(r.investment_amount),
         "expected_benefit": float(r.expected_annual_benefit),
         "expected_roi": float(r.expected_roi) if r.expected_roi else None,
         "actual_roi": float(r.actual_roi) if r.actual_roi else None,
         "payback_months": float(r.expected_payback_months) if r.expected_payback_months else None,
         "pdca_phase": r.pdca_phase, "owner": r.owner,
         "created_at": str(r.created_at)}
        for r in rows
    ]

@router.get("/projects/{project_id}", response_model=dict)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    from app.models.automation import AutomationProject
    model = _get_model("AutomationProject")
    result = await db.execute(select(model).where(model.id == project_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "id": r.id, "project_name": r.project_name, "category": r.category,
        "priority": r.priority, "status": r.status,
        "investment": float(r.investment_amount),
        "investment_breakdown": r.investment_breakdown,
        "expected_benefit": float(r.expected_annual_benefit),
        "expected_roi": float(r.expected_roi) if r.expected_roi else None,
        "actual_benefit": float(r.actual_annual_benefit) if r.actual_annual_benefit else None,
        "actual_roi": float(r.actual_roi) if r.actual_roi else None,
        "payback_months": float(r.expected_payback_months) if r.expected_payback_months else None,
        "actual_payback": float(r.actual_payback_months) if r.actual_payback_months else None,
        "pdca_phase": r.pdca_phase, "pdca_cycle": r.pdca_cycle,
        "owner": r.owner, "notes": r.notes,
        "start_date": r.start_date, "target_date": r.target_date,
        "completed_date": r.completed_date,
        "created_at": str(r.created_at),
    }

@router.put("/projects/{project_id}")
async def update_project(project_id: int, body: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    from app.models.automation import AutomationProject
    model = _get_model("AutomationProject")
    result = await db.execute(select(model).where(model.id == project_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    if body.pdca_phase: p.pdca_phase = body.pdca_phase
    if body.status: p.status = body.status
    if body.actual_annual_benefit is not None:
        p.actual_annual_benefit = Decimal(str(body.actual_annual_benefit))
    if body.actual_roi is not None:
        p.actual_roi = Decimal(str(body.actual_roi))
    if body.actual_payback_months is not None:
        p.actual_payback_months = Decimal(str(body.actual_payback_months))
    if body.completed_date:
        p.completed_date = body.completed_date
    if body.notes is not None:
        p.notes = body.notes

    await db.commit()
    return {"message": "Project updated"}

@router.post("/projects/{project_id}/review", response_model=dict)
async def add_review(project_id: int, body: ReviewCreate, db: AsyncSession = Depends(get_db)):
    from app.models.automation import AutomationProject, AutomationReview
    model_p = _get_model("AutomationProject")
    model_r = _get_model("AutomationReview")
    result = await db.execute(select(model_p).where(model_p.id == project_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    review = model_r(
        project_id=project_id,
        pdca_phase=body.pdca_phase,
        cycle_number=body.cycle_number,
        reviewer=body.reviewer,
        plan_goals=body.plan_goals,
        plan_actions=body.plan_actions,
        do_progress=body.do_progress,
        do_issues=body.do_issues,
        check_results=body.check_results,
        check_roi_actual=Decimal(str(body.check_roi_actual)) if body.check_roi_actual else None,
        act_decision=body.act_decision,
        act_next_steps=body.act_next_steps,
        review_date=body.review_date,
    )
    db.add(review)
    await db.flush()

    # Update project's PDCA cycle
    p.pdca_cycle = max(p.pdca_cycle, body.cycle_number)
    if body.act_decision in ["standardize", "推广"]:
        p.pdca_phase = "act"
    elif body.act_decision in ["adjust", "调整"]:
        p.pdca_phase = "plan"
        p.pdca_cycle += 1

    await db.commit()
    return {"id": review.id, "message": "Review recorded"}

@router.get("/projects/{project_id}/reviews", response_model=list[dict])
async def list_reviews(project_id: int, db: AsyncSession = Depends(get_db)):
    from app.models.automation import AutomationReview
    model = _get_model("AutomationReview")
    result = await db.execute(
        select(model).where(model.project_id == project_id).order_by(desc(model.id))
    )
    rows = result.scalars().all()
    return [
        {"id": r.id, "pdca_phase": r.pdca_phase, "cycle_number": r.cycle_number,
         "reviewer": r.reviewer, "check_results": r.check_results,
         "act_decision": r.act_decision, "check_roi_actual": float(r.check_roi_actual) if r.check_roi_actual else None,
         "review_date": r.review_date, "created_at": str(r.created_at)}
        for r in rows
    ]

@router.get("/roi-summary", response_model=ROISummary)
async def get_roi_summary(db: AsyncSession = Depends(get_db)):
    from app.models.automation import AutomationProject
    model = _get_model("AutomationProject")
    result = await db.execute(select(model))
    rows = result.scalars().all()

    total_inv = sum(float(r.investment_amount) for r in rows)
    total_exp = sum(float(r.expected_annual_benefit) for r in rows)
    avg_roi = (total_exp / total_inv * 100) if total_inv else 0

    by_status, by_priority = {}, {}
    for r in rows:
        by_status[r.status] = by_status.get(r.status, 0) + 1
        by_priority[r.priority] = by_priority.get(r.priority, 0) + 1

    top_projects = sorted(rows, key=lambda x: float(x.expected_roi) if x.expected_roi else 0, reverse=True)[:5]
    top_roi_list = [
        {"id": r.id, "name": r.project_name, "roi": float(r.expected_roi),
         "payback": float(r.expected_payback_months) if r.expected_payback_months else None}
        for r in top_projects
    ]

    return ROISummary(
        total_investment=round(total_inv, 2),
        total_expected_benefit=round(total_exp, 2),
        avg_expected_roi=round(avg_roi, 1),
        projects_by_status=by_status,
        projects_by_priority=by_priority,
        top_roi_projects=top_roi_list,
    )
