"""
项目管理 API 接口

- GET    /projects                 — 项目列表
- POST   /projects                 — 创建项目
- GET    /projects/{id}            — 项目详情
- PUT    /projects/{id}            — 更新项目
- DELETE /projects/{id}            — 删除项目
- POST   /projects/{id}/milestones — 添加里程碑
- PUT    /projects/{id}/milestones/{mid} — 更新里程碑
- DELETE /projects/{id}/milestones/{mid} — 删除里程碑
- POST   /projects/{id}/tasks      — 添加任务
- PUT    /projects/{id}/tasks/{tid} — 更新任务
- DELETE /projects/{id}/tasks/{tid} — 删除任务
- POST   /projects/{id}/members    — 添加成员
- DELETE /projects/{id}/members/{uid} — 移除成员
- POST   /projects/{id}/updates    — 提交周报
- GET    /projects/stats           — 统计数据
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user
from app.schemas.project import (
    MemberAddRequest,
    MilestoneCreateRequest,
    MilestoneUpdateRequest,
    ProjectCreateRequest,
    ProjectUpdateRequest,
    TaskCreateRequest,
    TaskUpdateRequest,
    UpdateCreateRequest,
)
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("")
async def list_projects(
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return await service.list_projects(
        factory_id=user.factory_id, status=status, page=page, page_size=page_size,
    )


@router.post("")
async def create_project(
    body: ProjectCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    result = await service.create_project(data=body, user_id=user.id, factory_id=user.factory_id)
    return {"success": True, "data": result.model_dump()}


@router.get("/stats")
async def project_stats(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return (await service.get_stats(user.factory_id)).model_dump()


@router.get("/{project_id}")
async def get_project(
    project_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    result = await service.get_project(project_id)
    return {"success": True, "data": result.model_dump()}


@router.put("/{project_id}")
async def update_project(
    project_id: int, body: ProjectUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    result = await service.update_project(project_id=project_id, data=body, user_id=user.id)
    return {"success": True, "data": result.model_dump()}


@router.post("/{project_id}/milestones")
async def add_milestone(
    project_id: int, body: MilestoneCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    result = await service.add_milestone(project_id=project_id, data=body)
    return {"success": True, "data": result.model_dump()}


@router.put("/{project_id}/milestones/{milestone_id}")
async def update_milestone(
    project_id: int, milestone_id: int, body: MilestoneUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    result = await service.update_milestone(
        project_id=project_id, milestone_id=milestone_id,
        data=body.model_dump(exclude_unset=True),
    )
    return {"success": True, "data": result.model_dump()}


@router.post("/{project_id}/tasks")
async def add_task(
    project_id: int, body: TaskCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    result = await service.add_task(project_id=project_id, data=body)
    return {"success": True, "data": result.model_dump()}


@router.put("/{project_id}/tasks/{task_id}")
async def update_task(
    project_id: int, task_id: int, body: TaskUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    result = await service.update_task(project_id=project_id, task_id=task_id, data=body)
    return {"success": True, "data": result.model_dump()}


@router.put("/{project_id}/tasks/{task_id}/dependencies")
async def set_task_dependencies(
    project_id: int, task_id: int, body: TaskUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    depends_on_ids = body.depends_on_ids if body.depends_on_ids is not None else []
    await service.set_task_dependencies(project_id, task_id, depends_on_ids)
    return {"success": True, "message": "依赖关系已更新"}


@router.post("/{project_id}/members")
async def add_member(
    project_id: int, body: MemberAddRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    result = await service.add_member(project_id=project_id, data=body)
    return {"success": True, "data": result.model_dump()}


@router.post("/{project_id}/updates")
async def add_update(
    project_id: int, body: UpdateCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    result = await service.add_update(project_id=project_id, data=body, user_id=user.id)
    return {"success": True, "data": result.model_dump()}


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    await service.delete_project(project_id)
    return {"success": True, "message": "项目已删除"}


@router.delete("/{project_id}/tasks/{task_id}")
async def delete_task(
    project_id: int, task_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    await service.delete_task(project_id, task_id)
    return {"success": True, "message": "任务已删除"}


@router.delete("/{project_id}/milestones/{milestone_id}")
async def delete_milestone(
    project_id: int, milestone_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    await service.delete_milestone(project_id, milestone_id)
    return {"success": True, "message": "里程碑已删除"}


@router.delete("/{project_id}/members/{user_id}")
async def remove_member(
    project_id: int, user_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    await service.remove_member(project_id, user_id)
    return {"success": True, "message": "成员已移除"}
