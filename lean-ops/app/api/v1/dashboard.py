"""
仪表板接口

- GET /dashboard/stats — KPI 统计数据
- GET /dashboard/todos  — 待办事项
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user
from app.models.kaizen import KaizenProposal
from app.models.fives import FiveSAudit
from app.models.training import TrainingSession
from app.models.tpm import TPMFault, TPMEquipment
from app.models.project import Project
from app.models.practice import BestPractice

router = APIRouter()


@router.get("/stats")
async def get_stats(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取仪表板 KPI 统计。"""
    factory_id = user.factory_id

    # 改善提案数
    kaizen_count = await db.execute(
        select(func.count(KaizenProposal.id)).where(
            KaizenProposal.factory_id == factory_id
        )
    )
    kaizen_total = kaizen_count.scalar() or 0

    # 5S 平均分
    fives_avg = await db.execute(
        select(func.avg(FiveSAudit.score)).where(
            FiveSAudit.factory_id == factory_id,
            FiveSAudit.status == "completed",
        )
    )
    fives_avg_score = fives_avg.scalar()

    # 培训场次
    training_count = await db.execute(
        select(func.count(TrainingSession.id)).where(
            TrainingSession.factory_id == factory_id
        )
    )
    training_total = training_count.scalar() or 0

    # 设备故障数
    fault_count = await db.execute(
        select(func.count(TPMFault.id)).join(TPMEquipment).where(
            TPMEquipment.factory_id == factory_id,
            TPMFault.status.in_(["reported", "diagnosing", "repairing"]),
        )
    )
    fault_total = fault_count.scalar() or 0

    # 项目数
    project_count = await db.execute(
        select(func.count(Project.id)).where(
            Project.factory_id == factory_id,
            Project.status.in_(["planning", "active"]),
        )
    )
    project_total = project_count.scalar() or 0

    # Best Practice 数
    bp_count = await db.execute(
        select(func.count(BestPractice.id)).where(
            BestPractice.factory_id == factory_id,
            BestPractice.status == "published",
        )
    )
    bp_total = bp_count.scalar() or 0

    return {
        "kaizen_count": kaizen_total,
        "fives_avg_score": round(float(fives_avg_score), 1) if fives_avg_score else None,
        "training_count": training_total,
        "fault_count": fault_total,
        "project_count": project_total,
        "practice_count": bp_total,
    }
