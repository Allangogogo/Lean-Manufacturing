"""
报表中心 API 接口

- GET /api/v1/reports/kpis     — 综合 KPI 数据
- GET /api/v1/reports/trends   — 各模块趋势数据
- GET /api/v1/reports/summary  — 各模块汇总
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user
from app.models.kaizen import KaizenProposal
from app.models.fives import FiveSAudit
from app.models.training import TrainingSession
from app.models.tpm import TPMEquipment, TPMFault
from app.models.project import Project, ProjectTask
from app.models.practice import BestPractice
from app.models.maturity import MaturityAssessment

router = APIRouter()


@router.get("/kpis")
async def get_kpis(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """综合 KPI 数据。"""
    fid = user.factory_id

    # 改善提案
    proposals_total = (await db.execute(
        select(func.count(KaizenProposal.id)).where(KaizenProposal.factory_id == fid)
    )).scalar() or 0
    proposals_implemented = (await db.execute(
        select(func.count(KaizenProposal.id)).where(
            KaizenProposal.factory_id == fid,
            KaizenProposal.status.in_(["implementing", "verified", "closed"]),
        )
    )).scalar() or 0

    # 5S 审核
    audits_total = (await db.execute(
        select(func.count(FiveSAudit.id)).where(FiveSAudit.factory_id == fid)
    )).scalar() or 0
    audits_avg_score = (await db.execute(
        select(func.avg(FiveSAudit.score)).where(
            FiveSAudit.factory_id == fid, FiveSAudit.status == "completed"
        )
    )).scalar() or 0

    # 培训
    training_total = (await db.execute(
        select(func.count(TrainingSession.id)).where(TrainingSession.factory_id == fid)
    )).scalar() or 0

    # TPM 设备
    equipment_total = (await db.execute(
        select(func.count(TPMEquipment.id)).where(TPMEquipment.factory_id == fid)
    )).scalar() or 0
    equipment_fault = (await db.execute(
        select(func.count(TPMEquipment.id)).where(
            TPMEquipment.factory_id == fid, TPMEquipment.status == "fault"
        )
    )).scalar() or 0
    faults_total = (await db.execute(
        select(func.count(TPMFault.id)).where(TPMFault.factory_id == fid)
    )).scalar() or 0
    faults_open = (await db.execute(
        select(func.count(TPMFault.id)).where(
            TPMFault.factory_id == fid,
            TPMFault.status.in_(["reported", "diagnosing", "repairing"]),
        )
    )).scalar() or 0

    # 项目
    projects_total = (await db.execute(
        select(func.count(Project.id)).where(Project.factory_id == fid)
    )).scalar() or 0
    projects_active = (await db.execute(
        select(func.count(Project.id)).where(
            Project.factory_id == fid, Project.status == "active"
        )
    )).scalar() or 0

    # 任务
    tasks_total = (await db.execute(
        select(func.count(ProjectTask.id))
        .join(Project, Project.id == ProjectTask.project_id)
        .where(Project.factory_id == fid)
    )).scalar() or 0
    tasks_done = (await db.execute(
        select(func.count(ProjectTask.id))
        .join(Project, Project.id == ProjectTask.project_id)
        .where(Project.factory_id == fid, ProjectTask.status == "done")
    )).scalar() or 0

    # Best Practice
    practices_total = (await db.execute(
        select(func.count(BestPractice.id)).where(BestPractice.factory_id == fid)
    )).scalar() or 0
    practices_published = (await db.execute(
        select(func.count(BestPractice.id)).where(
            BestPractice.factory_id == fid, BestPractice.status == "published"
        )
    )).scalar() or 0

    # 成熟度
    maturity_avg = (await db.execute(
        select(func.avg(MaturityAssessment.total_score)).where(
            MaturityAssessment.factory_id == fid,
            MaturityAssessment.status == "completed",
        )
    )).scalar() or 0

    return {
        "kaizen": {
            "total": proposals_total,
            "implemented": proposals_implemented,
            "rate": round(proposals_implemented / proposals_total * 100, 1) if proposals_total > 0 else 0,
        },
        "fives": {
            "total": audits_total,
            "avg_score": round(float(audits_avg_score), 1),
        },
        "training": {"total": training_total},
        "tpm": {
            "equipment_total": equipment_total,
            "equipment_fault": equipment_fault,
            "faults_total": faults_total,
            "faults_open": faults_open,
            "availability": round((equipment_total - equipment_fault) / equipment_total * 100, 1) if equipment_total > 0 else 100,
        },
        "projects": {
            "total": projects_total,
            "active": projects_active,
            "tasks_total": tasks_total,
            "tasks_done": tasks_done,
            "task_rate": round(tasks_done / tasks_total * 100, 1) if tasks_total > 0 else 0,
        },
        "practices": {
            "total": practices_total,
            "published": practices_published,
        },
        "maturity": {
            "avg_score": round(float(maturity_avg), 1),
        },
    }


@router.get("/summary")
async def get_summary(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """各模块最新数据摘要。"""
    fid = user.factory_id

    # 最近提案
    recent_proposals = (await db.execute(
        select(KaizenProposal)
        .where(KaizenProposal.factory_id == fid)
        .order_by(desc(KaizenProposal.created_at))
        .limit(5)
    )).scalars().all()

    # 最近审计
    recent_audits = (await db.execute(
        select(FiveSAudit)
        .where(FiveSAudit.factory_id == fid)
        .order_by(desc(FiveSAudit.created_at))
        .limit(5)
    )).scalars().all()

    # 故障设备
    fault_equipment = (await db.execute(
        select(TPMEquipment)
        .where(TPMEquipment.factory_id == fid, TPMEquipment.status == "fault")
        .limit(5)
    )).scalars().all()

    # 进行中项目
    active_projects = (await db.execute(
        select(Project)
        .where(Project.factory_id == fid, Project.status == "active")
        .order_by(desc(Project.priority))
        .limit(5)
    )).scalars().all()

    return {
        "recent_proposals": [
            {"id": p.id, "title": p.title, "status": p.status, "priority": p.priority}
            for p in recent_proposals
        ],
        "recent_audits": [
            {"id": a.id, "area_name": a.area_name, "score": float(a.score) if a.score else 0, "status": a.status}
            for a in recent_audits
        ],
        "fault_equipment": [
            {"id": e.id, "code": e.equipment_code, "name": e.equipment_name}
            for e in fault_equipment
        ],
        "active_projects": [
            {"id": p.id, "name": p.name, "priority": p.priority, "status": p.status}
            for p in active_projects
        ],
    }
