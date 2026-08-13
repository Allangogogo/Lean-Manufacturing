"""
Value Pillars API - Better / Faster / Closer

Provides pillar overview, detail, KPI tracking, and the
unified three-pillar dashboard for the LeanOps frontend.

Endpoints:
- GET  /pillars                    -- Three-pillar overview
- GET  /pillars/{code}             -- Pillar detail with dimension mapping
- GET  /pillars/{code}/kpis        -- KPI snapshots for a pillar
- POST /pillars/{code}/kpi-snapshot -- Record a KPI data point
- GET  /pillars/dashboard          -- Unified dashboard data
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user
from app.models.lean20 import Lean20Assessment, Lean20DimensionScore

router = APIRouter()


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PILLAR_INFO = {
    "better": {
        "name": "品质卓越",
        "name_en": "Better",
        "icon": "diamond",
        "color": "#2563eb",
        "vision": "持续追求零缺陷和世界级运营卓越",
        "target": Decimal("3.80"),
    },
    "faster": {
        "name": "敏捷交付",
        "name_en": "Faster",
        "icon": "bolt",
        "color": "#059669",
        "vision": "以最短路径将价值传递到客户手中",
        "target": Decimal("3.50"),
    },
    "closer": {
        "name": "客户亲密",
        "name_en": "Closer",
        "icon": "handshake",
        "color": "#d97706",
        "vision": "与客户深度连接，从供应商升级为价值伙伴",
        "target": Decimal("3.20"),
    },
}

# Dimension code -> display name
DIM_NAMES = {
    "O": "Operational Lean",
    "D": "Digital Lean",
    "G": "Green Lean",
    "R": "Resilience",
    "H": "Human-Centric",
}

# pillar -> { dimension_code: (focus_area, weight) }
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


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class DimensionInPillar(BaseModel):
    dimension_code: str
    dimension_name: str
    focus_area: str
    weight: Decimal
    current_level: Optional[Decimal] = None
    weighted_score: Optional[Decimal] = None


class PillarOverview(BaseModel):
    code: str
    name: str
    name_en: str
    icon: str
    color: str
    vision: str
    target_composite: Decimal
    current_composite: Optional[Decimal] = None
    dimensions: list[DimensionInPillar] = []
    weakest_dimension: Optional[str] = None
    strongest_dimension: Optional[str] = None


class KpiSnapshotInput(BaseModel):
    dimension_code: Optional[str] = None
    kpi_name: str
    kpi_value: Decimal
    target_value: Optional[Decimal] = None
    unit: str = ""
    snapshot_date: date = Field(default_factory=date.today)
    source: str = "manual"


class KpiSnapshotOutput(BaseModel):
    id: int
    pillar_code: str
    dimension_code: Optional[str] = None
    kpi_name: str
    kpi_value: Decimal
    target_value: Optional[Decimal] = None
    unit: str
    snapshot_date: date
    source: str


class DashboardPillar(BaseModel):
    code: str
    name: str
    name_en: str
    icon: str
    color: str
    current_composite: Optional[Decimal] = None
    target_composite: Decimal
    dimensions: list[DimensionInPillar] = []
    weakest_dimension: Optional[str] = None
    improvement_suggestion: Optional[str] = None


class DashboardOutput(BaseModel):
    vision_statement: str = "Better, Faster and Closer to Customer"
    overall_composite: Optional[Decimal] = None
    overall_level: Optional[str] = None
    pillars: list[DashboardPillar] = []
    latest_assessment_date: Optional[date] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _level_label(composite: Decimal) -> str:
    if composite >= 4.3:
        return "L5 - Optimizing"
    if composite >= 3.3:
        return "L4 - Managed"
    if composite >= 2.4:
        return "L3 - Defined"
    if composite >= 1.6:
        return "L2 - Developing"
    return "L1 - Initial"


def _compute_pillar_composite(
    pillar_code: str,
    dim_scores: dict[str, Decimal],
) -> Decimal:
    """Compute weighted composite for a pillar from dimension scores."""
    mapping = PILLAR_DIM_MAP.get(pillar_code, {})
    total = Decimal("0")
    for dim_code, (focus, weight) in mapping.items():
        level = dim_scores.get(dim_code, Decimal("0"))
        total += level * weight
    return total.quantize(Decimal("0.01"))


async def _get_latest_dim_scores(
    factory_id: int, db: AsyncSession
) -> tuple[dict[str, Decimal], Optional[date]]:
    """Get dimension scores from the latest completed Lean 2.0 assessment."""
    result = await db.execute(
        select(Lean20Assessment)
        .options(selectinload(Lean20Assessment.dimension_scores))
        .where(
            Lean20Assessment.factory_id == factory_id,
            Lean20Assessment.status == "completed",
        )
        .order_by(desc(Lean20Assessment.assessment_date))
        .limit(1)
    )
    record = result.unique().scalar_one_or_none()
    if not record:
        return {}, None
    scores = {ds.dimension_code: ds.level for ds in record.dimension_scores}
    return scores, record.assessment_date


def _build_pillar_dims(
    pillar_code: str,
    dim_scores: dict[str, Decimal],
) -> list[DimensionInPillar]:
    mapping = PILLAR_DIM_MAP.get(pillar_code, {})
    dims = []
    for dim_code, (focus, weight) in mapping.items():
        level = dim_scores.get(dim_code)
        dims.append(DimensionInPillar(
            dimension_code=dim_code,
            dimension_name=DIM_NAMES.get(dim_code, dim_code),
            focus_area=focus,
            weight=weight,
            current_level=level,
            weighted_score=(level * weight).quantize(Decimal("0.01")) if level else None,
        ))
    return dims


def _find_weakest(dims: list[DimensionInPillar]) -> Optional[str]:
    scored = [d for d in dims if d.current_level is not None]
    if not scored:
        return None
    return min(scored, key=lambda d: d.current_level).dimension_code


# ---------------------------------------------------------------------------
# Improvement suggestions based on weakest dimension
# ---------------------------------------------------------------------------

IMPROVEMENT_SUGGESTIONS = {
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


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("", response_model=list[PillarOverview])
async def list_pillars(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Three-pillar overview with current scores."""
    dim_scores, _ = await _get_latest_dim_scores(user.factory_id, db)

    result = []
    for code, info in PILLAR_INFO.items():
        dims = _build_pillar_dims(code, dim_scores)
        composite = _compute_pillar_composite(code, dim_scores) if dim_scores else None

        result.append(PillarOverview(
            code=code,
            name=info["name"],
            name_en=info["name_en"],
            icon=info["icon"],
            color=info["color"],
            vision=info["vision"],
            target_composite=info["target"],
            current_composite=composite,
            dimensions=dims,
            weakest_dimension=_find_weakest(dims),
            strongest_dimension=max(
                [d for d in dims if d.current_level is not None],
                key=lambda d: d.current_level,
            ).dimension_code if any(d.current_level for d in dims) else None,
        ))

    return result


@router.get("/dashboard", response_model=DashboardOutput)
async def pillar_dashboard(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unified Better-Faster-Closer dashboard."""
    dim_scores, latest_date = await _get_latest_dim_scores(user.factory_id, db)

    pillars = []
    for code, info in PILLAR_INFO.items():
        dims = _build_pillar_dims(code, dim_scores)
        composite = _compute_pillar_composite(code, dim_scores) if dim_scores else None
        weakest = _find_weakest(dims)

        suggestion = None
        if weakest:
            suggestion = IMPROVEMENT_SUGGESTIONS.get(code, {}).get(weakest)

        pillars.append(DashboardPillar(
            code=code,
            name=info["name"],
            name_en=info["name_en"],
            icon=info["icon"],
            color=info["color"],
            current_composite=composite,
            target_composite=info["target"],
            dimensions=dims,
            weakest_dimension=weakest,
            improvement_suggestion=suggestion,
        ))

    overall = None
    level = None
    if dim_scores:
        overall = sum(
            _compute_pillar_composite(code, dim_scores) for code in PILLAR_INFO
        ) / Decimal("3")
        overall = overall.quantize(Decimal("0.01"))
        level = _level_label(overall)

    return DashboardOutput(
        overall_composite=overall,
        overall_level=level,
        pillars=pillars,
        latest_assessment_date=latest_date,
    )


@router.get("/{code}", response_model=PillarOverview)
async def get_pillar(
    code: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pillar detail with dimension mapping and current scores."""
    if code not in PILLAR_INFO:
        raise HTTPException(404, f"Pillar '{code}' not found. Use: better/faster/closer")

    info = PILLAR_INFO[code]
    dim_scores, _ = await _get_latest_dim_scores(user.factory_id, db)
    dims = _build_pillar_dims(code, dim_scores)
    composite = _compute_pillar_composite(code, dim_scores) if dim_scores else None

    return PillarOverview(
        code=code,
        name=info["name"],
        name_en=info["name_en"],
        icon=info["icon"],
        color=info["color"],
        vision=info["vision"],
        target_composite=info["target"],
        current_composite=composite,
        dimensions=dims,
        weakest_dimension=_find_weakest(dims),
        strongest_dimension=max(
            [d for d in dims if d.current_level is not None],
            key=lambda d: d.current_level,
        ).dimension_code if any(d.current_level for d in dims) else None,
    )


@router.get("/{code}/kpis", response_model=list[KpiSnapshotOutput])
async def get_pillar_kpis(
    code: str,
    limit: int = Query(30, ge=1, le=200),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get KPI snapshots for a pillar."""
    if code not in PILLAR_INFO:
        raise HTTPException(404, f"Pillar '{code}' not found")

    from sqlalchemy import text
    result = await db.execute(
        text("""
            SELECT id, pillar_code, dimension_code, kpi_name,
                   kpi_value, target_value, unit, snapshot_date, source
            FROM pillar_kpi_snapshots
            WHERE pillar_code = :code
            ORDER BY snapshot_date DESC, id DESC
            LIMIT :limit
        """),
        {"code": code, "limit": limit},
    )
    rows = result.fetchall()
    return [KpiSnapshotOutput(
        id=r[0], pillar_code=r[1], dimension_code=r[2], kpi_name=r[3],
        kpi_value=r[4], target_value=r[5], unit=r[6],
        snapshot_date=r[7], source=r[8],
    ) for r in rows]


@router.post("/{code}/kpi-snapshot", response_model=KpiSnapshotOutput)
async def create_kpi_snapshot(
    code: str,
    body: KpiSnapshotInput,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a KPI data point for a pillar."""
    if code not in PILLAR_INFO:
        raise HTTPException(404, f"Pillar '{code}' not found")

    from sqlalchemy import text
    result = await db.execute(
        text("""
            INSERT INTO pillar_kpi_snapshots
            (pillar_code, dimension_code, kpi_name, kpi_value, target_value,
             unit, snapshot_date, source)
            VALUES (:pc, :dc, :kn, :kv, :tv, :u, :sd, :src)
        """),
        {
            "pc": code,
            "dc": body.dimension_code,
            "kn": body.kpi_name,
            "kv": float(body.kpi_value),
            "tv": float(body.target_value) if body.target_value else None,
            "u": body.unit,
            "sd": body.snapshot_date.isoformat(),
            "src": body.source,
        },
    )
    await db.flush()

    snap_id = result.lastrowid
    return KpiSnapshotOutput(
        id=snap_id,
        pillar_code=code,
        dimension_code=body.dimension_code,
        kpi_name=body.kpi_name,
        kpi_value=body.kpi_value,
        target_value=body.target_value,
        unit=body.unit,
        snapshot_date=body.snapshot_date,
        source=body.source,
    )
