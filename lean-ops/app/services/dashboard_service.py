# app/services/dashboard_service.py
"""项目 KPI 仪表板服务。"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.enums import TaskStatus
from app.models.project import Project, ProjectTask, ProjectUpdate


class DashboardService:
    """项目 KPI 数据聚合。"""

    # Health score weights
    SCHEDULE_WEIGHT = 0.35
    BUDGET_WEIGHT = 0.25
    RISK_WEIGHT = 0.20
    QUALITY_WEIGHT = 0.20

    # Health level thresholds
    THRESHOLD_GREEN = 0.8
    THRESHOLD_YELLOW = 0.6
    THRESHOLD_ORANGE = 0.4

    # Burn rate thresholds
    BURN_RATE_CRITICAL_RATIO = 1.0
    BURN_RATE_WARNING_RATIO = 0.8

    def __init__(self, db: AsyncSession):
        self.db = db

    def _calculate_health_score(
        self,
        planned_progress: int,
        actual_progress: int,
        budget: Decimal,
        actual_cost: Decimal,
        open_risks: int,
        total_risks: int,
        total_tasks: int,
        completed_tasks: int,
    ) -> dict:
        """计算项目健康度评分。"""
        # Schedule score
        if planned_progress > 0:
            schedule_score = min(actual_progress / planned_progress, 1.5)
        else:
            schedule_score = 1.0

        # Budget score
        if budget and budget > 0:
            cost = max(actual_cost, Decimal("1"))
            budget_score = min(float(budget / cost), 1.5)
        else:
            budget_score = 0.5

        # Risk score
        if total_risks > 0:
            risk_score = 1 - (open_risks / total_risks)
        else:
            risk_score = 1.0

        # Quality score
        if total_tasks > 0:
            quality_score = completed_tasks / total_tasks
        else:
            quality_score = 1.0

        health_score = (
            self.SCHEDULE_WEIGHT * schedule_score
            + self.BUDGET_WEIGHT * budget_score
            + self.RISK_WEIGHT * risk_score
            + self.QUALITY_WEIGHT * quality_score
        )
        health_score = max(0, min(health_score, 1.5))

        if health_score >= self.THRESHOLD_GREEN:
            level = "green"
        elif health_score >= self.THRESHOLD_YELLOW:
            level = "yellow"
        elif health_score >= self.THRESHOLD_ORANGE:
            level = "orange"
        else:
            level = "red"

        return {
            "score": round(health_score, 2),
            "level": level,
            "breakdown": {
                "schedule": round(schedule_score, 2),
                "budget": round(budget_score, 2),
                "risk": round(risk_score, 2),
                "quality": round(quality_score, 2),
            },
        }

    def _calculate_planned_progress(self, project: Project) -> int:
        """基于时间推移计算计划进度百分比。"""
        if project.start_date and project.target_end_date:
            total_days = (project.target_end_date - project.start_date).days
            elapsed_days = (date.today() - project.start_date).days
            if total_days > 0:
                return min(int(elapsed_days / total_days * 100), 100)
        return 0

    def _budget_status(self, project: Project) -> dict:
        """计算预算状态和消耗速率。"""
        budget = project.budget or Decimal("0")
        actual_cost = project.actual_cost or Decimal("0")
        remaining = budget - actual_cost
        if budget > 0:
            cost_ratio = float(actual_cost / budget)
            if cost_ratio > self.BURN_RATE_CRITICAL_RATIO:
                burn_rate = "critical"
            elif cost_ratio > self.BURN_RATE_WARNING_RATIO:
                burn_rate = "warning"
            else:
                burn_rate = "normal"
        else:
            burn_rate = "normal"

        return {
            "total": float(budget),
            "spent": float(actual_cost),
            "remaining": float(remaining),
            "burn_rate": burn_rate,
        }

    async def _fetch_health_history(self, project_id: int) -> list[dict]:
        """获取项目历史更新的健康度趋势。"""
        updates_result = await self.db.execute(
            select(ProjectUpdate)
            .where(ProjectUpdate.project_id == project_id, ProjectUpdate.is_deleted == False)
            .order_by(ProjectUpdate.update_date)
        )
        updates = updates_result.scalars().all()
        return [
            {"date": update.update_date.isoformat(), "score": update.progress_pct / 100}
            for update in updates
        ]

    async def get_dashboard(self, project_id: int) -> dict:
        """获取项目 KPI 仪表板数据。"""
        project = await self.db.get(Project, project_id)
        if project is None:
            raise NotFoundError("项目", project_id)

        # Task stats
        task_result = await self.db.execute(
            select(
                func.count(ProjectTask.id).label("total"),
                func.count().filter(ProjectTask.status == TaskStatus.DONE).label("completed"),
                func.count().filter(ProjectTask.status == TaskStatus.BLOCKED).label("blocked"),
                func.count().filter(
                    ProjectTask.due_date < date.today(),
                    ProjectTask.status != TaskStatus.DONE,
                ).label("overdue"),
            ).where(
                ProjectTask.project_id == project_id,
                ProjectTask.is_deleted == False,
            )
        )
        task_counts = task_result.one()

        # Planned progress (based on time elapsed)
        planned_progress = self._calculate_planned_progress(project)

        # Actual progress
        actual_progress = int(task_counts.completed / task_counts.total * 100) if task_counts.total > 0 else 0

        # Risk counts (real data)
        from app.models.risk import ProjectRisk
        risk_result = await self.db.execute(
            select(
                func.count(ProjectRisk.id).label("total"),
                func.count().filter(
                    ProjectRisk.status.notin_(["closed", "accepted"]),
                ).label("open"),
            ).where(
                ProjectRisk.project_id == project_id,
                ProjectRisk.is_deleted == False,
            )
        )
        rc = risk_result.one()
        total_risks = rc.total
        open_risks = rc.open

        # Health score
        health = self._calculate_health_score(
            planned_progress=planned_progress,
            actual_progress=actual_progress,
            budget=project.budget or Decimal("0"),
            actual_cost=project.actual_cost or Decimal("0"),
            open_risks=open_risks,
            total_risks=total_risks,
            total_tasks=task_counts.total,
            completed_tasks=task_counts.completed,
        )

        # Budget
        budget_info = self._budget_status(project)

        # Health history from weekly updates
        health_history = await self._fetch_health_history(project_id)

        return {
            "health": health,
            "schedule": {
                "planned_progress": planned_progress,
                "actual_progress": actual_progress,
                "deviation": actual_progress - planned_progress,
            },
            "budget": budget_info,
            "quality": {
                "total_tasks": task_counts.total,
                "completed": task_counts.completed,
                "blocked": task_counts.blocked,
                "overdue": task_counts.overdue,
            },
            "health_history": health_history,
        }
