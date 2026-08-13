"""
系统管理 API 接口

- GET    /admin/users          — 用户列表
- POST   /admin/users          — 创建用户
- PUT    /admin/users/{id}     — 更新用户
- POST   /admin/users/{id}/reset-password — 重置密码
- GET    /admin/roles          — 角色列表
- GET    /admin/departments    — 部门列表
- GET    /admin/stats          — 系统统计
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user
from app.schemas.admin import (
    PasswordResetRequest,
    UserCreateRequest,
    UserUpdateRequest,
)
from app.services.admin_service import AdminService

router = APIRouter()


@router.get("/users")
async def list_users(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    role_code: Optional[str] = Query(None, description="角色筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    return await service.list_users(
        factory_id=user.factory_id, keyword=keyword,
        role_code=role_code, page=page, page_size=page_size,
    )


@router.post("/users")
async def create_user(
    body: UserCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    result = await service.create_user(data=body, factory_id=user.factory_id)
    return {"success": True, "data": result.model_dump()}


@router.put("/users/{user_id}")
async def update_user(
    user_id: int, body: UserUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    result = await service.update_user(
        user_id=user_id, data=body, factory_id=user.factory_id,
    )
    return {"success": True, "data": result.model_dump()}


@router.post("/users/{user_id}/reset-password")
async def reset_password(
    user_id: int, body: PasswordResetRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    await service.reset_password(user_id=user_id, data=body)
    return {"success": True, "message": "密码已重置"}


@router.get("/roles")
async def list_roles(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    result = await service.list_roles()
    return [r.model_dump() for r in result]


@router.get("/departments")
async def list_departments(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    return await service.list_departments(user.factory_id)


@router.get("/stats")
async def system_stats(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    return (await service.get_stats(user.factory_id)).model_dump()
