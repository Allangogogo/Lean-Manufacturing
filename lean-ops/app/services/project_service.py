"""
项目管理业务逻辑层

职责：
1. 项目 CRUD
2. 里程碑管理
3. 任务管理
4. 成员管理
5. 周报管理
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.core.pagination import PaginatedResponse, paginate
from app.models.project import (
    Project,
    ProjectMember,
    ProjectMilestone,
    ProjectTask,
    ProjectUpdate,
    task_dependencies,
)
from app.models.user import User
from app.schemas.project import (
    MilestoneCreateRequest,
    MilestoneResponse,
    MemberAddRequest,
    MemberResponse,
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectListItem,
    ProjectStatsResponse,
    ProjectUpdateRequest,
    TaskCreateRequest,
    TaskResponse,
    TaskUpdateRequest,
    UpdateCreateRequest,
    UpdateResponse,
)


class ProjectService:
    """项目管理业务服务。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # 项目 CRUD
    # ============================================================

    async def list_projects(
        self,
        factory_id: int,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse:
        """查询项目列表。"""
        query = (
            select(Project)
            .where(Project.factory_id == factory_id, Project.is_deleted == False)
            .options(joinedload(Project.owner))
        )
        if status:
            query = query.where(Project.status == status)
        query = query.order_by(desc(Project.created_at))

        # Subquery for task counts
        task_count_sq = (
            select(
                ProjectTask.project_id,
                func.count(ProjectTask.id).label("total"),
                func.count().filter(ProjectTask.status == "done").label("completed"),
            )
            .where(ProjectTask.is_deleted == False)
            .group_by(ProjectTask.project_id)
            .subquery()
        )

        result = await paginate(self.db, query, page, page_size)

        items = []
        for p in result.data:
            tc_result = await self.db.execute(
                select(task_count_sq).where(task_count_sq.c.project_id == p.id)
            )
            tc = tc_result.first()
            total = tc.total if tc else 0
            completed = tc.completed if tc else 0
            progress = int(completed / total * 100) if total > 0 else 0

            # Quick health score (schedule only, for list view)
            if p.start_date and p.target_end_date:
                total_days = (p.target_end_date - p.start_date).days
                from datetime import date as _date
                elapsed = (_date.today() - p.start_date).days
                planned = min(int(elapsed / total_days * 100), 100) if total_days > 0 else 0
                schedule_ratio = progress / planned if planned > 0 else 1.0
                if schedule_ratio >= 0.8:
                    health = "green"
                elif schedule_ratio >= 0.6:
                    health = "yellow"
                elif schedule_ratio >= 0.4:
                    health = "orange"
                else:
                    health = "red"
            else:
                health = ""

            items.append(ProjectListItem(
                id=p.id, name=p.name, project_type=p.project_type,
                owner_name=p.owner.display_name if p.owner else "",
                status=p.status, priority=p.priority,
                start_date=p.start_date, target_end_date=p.target_end_date,
                progress_pct=progress, task_count=total, completed_tasks=completed,
                health_level=health,
                lean20_dimensions=p.lean20_dimensions,
                source_assessment_id=p.source_assessment_id,
            ))

        return PaginatedResponse.create(
            items=[i.model_dump() for i in items],
            total=result.pagination["total"], page=page, page_size=page_size,
        )

    async def get_project(self, project_id: int) -> ProjectDetailResponse:
        """获取项目详情。"""
        result = await self.db.execute(
            select(Project)
            .options(
                selectinload(Project.milestones),
                selectinload(Project.tasks),
                selectinload(Project.members),
                selectinload(Project.updates),
                joinedload(Project.owner),
            )
            .where(Project.id == project_id, Project.is_deleted == False)
        )
        project = result.unique().scalar_one_or_none()
        if project is None:
            raise NotFoundError("项目", project_id)

        # Batch-load all referenced users
        task_assignee_ids = {t.assigned_to_id for t in (project.tasks or []) if t.assigned_to_id}
        member_user_ids = {m.user_id for m in (project.members or [])}
        update_author_ids = {u.author_id for u in (project.updates or [])}
        all_user_ids = task_assignee_ids | member_user_ids | update_author_ids

        users_result = await self.db.execute(
            select(User).where(User.id.in_(all_user_ids)) if all_user_ids else select(User).where(User.id == -1)
        )
        users_map = {u.id: u for u in users_result.scalars().all()}

        milestones = []
        for m in (project.milestones or []):
            if m.is_deleted:
                continue
            m_task_count = sum(1 for t in (project.tasks or []) if t.milestone_id == m.id and not t.is_deleted)
            m_completed = sum(1 for t in (project.tasks or []) if t.milestone_id == m.id and t.status == "done" and not t.is_deleted)
            milestones.append(MilestoneResponse(
                id=m.id, name=m.name, description=m.description,
                target_date=m.target_date, actual_date=m.actual_date,
                status=m.status, sort_order=m.sort_order,
                task_count=m_task_count, completed_tasks=m_completed,
            ))

        tasks = []
        for t in (project.tasks or []):
            if t.is_deleted:
                continue
            assignee = users_map.get(t.assigned_to_id) if t.assigned_to_id else None
            # Load dependency IDs
            dep_result = await self.db.execute(
                select(task_dependencies.c.depends_on_id).where(
                    task_dependencies.c.task_id == t.id
                )
            )
            dep_ids = [row[0] for row in dep_result.all()]
            tasks.append(TaskResponse(
                id=t.id, name=t.name, description=t.description,
                milestone_id=t.milestone_id, assigned_to_id=t.assigned_to_id,
                assigned_to_name=assignee.display_name if assignee else "",
                status=t.status, priority=t.priority,
                due_date=t.due_date, completed_date=t.completed_date,
                estimated_hours=t.estimated_hours, actual_hours=t.actual_hours,
                depends_on_ids=dep_ids,
            ))

        members = []
        for mem in (project.members or []):
            if mem.is_deleted:
                continue
            user = users_map.get(mem.user_id)
            members.append(MemberResponse(
                id=mem.id, user_id=mem.user_id,
                user_name=user.display_name if user else "",
                role=mem.role, joined_at=mem.joined_at,
            ))

        updates = []
        for u in (project.updates or []):
            if u.is_deleted:
                continue
            author = users_map.get(u.author_id)
            updates.append(UpdateResponse(
                id=u.id, author_name=author.display_name if author else "",
                update_date=u.update_date, progress_pct=u.progress_pct,
                accomplishments=u.accomplishments,
                plan_next_week=u.plan_next_week,
                risks_issues=u.risks_issues, created_at=u.created_at,
            ))

        return ProjectDetailResponse(
            id=project.id, name=project.name, description=project.description,
            project_type=project.project_type,
            owner_name=project.owner.display_name if project.owner else "",
            factory_id=project.factory_id, status=project.status,
            priority=project.priority, start_date=project.start_date,
            target_end_date=project.target_end_date,
            actual_end_date=project.actual_end_date,
            budget=project.budget, actual_cost=project.actual_cost,
            scope=project.scope, objectives=project.objectives,
            success_criteria=project.success_criteria,
            lean20_dimensions=project.lean20_dimensions,
            source_assessment_id=project.source_assessment_id,
            created_at=project.created_at,
            milestones=milestones, tasks=tasks, members=members, updates=updates,
        )

    async def create_project(
        self, data: ProjectCreateRequest, user_id: int, factory_id: int,
    ) -> ProjectDetailResponse:
        """创建项目。"""
        project = Project(
            name=data.name, description=data.description,
            project_type=data.project_type, owner_id=user_id,
            factory_id=factory_id, status="planning", priority=data.priority,
            start_date=data.start_date, target_end_date=data.target_end_date,
            budget=data.budget, scope=data.scope, objectives=data.objectives,
            success_criteria=data.success_criteria,
            lean20_dimensions=data.lean20_dimensions,
            source_assessment_id=data.source_assessment_id,
        )
        self.db.add(project)
        await self.db.flush()

        # 添加创建者为 owner
        member = ProjectMember(project_id=project.id, user_id=user_id, role="owner")
        self.db.add(member)
        await self.db.flush()

        return await self.get_project(project.id)

    async def update_project(
        self, project_id: int, data: ProjectUpdateRequest, user_id: int,
    ) -> ProjectDetailResponse:
        """更新项目。"""
        project = await self.db.get(Project, project_id)
        if project is None:
            raise NotFoundError("项目", project_id)
        if project.is_deleted:
            raise NotFoundError("项目", project_id)

        # Validate status transition
        if data.status and data.status != project.status:
            from app.models.enums import PROJECT_STATUS_TRANSITIONS, ProjectStatus
            current = ProjectStatus(project.status)
            allowed = PROJECT_STATUS_TRANSITIONS.get(current, set())
            try:
                target = ProjectStatus(data.status)
            except ValueError:
                raise AppError(f"无效的状态值: {data.status}", code="VALIDATION_ERROR")
            if target not in allowed:
                raise AppError(
                    f"状态不能从 '{project.status}' 变更为 '{data.status}'",
                    code="VALIDATION_ERROR",
                )

        if data.status and data.status == "completed":
            project.actual_end_date = date.today()
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        return await self.get_project(project_id)

    # ============================================================
    # 里程碑
    # ============================================================

    async def add_milestone(
        self, project_id: int, data: MilestoneCreateRequest,
    ) -> ProjectDetailResponse:
        """添加里程碑。"""
        project = await self.db.get(Project, project_id)
        if project is None:
            raise NotFoundError("项目", project_id)
        milestone = ProjectMilestone(
            project_id=project_id, name=data.name,
            description=data.description, target_date=data.target_date,
            sort_order=data.sort_order, status="pending",
        )
        self.db.add(milestone)
        await self.db.flush()
        return await self.get_project(project_id)

    async def update_milestone(
        self, project_id: int, milestone_id: int, data: dict,
    ) -> ProjectDetailResponse:
        """更新里程碑。"""
        milestone = await self.db.get(ProjectMilestone, milestone_id)
        if milestone is None or milestone.project_id != project_id:
            raise NotFoundError("里程碑", milestone_id)
        for field, value in data.items():
            if value is not None:
                setattr(milestone, field, value)
        if data.get("status") == "completed":
            milestone.actual_date = date.today()
        await self.db.flush()
        return await self.get_project(project_id)

    # ============================================================
    # 任务
    # ============================================================

    async def add_task(
        self, project_id: int, data: TaskCreateRequest,
    ) -> ProjectDetailResponse:
        """添加任务。"""
        project = await self.db.get(Project, project_id)
        if project is None:
            raise NotFoundError("项目", project_id)
        task = ProjectTask(
            project_id=project_id, name=data.name,
            description=data.description, milestone_id=data.milestone_id,
            assigned_to_id=data.assigned_to_id, priority=data.priority,
            due_date=data.due_date, estimated_hours=data.estimated_hours,
            status="todo",
        )
        self.db.add(task)
        await self.db.flush()

        # Handle dependencies
        if data.depends_on_ids:
            await self.set_task_dependencies(project_id, task.id, data.depends_on_ids)

        return await self.get_project(project_id)

    async def update_task(
        self, project_id: int, task_id: int, data: TaskUpdateRequest,
    ) -> ProjectDetailResponse:
        """更新任务。"""
        task = await self.db.get(ProjectTask, task_id)
        if task is None or task.project_id != project_id:
            raise NotFoundError("任务", task_id)
        if task.is_deleted:
            raise NotFoundError("任务", task_id)

        # Validate status transition
        if data.status and data.status != task.status:
            from app.models.enums import TASK_STATUS_TRANSITIONS, TaskStatus
            current = TaskStatus(task.status)
            allowed = TASK_STATUS_TRANSITIONS.get(current, set())
            try:
                target = TaskStatus(data.status)
            except ValueError:
                raise AppError(f"无效的状态值: {data.status}", code="VALIDATION_ERROR")
            if target not in allowed:
                raise AppError(
                    f"任务状态不能从 '{task.status}' 变更为 '{data.status}'",
                    code="VALIDATION_ERROR",
                )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        if data.status == "done" and not task.completed_date:
            task.completed_date = date.today()
        await self.db.flush()
        return await self.get_project(project_id)

    # ============================================================
    # 成员
    # ============================================================

    async def add_member(
        self, project_id: int, data: MemberAddRequest,
    ) -> ProjectDetailResponse:
        """添加成员。"""
        project = await self.db.get(Project, project_id)
        if project is None:
            raise NotFoundError("项目", project_id)
        # 检查是否已存在
        existing = await self.db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == data.user_id,
            )
        )
        if existing.scalar_one_or_none():
            raise AppError("该用户已是项目成员", code="CONFLICT")
        member = ProjectMember(
            project_id=project_id, user_id=data.user_id, role=data.role,
        )
        self.db.add(member)
        await self.db.flush()
        return await self.get_project(project_id)

    # ============================================================
    # 周报
    # ============================================================

    async def add_update(
        self, project_id: int, data: UpdateCreateRequest, user_id: int,
    ) -> ProjectDetailResponse:
        """提交周报。"""
        project = await self.db.get(Project, project_id)
        if project is None:
            raise NotFoundError("项目", project_id)
        update = ProjectUpdate(
            project_id=project_id, author_id=user_id,
            update_date=data.update_date, progress_pct=data.progress_pct,
            accomplishments=data.accomplishments,
            plan_next_week=data.plan_next_week,
            risks_issues=data.risks_issues,
        )
        self.db.add(update)
        await self.db.flush()
        return await self.get_project(project_id)

    # ============================================================
    # 依赖管理
    # ============================================================

    async def _check_cycle(self, task_id: int, depends_on_ids: list[int]) -> bool:
        """检测循环依赖。使用 DFS 遍历依赖图。"""
        visited = set()
        stack = list(depends_on_ids)

        while stack:
            current_id = stack.pop()
            if current_id == task_id:
                return True  # Cycle found
            if current_id in visited:
                continue
            visited.add(current_id)

            # Load dependencies of current task
            result = await self.db.execute(
                select(ProjectTask).where(ProjectTask.id == current_id)
            )
            task = result.scalar_one_or_none()
            if task:
                dep_result = await self.db.execute(
                    select(task_dependencies.c.depends_on_id).where(
                        task_dependencies.c.task_id == current_id
                    )
                )
                for (dep_id,) in dep_result.all():
                    stack.append(dep_id)

        return False

    async def set_task_dependencies(self, project_id: int, task_id: int, depends_on_ids: list[int]) -> None:
        """设置任务的前置依赖。"""
        task = await self.db.get(ProjectTask, task_id)
        if task is None or task.project_id != project_id:
            raise NotFoundError("任务", task_id)

        # Validate all dependency IDs exist in same project
        for dep_id in depends_on_ids:
            dep_task = await self.db.get(ProjectTask, dep_id)
            if dep_task is None or dep_task.project_id != project_id:
                raise AppError(f"前置任务 {dep_id} 不存在或不属于本项目", code="VALIDATION_ERROR")
            if dep_id == task_id:
                raise AppError("任务不能依赖自身", code="VALIDATION_ERROR")

        # Check for cycles
        if depends_on_ids and await self._check_cycle(task_id, depends_on_ids):
            raise AppError("检测到循环依赖", code="VALIDATION_ERROR")

        # Clear existing dependencies
        await self.db.execute(
            task_dependencies.delete().where(task_dependencies.c.task_id == task_id)
        )

        # Add new dependencies
        for dep_id in depends_on_ids:
            await self.db.execute(
                task_dependencies.insert().values(task_id=task_id, depends_on_id=dep_id)
            )

        await self.db.flush()

    # ============================================================
    # 删除
    # ============================================================

    async def delete_project(self, project_id: int) -> None:
        """软删除项目（必须先取消）。"""
        result = await self.db.execute(
            select(Project)
            .options(
                selectinload(Project.tasks),
                selectinload(Project.milestones),
                selectinload(Project.members),
                selectinload(Project.updates),
            )
            .where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        if project is None:
            raise NotFoundError("项目", project_id)
        if project.status == "active":
            raise AppError("活跃项目不能删除，请先取消项目", code="VALIDATION_ERROR")
        if project.is_deleted:
            raise NotFoundError("项目", project_id)

        now = datetime.now(timezone.utc)
        project.is_deleted = True
        project.deleted_at = now

        # 级联软删除子实体
        for task in (project.tasks or []):
            task.is_deleted = True
            task.deleted_at = now
        for milestone in (project.milestones or []):
            milestone.is_deleted = True
            milestone.deleted_at = now
        for member in (project.members or []):
            member.is_deleted = True
            member.deleted_at = now
        for update in (project.updates or []):
            update.is_deleted = True
            update.deleted_at = now

        await self.db.flush()

    async def delete_task(self, project_id: int, task_id: int) -> None:
        """软删除任务。"""
        task = await self.db.get(ProjectTask, task_id)
        if task is None or task.project_id != project_id:
            raise NotFoundError("任务", task_id)
        task.is_deleted = True
        task.deleted_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def delete_milestone(self, project_id: int, milestone_id: int) -> None:
        """软删除里程碑。"""
        milestone = await self.db.get(ProjectMilestone, milestone_id)
        if milestone is None or milestone.project_id != project_id:
            raise NotFoundError("里程碑", milestone_id)
        milestone.is_deleted = True
        milestone.deleted_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def remove_member(self, project_id: int, user_id: int) -> None:
        """移除项目成员。"""
        result = await self.db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )
        member = result.scalar_one_or_none()
        if member is None:
            raise NotFoundError("项目成员", user_id)
        if member.role == "owner":
            raise AppError("不能移除项目所有者", code="VALIDATION_ERROR")
        member.is_deleted = True
        member.deleted_at = datetime.now(timezone.utc)
        await self.db.flush()

    # ============================================================
    # 统计
    # ============================================================

    async def get_stats(self, factory_id: int) -> ProjectStatsResponse:
        """获取项目统计。"""
        result = await self.db.execute(
            select(Project.status, func.count(Project.id))
            .where(Project.factory_id == factory_id, Project.is_deleted == False)
            .group_by(Project.status)
        )
        status_counts = {row[0]: row[1] for row in result.all()}
        total = sum(status_counts.values())

        budget_result = await self.db.execute(
            select(
                func.sum(Project.budget),
                func.sum(Project.actual_cost),
            ).where(Project.factory_id == factory_id, Project.is_deleted == False)
        )
        row = budget_result.one()

        # Aggregate dimension counts from lean20_dimensions JSON field
        dim_result = await self.db.execute(
            select(Project.lean20_dimensions)
            .where(Project.factory_id == factory_id, Project.is_deleted == False)
        )
        dimension_counts = {"O": 0, "D": 0, "G": 0, "R": 0, "H": 0}
        for (dims,) in dim_result.all():
            if dims:
                for d in dims:
                    if d in dimension_counts:
                        dimension_counts[d] += 1

        return ProjectStatsResponse(
            total=total,
            planning=status_counts.get("planning", 0),
            active=status_counts.get("active", 0),
            on_hold=status_counts.get("on_hold", 0),
            completed=status_counts.get("completed", 0),
            total_budget=float(row[0] or 0),
            total_actual_cost=float(row[1] or 0),
            dimension_counts=dimension_counts,
        )
