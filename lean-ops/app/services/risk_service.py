"""风险管理业务逻辑。"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, NotFoundError
from app.core.pagination import PaginatedResponse, paginate
from app.models.project import Project
from app.models.risk import ProjectRisk

ALLOWED_UPDATE_FIELDS = {"title", "description", "probability", "impact", "status", "response_plan", "mitigation_actions", "due_date"}


class RiskService:
    """风险管理服务。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_risks(
        self,
        project_id: int,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse:
        """查询风险列表。"""
        query = (
            select(ProjectRisk)
            .where(
                ProjectRisk.project_id == project_id,
                ProjectRisk.is_deleted == False,
            )
        )
        if status:
            query = query.where(ProjectRisk.status == status)
        query = query.order_by(ProjectRisk.created_at.desc())
        return await paginate(self.db, query, page, page_size)

    async def get_risk(self, project_id: int, risk_id: int) -> ProjectRisk:
        """获取风险详情。"""
        risk = await self.db.get(ProjectRisk, risk_id)
        if risk is None or risk.project_id != project_id or risk.is_deleted:
            raise NotFoundError("风险", risk_id)
        return risk

    async def create_risk(
        self, project_id: int, data: dict, user_id: int,
    ) -> ProjectRisk:
        """创建风险。"""
        project = await self.db.get(Project, project_id)
        if project is None:
            raise NotFoundError("项目", project_id)

        risk = ProjectRisk(
            project_id=project_id,
            title=data["title"],
            description=data.get("description"),
            probability=data.get("probability", "medium"),
            impact=data.get("impact", "medium"),
            status=data.get("status", "identified"),
            owner_id=user_id,
            response_plan=data.get("response_plan"),
            mitigation_actions=data.get("mitigation_actions"),
            due_date=data.get("due_date"),
        )
        self.db.add(risk)
        await self.db.flush()
        return risk

    async def update_risk(
        self, project_id: int, risk_id: int, data: dict,
    ) -> ProjectRisk:
        """更新风险。"""
        risk = await self.get_risk(project_id, risk_id)

        # Validate status transition
        if "status" in data and data["status"] != risk.status:
            valid_transitions = {
                "identified": {"analyzing", "accepted", "closed"},
                "analyzing": {"mitigating", "accepted", "closed"},
                "mitigating": {"monitoring", "accepted", "closed"},
                "monitoring": {"closed", "mitigating"},
                "closed": set(),
                "accepted": set(),
            }
            current = risk.status
            allowed = valid_transitions.get(current, set())
            if data["status"] not in allowed:
                raise AppError(
                    f"风险状态不能从 '{current}' 变更为 '{data['status']}'",
                    code="VALIDATION_ERROR",
                )

        for field, value in data.items():
            if field in ALLOWED_UPDATE_FIELDS:
                setattr(risk, field, value)

        await self.db.flush()
        return risk

    async def delete_risk(self, project_id: int, risk_id: int) -> None:
        """软删除风险。"""
        risk = await self.get_risk(project_id, risk_id)
        risk.is_deleted = True
        risk.deleted_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def get_matrix(self, project_id: int) -> dict:
        """获取风险矩阵数据。"""
        result = await self.db.execute(
            select(ProjectRisk).where(
                ProjectRisk.project_id == project_id,
                ProjectRisk.is_deleted == False,
            )
        )
        risks = result.scalars().all()

        matrix = {
            "critical": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "high": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "medium": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "low": {"low": 0, "medium": 0, "high": 0, "critical": 0},
        }

        risk_list = []
        for r in risks:
            if r.probability in matrix and r.impact in matrix[r.probability]:
                matrix[r.probability][r.impact] += 1
            risk_list.append({
                "id": r.id,
                "title": r.title,
                "probability": r.probability,
                "impact": r.impact,
                "status": r.status,
                "owner_id": r.owner_id,
            })

        # Summary
        total = len(risks)
        open_risks = sum(1 for r in risks if r.status not in ("closed", "accepted"))

        return {
            "matrix": matrix,
            "risks": risk_list,
            "summary": {
                "total": total,
                "open": open_risks,
            },
        }
