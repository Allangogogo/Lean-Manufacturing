"""
5S 审核业务逻辑层

职责：
1. 审核计划 CRUD
2. 审核评分管理
3. 改善项跟踪
4. 统计查询
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.core.pagination import PaginatedResponse, paginate
from app.models.fives import FiveSAudit, FiveSArea, FiveSImprovement, FiveSItem
from app.models.user import User
from app.schemas.fives import (
    FiveSAuditCreateRequest,
    FiveSAuditDetailResponse,
    FiveSAuditListItem,
    FiveSAuditScoreRequest,
    FiveSAuditStatsResponse,
    FiveSImprovementCreateRequest,
    FiveSImprovementResponse,
    FiveSImprovementUpdateRequest,
    FiveSItemResponse,
)


class FiveSService:
    """5S 审核业务服务。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # 区域管理
    # ============================================================

    async def list_areas(self, factory_id: int) -> List[dict]:
        """获取工厂下的 5S 区域列表。"""
        result = await self.db.execute(
            select(FiveSArea)
            .where(FiveSArea.factory_id == factory_id, FiveSArea.is_active == True)
            .order_by(FiveSArea.name)
        )
        areas = result.scalars().all()
        items = []
        for a in areas:
            responsible = await self.db.get(User, a.responsible_id) if a.responsible_id else None
            items.append({
                "id": a.id,
                "name": a.name,
                "code": a.code,
                "description": a.description,
                "responsible_name": responsible.display_name if responsible else "",
                "is_active": a.is_active,
            })
        return items

    # ============================================================
    # 审核计划
    # ============================================================

    async def list_audits(
        self,
        factory_id: int,
        status: Optional[str] = None,
        audit_type: Optional[str] = None,
        area_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse:
        """查询审核列表（支持筛选、分页）。"""
        query = select(FiveSAudit).where(FiveSAudit.factory_id == factory_id)

        if status:
            query = query.where(FiveSAudit.status == status)
        if audit_type:
            query = query.where(FiveSAudit.audit_type == audit_type)
        if area_id:
            query = query.where(FiveSAudit.area_id == area_id)

        query = query.order_by(desc(FiveSAudit.scheduled_date))
        result = await paginate(self.db, query, page, page_size)

        items = []
        for a in result.data:
            area = await self.db.get(FiveSArea, a.area_id)
            auditor = await self.db.get(User, a.auditor_id)
            # 统计改善项数量
            imp_count = await self.db.execute(
                select(func.count(FiveSImprovement.id)).where(
                    FiveSImprovement.audit_id == a.id,
                    FiveSImprovement.status != "completed",
                )
            )
            items.append(FiveSAuditListItem(
                id=a.id,
                area_name=area.name if area else "",
                auditor_name=auditor.display_name if auditor else "",
                audit_type=a.audit_type,
                score=a.score,
                max_score=a.max_score,
                status=a.status,
                scheduled_date=a.scheduled_date,
                completed_date=a.completed_date,
                improvement_count=imp_count.scalar() or 0,
            ))

        return PaginatedResponse.create(
            items=[i.model_dump() for i in items],
            total=result.pagination["total"],
            page=page,
            page_size=page_size,
        )

    async def get_audit(self, audit_id: int) -> FiveSAuditDetailResponse:
        """获取审核详情（含评分项和改善项）。"""
        result = await self.db.execute(
            select(FiveSAudit)
            .options(
                selectinload(FiveSAudit.items),
                selectinload(FiveSAudit.improvements),
            )
            .where(FiveSAudit.id == audit_id)
        )
        audit = result.scalar_one_or_none()
        if audit is None:
            raise NotFoundError("5S 审核", audit_id)

        area = await self.db.get(FiveSArea, audit.area_id)
        auditor = await self.db.get(User, audit.auditor_id)

        items = []
        for item in (audit.items or []):
            items.append(FiveSItemResponse(
                id=item.id,
                s_category=item.s_category,
                item_name=item.item_name,
                description=item.description,
                weight=item.weight,
                score=item.score,
                max_score=item.max_score,
                photo_path=item.photo_path,
                remarks=item.remarks,
            ))

        improvements = []
        for imp in (audit.improvements or []):
            assigned = await self.db.get(User, imp.assigned_to_id) if imp.assigned_to_id else None
            improvements.append(FiveSImprovementResponse(
                id=imp.id,
                audit_id=imp.audit_id,
                item_description=imp.item_description,
                assigned_to_id=imp.assigned_to_id,
                assigned_to_name=assigned.display_name if assigned else "",
                status=imp.status,
                due_date=imp.due_date,
                completed_date=imp.completed_date,
                evidence_path=imp.evidence_path,
                verified_by_id=imp.verified_by_id,
                verified_at=imp.verified_at,
                created_at=imp.created_at,
            ))

        return FiveSAuditDetailResponse(
            id=audit.id,
            area_id=audit.area_id,
            area_name=area.name if area else "",
            factory_id=audit.factory_id,
            auditor_id=audit.auditor_id,
            auditor_name=auditor.display_name if auditor else "",
            audit_type=audit.audit_type,
            score=audit.score,
            max_score=audit.max_score,
            status=audit.status,
            scheduled_date=audit.scheduled_date,
            completed_date=audit.completed_date,
            remarks=audit.remarks,
            created_at=audit.created_at,
            items=items,
            improvements=improvements,
        )

    async def create_audit(
        self,
        data: FiveSAuditCreateRequest,
        user_id: int,
        factory_id: int,
    ) -> FiveSAuditDetailResponse:
        """创建审核计划。"""
        # 验证区域存在
        area = await self.db.get(FiveSArea, data.area_id)
        if area is None:
            raise NotFoundError("审核区域", data.area_id)
        if area.factory_id != factory_id:
            raise ForbiddenError("无权审核其他工厂的区域")

        auditor_id = data.auditor_id or user_id

        audit = FiveSAudit(
            area_id=data.area_id,
            factory_id=factory_id,
            auditor_id=auditor_id,
            audit_type=data.audit_type,
            scheduled_date=data.scheduled_date,
            remarks=data.remarks,
            status="scheduled",
        )
        self.db.add(audit)
        await self.db.flush()

        # 创建默认审核项（5S 五大项）
        default_items = [
            ("sort", "整理", "是否区分必需品与非必需品，清除不必要物品"),
            ("straighten", "整顿", "物品是否定位放置、标识清晰"),
            ("shine", "清扫", "工作区域是否清洁、设备无污垢"),
            ("standardize", "清洁", "是否有标准化的5S检查流程"),
            ("sustain", "素养", "员工是否养成5S习惯、遵守规则"),
        ]
        for s_cat, name, desc_text in default_items:
            item = FiveSItem(
                audit_id=audit.id,
                s_category=s_cat,
                item_name=name,
                description=desc_text,
                weight=Decimal("1.0"),
                max_score=Decimal("20.0"),
            )
            self.db.add(item)

        await self.db.flush()
        return await self.get_audit(audit.id)

    async def save_scores(
        self,
        audit_id: int,
        data: FiveSAuditScoreRequest,
        user_id: int,
    ) -> FiveSAuditDetailResponse:
        """保存审核评分。"""
        audit = await self.db.get(FiveSAudit, audit_id)
        if audit is None:
            raise NotFoundError("5S 审核", audit_id)

        if audit.status == "completed":
            raise AppError("已完成的审核不可再修改评分", code="VALIDATION_ERROR")

        # 更新审核状态为进行中
        if audit.status == "scheduled":
            audit.status = "in_progress"

        # 更新评分项
        total_score = Decimal("0")
        total_max = Decimal("0")
        for item_data in data.items:
            item = await self.db.get(FiveSItem, item_data.id)
            if item is None or item.audit_id != audit_id:
                continue
            item.score = item_data.score
            item.remarks = item_data.remarks
            item.photo_path = item_data.photo_path
            total_score += item_data.score * item.weight
            total_max += item.max_score * item.weight

        # 计算总分（百分制）
        if total_max > 0:
            audit.score = (total_score / total_max * 100).quantize(Decimal("0.01"))
        if data.remarks:
            audit.remarks = data.remarks

        await self.db.flush()
        return await self.get_audit(audit_id)

    async def complete_audit(
        self,
        audit_id: int,
        user_id: int,
    ) -> FiveSAuditDetailResponse:
        """完成审核。"""
        audit = await self.db.get(FiveSAudit, audit_id)
        if audit is None:
            raise NotFoundError("5S 审核", audit_id)

        if audit.status == "completed":
            raise AppError("审核已完成", code="VALIDATION_ERROR")

        # 检查是否所有项都已评分
        result = await self.db.execute(
            select(FiveSItem).where(
                FiveSItem.audit_id == audit_id,
                FiveSItem.score.is_(None),
            )
        )
        unscored = result.scalars().all()
        if unscored:
            raise AppError(f"还有 {len(unscored)} 个审核项未评分", code="VALIDATION_ERROR")

        audit.status = "completed"
        audit.completed_date = date.today()
        await self.db.flush()

        return await self.get_audit(audit_id)

    async def get_stats(self, factory_id: int) -> FiveSAuditStatsResponse:
        """获取审核统计。"""
        result = await self.db.execute(
            select(
                FiveSAudit.status,
                func.count(FiveSAudit.id),
            )
            .where(FiveSAudit.factory_id == factory_id)
            .group_by(FiveSAudit.status)
        )
        status_counts = {row[0]: row[1] for row in result.all()}
        total = sum(status_counts.values())

        # 平均分
        avg_result = await self.db.execute(
            select(func.avg(FiveSAudit.score)).where(
                FiveSAudit.factory_id == factory_id,
                FiveSAudit.score.isnot(None),
            )
        )
        avg_score = avg_result.scalar() or 0

        # 未完成改善项
        imp_result = await self.db.execute(
            select(func.count(FiveSImprovement.id))
            .join(FiveSAudit, FiveSImprovement.audit_id == FiveSAudit.id)
            .where(
                FiveSAudit.factory_id == factory_id,
                FiveSImprovement.status != "completed",
            )
        )
        open_improvements = imp_result.scalar() or 0

        return FiveSAuditStatsResponse(
            total=total,
            scheduled=status_counts.get("scheduled", 0),
            in_progress=status_counts.get("in_progress", 0),
            completed=status_counts.get("completed", 0),
            avg_score=float(avg_score),
            open_improvements=open_improvements,
        )

    # ============================================================
    # 改善项管理
    # ============================================================

    async def list_improvements(
        self,
        factory_id: int,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse:
        """查询改善项列表。"""
        query = (
            select(FiveSImprovement)
            .join(FiveSAudit, FiveSImprovement.audit_id == FiveSAudit.id)
            .where(FiveSAudit.factory_id == factory_id)
        )
        if status:
            query = query.where(FiveSImprovement.status == status)
        query = query.order_by(desc(FiveSImprovement.created_at))

        result = await paginate(self.db, query, page, page_size)

        items = []
        for imp in result.data:
            assigned = await self.db.get(User, imp.assigned_to_id) if imp.assigned_to_id else None
            items.append(FiveSImprovementResponse(
                id=imp.id,
                audit_id=imp.audit_id,
                item_description=imp.item_description,
                assigned_to_id=imp.assigned_to_id,
                assigned_to_name=assigned.display_name if assigned else "",
                status=imp.status,
                due_date=imp.due_date,
                completed_date=imp.completed_date,
                evidence_path=imp.evidence_path,
                verified_by_id=imp.verified_by_id,
                verified_at=imp.verified_at,
                created_at=imp.created_at,
            ))

        return PaginatedResponse.create(
            items=[i.model_dump() for i in items],
            total=result.pagination["total"],
            page=page,
            page_size=page_size,
        )

    async def create_improvement(
        self,
        audit_id: int,
        data: FiveSImprovementCreateRequest,
        user_id: int,
        factory_id: int,
    ) -> FiveSImprovementResponse:
        """创建改善项。"""
        audit = await self.db.get(FiveSAudit, audit_id)
        if audit is None:
            raise NotFoundError("5S 审核", audit_id)
        if audit.factory_id != factory_id:
            raise ForbiddenError("无权操作其他工厂的审核")

        improvement = FiveSImprovement(
            audit_id=audit_id,
            item_description=data.item_description,
            assigned_to_id=data.assigned_to_id,
            due_date=data.due_date,
            status="open",
        )
        self.db.add(improvement)
        await self.db.flush()

        assigned = await self.db.get(User, improvement.assigned_to_id) if improvement.assigned_to_id else None
        return FiveSImprovementResponse(
            id=improvement.id,
            audit_id=improvement.audit_id,
            item_description=improvement.item_description,
            assigned_to_id=improvement.assigned_to_id,
            assigned_to_name=assigned.display_name if assigned else "",
            status=improvement.status,
            due_date=improvement.due_date,
            created_at=improvement.created_at,
        )

    async def update_improvement(
        self,
        improvement_id: int,
        data: FiveSImprovementUpdateRequest,
        user_id: int,
    ) -> FiveSImprovementResponse:
        """更新改善项。"""
        improvement = await self.db.get(FiveSImprovement, improvement_id)
        if improvement is None:
            raise NotFoundError("改善项", improvement_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(improvement, field, value)

        # 如果状态变为 completed，记录完成时间
        if data.status == "completed" and not improvement.completed_date:
            improvement.completed_date = date.today()

        await self.db.flush()

        assigned = await self.db.get(User, improvement.assigned_to_id) if improvement.assigned_to_id else None
        return FiveSImprovementResponse(
            id=improvement.id,
            audit_id=improvement.audit_id,
            item_description=improvement.item_description,
            assigned_to_id=improvement.assigned_to_id,
            assigned_to_name=assigned.display_name if assigned else "",
            status=improvement.status,
            due_date=improvement.due_date,
            completed_date=improvement.completed_date,
            evidence_path=improvement.evidence_path,
            verified_by_id=improvement.verified_by_id,
            verified_at=improvement.verified_at,
            created_at=improvement.created_at,
        )
