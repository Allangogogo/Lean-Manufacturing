"""
成熟度评估业务逻辑层

职责：
1. 评估计划 CRUD
2. 维度/细项评分
3. 评估完成与报告生成
4. 历史趋势
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError, NotFoundError
from app.core.pagination import PaginatedResponse, paginate
from app.models.maturity import (
    MaturityAssessment,
    MaturityCriterion,
    MaturityDimension,
)
from app.models.user import User
from app.schemas.maturity import (
    AssessmentCompleteRequest,
    AssessmentCreateRequest,
    AssessmentDetailResponse,
    AssessmentListItem,
    MaturityStatsResponse,
    CriterionResponse,
    DimensionResponse,
    DimensionScoreRequest,
    TrendResponse,
)

# 默认维度模板
DEFAULT_DIMENSIONS = [
    {
        "name": "领导力与战略",
        "weight": Decimal("0.25"),
        "max_score": Decimal("25"),
        "criteria": [
            {"name": "精益愿景与战略规划", "weight": Decimal("0.10"), "max_score": Decimal("10")},
            {"name": "领导层参与度", "weight": Decimal("0.08"), "max_score": Decimal("8")},
            {"name": "资源配置", "weight": Decimal("0.07"), "max_score": Decimal("7")},
        ],
    },
    {
        "name": "流程管理",
        "weight": Decimal("0.25"),
        "max_score": Decimal("25"),
        "criteria": [
            {"name": "价值流识别与优化", "weight": Decimal("0.10"), "max_score": Decimal("10")},
            {"name": "标准化作业", "weight": Decimal("0.08"), "max_score": Decimal("8")},
            {"name": "持续改进机制", "weight": Decimal("0.07"), "max_score": Decimal("7")},
        ],
    },
    {
        "name": "人员能力",
        "weight": Decimal("0.25"),
        "max_score": Decimal("25"),
        "criteria": [
            {"name": "精益培训体系", "weight": Decimal("0.10"), "max_score": Decimal("10")},
            {"name": "多能工培养", "weight": Decimal("0.08"), "max_score": Decimal("8")},
            {"name": "员工参与度", "weight": Decimal("0.07"), "max_score": Decimal("7")},
        ],
    },
    {
        "name": "绩效成果",
        "weight": Decimal("0.25"),
        "max_score": Decimal("25"),
        "criteria": [
            {"name": "质量指标", "weight": Decimal("0.10"), "max_score": Decimal("10")},
            {"name": "效率指标", "weight": Decimal("0.08"), "max_score": Decimal("8")},
            {"name": "成本改善", "weight": Decimal("0.07"), "max_score": Decimal("7")},
        ],
    },
]

# Lean 2.0 five dimensions (Industry 5.0 extended)
LEAN20_DIMENSIONS = [
    {
        "name": "Operational Lean (O)",
        "code": "O",
        "weight": Decimal("0.30"),
        "max_score": Decimal("30"),
        "criteria": [
            {"name": "OEE / Flow efficiency", "weight": Decimal("0.10"), "max_score": Decimal("10")},
            {"name": "Quality system maturity", "weight": Decimal("0.10"), "max_score": Decimal("10")},
            {"name": "Standard work coverage", "weight": Decimal("0.10"), "max_score": Decimal("10")},
        ],
    },
    {
        "name": "Digital Lean (D)",
        "code": "D",
        "weight": Decimal("0.25"),
        "max_score": Decimal("25"),
        "criteria": [
            {"name": "MES / ERP integration", "weight": Decimal("0.08"), "max_score": Decimal("8")},
            {"name": "IoT / Real-time visibility", "weight": Decimal("0.09"), "max_score": Decimal("9")},
            {"name": "AI-driven decision support", "weight": Decimal("0.08"), "max_score": Decimal("8")},
        ],
    },
    {
        "name": "Green Lean (G)",
        "code": "G",
        "weight": Decimal("0.20"),
        "max_score": Decimal("20"),
        "criteria": [
            {"name": "Carbon footprint measurement", "weight": Decimal("0.07"), "max_score": Decimal("7")},
            {"name": "Green Kaizen / ISO 50001", "weight": Decimal("0.07"), "max_score": Decimal("7")},
            {"name": "CBAM compliance readiness", "weight": Decimal("0.06"), "max_score": Decimal("6")},
        ],
    },
    {
        "name": "Resilience (R)",
        "code": "R",
        "weight": Decimal("0.15"),
        "max_score": Decimal("15"),
        "criteria": [
            {"name": "Supply chain dual-source coverage", "weight": Decimal("0.05"), "max_score": Decimal("5")},
            {"name": "Anomaly response capability", "weight": Decimal("0.05"), "max_score": Decimal("5")},
            {"name": "Resilience index / stress test", "weight": Decimal("0.05"), "max_score": Decimal("5")},
        ],
    },
    {
        "name": "Human-Centric (H)",
        "code": "H",
        "weight": Decimal("0.10"),
        "max_score": Decimal("10"),
        "criteria": [
            {"name": "Employee-led improvement ratio", "weight": Decimal("0.04"), "max_score": Decimal("4")},
            {"name": "T-shaped talent program", "weight": Decimal("0.03"), "max_score": Decimal("3")},
            {"name": "Human-AI collaboration level", "weight": Decimal("0.03"), "max_score": Decimal("3")},
        ],
    },
]


def _calc_level(score: Decimal, max_score: Decimal) -> str:
    """根据得分百分比计算等级。"""
    if max_score <= 0:
        return "L1"
    pct = float(score) / float(max_score) * 100
    if pct >= 90:
        return "L5"
    elif pct >= 70:
        return "L4"
    elif pct >= 50:
        return "L3"
    elif pct >= 30:
        return "L2"
    return "L1"


def _calc_composite_level(dimension_scores: dict[str, Decimal], dimension_weights: dict[str, Decimal]) -> tuple[Decimal, str]:
    """Calculate Lean 2.0 composite index and level from 5 dimensions.

    Each dimension score is on 1-5 scale. Composite = weighted sum.
    Level mapping: 1.0-1.5=L1, 1.6-2.3=L2, 2.4-3.2=L3, 3.3-4.2=L4, 4.3-5.0=L5.
    Returns (composite_index, level_label).
    """
    composite = Decimal("0")
    for code, score in dimension_scores.items():
        composite += score * dimension_weights.get(code, Decimal("0"))
    composite = composite.quantize(Decimal("0.01"))

    ci = float(composite)
    if ci >= 4.3:
        level = "L5 - World-class"
    elif ci >= 3.3:
        level = "L4 - Proactive"
    elif ci >= 2.4:
        level = "L3 - Systematic"
    elif ci >= 1.6:
        level = "L2 - Developing"
    else:
        level = "L1 - Initial"
    return composite, level


def _score_to_5level(score: Decimal, max_score: Decimal) -> Decimal:
    """Convert a percentage-based score to 1-5 scale for Lean 2.0."""
    if max_score <= 0:
        return Decimal("1.0")
    pct = float(score) / float(max_score)
    return Decimal(str(round(1 + pct * 4, 1)))


class MaturityService:
    """成熟度评估业务服务。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # 查询
    # ============================================================

    async def list_assessments(
        self,
        factory_id: int,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse:
        """查询评估列表。"""
        query = select(MaturityAssessment).where(
            MaturityAssessment.factory_id == factory_id
        )
        if status:
            query = query.where(MaturityAssessment.status == status)
        query = query.order_by(desc(MaturityAssessment.created_at))
        result = await paginate(self.db, query, page, page_size)

        items = []
        for a in result.data:
            assessor = await self.db.get(User, a.assessor_id)
            items.append(AssessmentListItem(
                id=a.id, assessment_type=a.assessment_type,
                area_name=a.area_name,
                assessor_name=assessor.display_name if assessor else "",
                overall_level=a.overall_level,
                total_score=a.total_score, max_score=a.max_score,
                status=a.status, assessment_date=a.assessment_date,
                created_at=a.created_at,
            ))

        return PaginatedResponse.create(
            items=[i.model_dump() for i in items],
            total=result.pagination["total"], page=page, page_size=page_size,
        )

    async def get_assessment(self, assessment_id: int) -> AssessmentDetailResponse:
        """获取评估详情。"""
        result = await self.db.execute(
            select(MaturityAssessment)
            .options(
                selectinload(MaturityAssessment.dimensions)
                .selectinload(MaturityDimension.criteria),
            )
            .where(MaturityAssessment.id == assessment_id)
        )
        assessment = result.scalar_one_or_none()
        if assessment is None:
            raise NotFoundError("评估", assessment_id)

        assessor = await self.db.get(User, assessment.assessor_id)

        dimensions = []
        for d in (assessment.dimensions or []):
            criteria = []
            for c in (d.criteria or []):
                criteria.append(CriterionResponse(
                    id=c.id, criterion_name=c.criterion_name,
                    description=c.description, weight=c.weight,
                    score=c.score, max_score=c.max_score, level=c.level,
                    evidence=c.evidence, remarks=c.remarks,
                    improvement_suggestion=c.improvement_suggestion,
                ))
            dimensions.append(DimensionResponse(
                id=d.id, dimension_name=d.dimension_name,
                weight=d.weight, score=d.score, max_score=d.max_score,
                level=d.level, findings=d.findings,
                action_items=d.action_items, criteria=criteria,
            ))
        dimensions.sort(key=lambda x: x.dimension_name)

        return AssessmentDetailResponse(
            id=assessment.id,
            assessment_type=assessment.assessment_type,
            area_name=assessment.area_name,
            assessor_name=assessor.display_name if assessor else "",
            assessment_date=assessment.assessment_date,
            overall_level=assessment.overall_level,
            total_score=assessment.total_score,
            max_score=assessment.max_score,
            status=assessment.status,
            summary=assessment.summary,
            recommendations=assessment.recommendations,
            completed_at=assessment.completed_at,
            created_at=assessment.created_at,
            dimensions=dimensions,
        )

    # ============================================================
    # CRUD
    # ============================================================

    async def create_assessment(
        self, data: AssessmentCreateRequest, user_id: int, factory_id: int,
    ) -> AssessmentDetailResponse:
        """创建评估（自动生成默认维度和细项）。"""
        assessment = MaturityAssessment(
            assessment_type=data.assessment_type,
            area_name=data.area_name,
            assessor_id=user_id,
            factory_id=factory_id,
            max_score=data.max_score,
            assessment_date=data.assessment_date,
            status="draft",
        )
        self.db.add(assessment)
        await self.db.flush()

        # Select dimension template based on assessment type
        if data.assessment_type == "lean20":
            dim_template = LEAN20_DIMENSIONS
        else:
            dim_template = DEFAULT_DIMENSIONS

        # 自动生成默认维度和细项
        for idx, dim_tpl in enumerate(dim_template):
            dim = MaturityDimension(
                assessment_id=assessment.id,
                dimension_name=dim_tpl["name"],
                weight=dim_tpl["weight"],
                max_score=dim_tpl["max_score"],
                sort_order=idx,
            )
            self.db.add(dim)
            await self.db.flush()

            for cidx, crit_tpl in enumerate(dim_tpl["criteria"]):
                self.db.add(MaturityCriterion(
                    dimension_id=dim.id,
                    criterion_name=crit_tpl["name"],
                    weight=crit_tpl["weight"],
                    max_score=crit_tpl["max_score"],
                    sort_order=cidx,
                ))
        await self.db.flush()

        return await self.get_assessment(assessment.id)

    async def save_dimension_scores(
        self, assessment_id: int, scores: list[DimensionScoreRequest],
    ) -> AssessmentDetailResponse:
        """保存维度评分。"""
        assessment = await self.db.get(MaturityAssessment, assessment_id)
        if assessment is None:
            raise NotFoundError("评估", assessment_id)
        if assessment.status == "completed":
            raise AppError("已完成的评估不可修改", code="INVALID_STATE")

        for ds in scores:
            dim = await self.db.get(MaturityDimension, ds.dimension_id)
            if dim is None or dim.assessment_id != assessment_id:
                raise NotFoundError("维度", ds.dimension_id)

            # 保存细项评分
            if ds.criteria_scores:
                for cs in ds.criteria_scores:
                    criterion = await self.db.get(MaturityCriterion, cs.criterion_id)
                    if criterion is None or criterion.dimension_id != dim.id:
                        raise NotFoundError("细项", cs.criterion_id)
                    criterion.score = cs.score
                    criterion.level = cs.level
                    criterion.evidence = cs.evidence
                    criterion.remarks = cs.remarks
                    criterion.improvement_suggestion = cs.improvement_suggestion

                # 汇总维度得分
                total = sum(float(c.score or 0) for c in dim.criteria)
                dim.score = Decimal(str(total))
                dim.level = _calc_level(dim.score, dim.max_score)
            elif ds.score is not None:
                dim.score = ds.score
                dim.level = ds.level or _calc_level(ds.score, dim.max_score)

            dim.findings = ds.findings
            dim.action_items = ds.action_items
            await self.db.flush()

        # 汇总总分
        dims = await self.db.execute(
            select(MaturityDimension).where(MaturityDimension.assessment_id == assessment_id)
        )
        all_dims = dims.scalars().all()
        total = sum(float(d.score or 0) for d in all_dims)
        assessment.total_score = Decimal(str(total))

        # Use composite index for lean20 type
        if assessment.assessment_type == "lean20":
            dim_scores = {}
            dim_weights = {}
            for d in all_dims:
                name = d.dimension_name
                # Extract code from name like "Operational Lean (O)"
                import re
                code_match = re.search(r'\(([ODGRH])\)', name)
                if code_match:
                    code = code_match.group(1)
                    dim_scores[code] = _score_to_5level(d.score or Decimal("0"), d.max_score)
                    dim_weights[code] = d.weight
            if len(dim_scores) == 5:
                composite, level = _calc_composite_level(dim_scores, dim_weights)
                assessment.total_score = composite
                assessment.overall_level = level
            else:
                assessment.overall_level = _calc_level(assessment.total_score, assessment.max_score)
        else:
            assessment.overall_level = _calc_level(assessment.total_score, assessment.max_score)

        assessment.status = "in_progress"
        await self.db.flush()

        return await self.get_assessment(assessment_id)

    async def complete_assessment(
        self, assessment_id: int, data: AssessmentCompleteRequest,
    ) -> AssessmentDetailResponse:
        """完成评估。"""
        assessment = await self.db.get(MaturityAssessment, assessment_id)
        if assessment is None:
            raise NotFoundError("评估", assessment_id)
        if assessment.status == "completed":
            raise AppError("评估已完成", code="INVALID_STATE")

        # 确保总分已计算
        if assessment.total_score is None:
            dims = await self.db.execute(
                select(MaturityDimension).where(MaturityDimension.assessment_id == assessment_id)
            )
            total = sum(float(d.score or 0) for d in dims.scalars().all())
            assessment.total_score = Decimal(str(total))
            assessment.overall_level = _calc_level(assessment.total_score, assessment.max_score)

        assessment.status = "completed"
        assessment.summary = data.summary
        assessment.recommendations = data.recommendations
        assessment.completed_at = datetime.now(timezone.utc)
        await self.db.flush()

        return await self.get_assessment(assessment_id)

    # ============================================================
    # 统计
    # ============================================================

    async def get_stats(self, factory_id: int) -> MaturityStatsResponse:
        """获取成熟度统计。"""
        result = await self.db.execute(
            select(MaturityAssessment.status, func.count(MaturityAssessment.id))
            .where(MaturityAssessment.factory_id == factory_id)
            .group_by(MaturityAssessment.status)
        )
        status_counts = {row[0]: row[1] for row in result.all()}
        total = sum(status_counts.values())

        avg_result = await self.db.execute(
            select(func.avg(MaturityAssessment.total_score))
            .where(
                MaturityAssessment.factory_id == factory_id,
                MaturityAssessment.total_score.isnot(None),
            )
        )
        avg_score = float(avg_result.scalar() or 0)

        return MaturityStatsResponse(
            total=total,
            completed=status_counts.get("completed", 0),
            in_progress=status_counts.get("in_progress", 0),
            draft=status_counts.get("draft", 0),
            avg_score=round(avg_score, 2),
        )

    async def get_trends(self, factory_id: int) -> list[TrendResponse]:
        """获取历史趋势。"""
        result = await self.db.execute(
            select(MaturityAssessment)
            .where(
                MaturityAssessment.factory_id == factory_id,
                MaturityAssessment.status == "completed",
            )
            .order_by(MaturityAssessment.assessment_date)
        )
        trends = []
        for a in result.scalars().all():
            trends.append(TrendResponse(
                assessment_id=a.id, area_name=a.area_name,
                assessment_date=a.assessment_date,
                total_score=a.total_score, overall_level=a.overall_level,
            ))
        return trends
