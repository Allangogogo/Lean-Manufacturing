"""甘特图数据服务。"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.project import Project, ProjectTask, ProjectMilestone, task_dependencies


class GanttService:
    """甘特图数据聚合。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_gantt_data(self, project_id: int) -> dict:
        """获取甘特图所需的任务+依赖+里程碑数据。"""
        project = await self.db.get(Project, project_id)
        if project is None:
            raise NotFoundError("项目", project_id)

        # Fetch all tasks
        task_result = await self.db.execute(
            select(ProjectTask).where(
                ProjectTask.project_id == project_id,
                ProjectTask.is_deleted == False,
            ).order_by(ProjectTask.sort_order)
        )
        tasks = task_result.scalars().all()

        # Fetch all dependencies
        dep_result = await self.db.execute(
            select(task_dependencies).where(
                task_dependencies.c.task_id.in_([t.id for t in tasks])
            )
        )
        dep_map: dict[int, list[int]] = {}
        for row in dep_result.all():
            dep_map.setdefault(row.task_id, []).append(row.depends_on_id)

        # Fetch milestones
        ms_result = await self.db.execute(
            select(ProjectMilestone).where(
                ProjectMilestone.project_id == project_id,
                ProjectMilestone.is_deleted == False,
            ).order_by(ProjectMilestone.sort_order)
        )
        milestones = ms_result.scalars().all()

        # Build gantt items
        gantt_tasks = []
        for t in tasks:
            progress = 100 if t.status == "done" else (50 if t.status == "in_progress" else 0)
            gantt_tasks.append({
                "id": f"task-{t.id}",
                "name": t.name,
                "start": t.due_date.isoformat() if t.due_date else date.today().isoformat(),
                "end": (t.due_date or date.today()).isoformat(),
                "progress": progress,
                "dependencies": ",".join(f"task-{d}" for d in dep_map.get(t.id, [])),
                "custom_class": "task",
            })

        gantt_milestones = []
        for m in milestones:
            gantt_milestones.append({
                "id": f"milestone-{m.id}",
                "name": m.name,
                "start": m.target_date.isoformat() if m.target_date else date.today().isoformat(),
                "end": m.target_date.isoformat() if m.target_date else date.today().isoformat(),
                "progress": 100 if m.status == "completed" else 0,
                "dependencies": "",
                "custom_class": "milestone",
            })

        return {"tasks": gantt_tasks + gantt_milestones}

    async def update_task_dates(
        self, project_id: int, task_id: int, start: str, end: str,
    ) -> dict:
        """甘特图拖拽更新任务时间。"""
        from datetime import datetime as dt

        task = await self.db.get(ProjectTask, task_id)
        if task is None or task.project_id != project_id:
            raise NotFoundError("任务", task_id)

        task.due_date = dt.strptime(end, "%Y-%m-%d").date()
        await self.db.flush()

        return {"id": task_id, "start": start, "end": end}
