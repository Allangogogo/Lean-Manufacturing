"""
RBAC 权限检查模块

职责：
1. 从 Token 提取当前用户
2. 查询用户的工厂、角色、权限
3. 提供权限检查函数和 FastAPI 依赖注入
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional, Set, Tuple

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.core.security import decode_access_token

settings = get_settings()


# ============================================================
# 数据结构
# ============================================================

@dataclass
class CurrentUser:
    """当前登录用户上下文。"""
    id: int
    username: str
    display_name: str
    factory_id: int           # 当前工厂 ID
    factory_name: str
    department_id: Optional[int]
    role_code: str            # 当前工厂下的角色编码
    role_id: int
    permissions: Set[Tuple[str, str, str]]  # {(resource, action, scope), ...}


# ============================================================
# 依赖注入
# ============================================================

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    """
    FastAPI 依赖注入：从 Cookie/Authorization 获取当前用户。

    支持两种方式：
    - Cookie: leanops_token=<jwt>
    - Header: Authorization: Bearer <jwt>
    """
    from app.models.user import User, UserFactoryRole, Role, Permission, Factory  # noqa: F811

    # 提取 Token
    token = None

    # 优先从 Cookie 获取
    cookie_token = request.cookies.get("leanops_token")
    if cookie_token:
        token = cookie_token

    # 其次从 Authorization Header 获取
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录，请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 解码 Token
    from app.core.security import get_user_id_from_token
    user_id = get_user_id_from_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期，请重新登录",
        )

    # 查询用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已禁用",
        )

    # 查询用户在当前工厂的角色和权限
    # 从 Cookie 或 Header 中提取 factory_id（默认用用户默认工厂）
    factory_id = request.cookies.get("leanops_factory_id")
    if factory_id:
        try:
            factory_id = int(factory_id)
        except (ValueError, TypeError):
            factory_id = user.default_factory_id
    else:
        factory_id = user.default_factory_id

    # 查询用户工厂角色关联
    ufr_result = await db.execute(
        select(UserFactoryRole, Role, Factory)
        .join(Role, UserFactoryRole.role_id == Role.id)
        .join(Factory, UserFactoryRole.factory_id == Factory.id)
        .where(
            UserFactoryRole.user_id == user_id,
            UserFactoryRole.factory_id == factory_id,
        )
    )
    ufr_row = ufr_result.first()
    if ufr_row is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"用户在工厂 {factory_id} 无角色分配",
        )

    ufr, role, factory = ufr_row

    # 查询权限
    perm_result = await db.execute(
        select(Permission).where(Permission.role_id == role.id)
    )
    permissions = set()
    for perm in perm_result.scalars().all():
        permissions.add((perm.resource, perm.action, perm.scope))

    return CurrentUser(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        factory_id=factory.id,
        factory_name=factory.name,
        department_id=ufr.department_id,
        role_code=role.code,
        role_id=role.id,
        permissions=permissions,
    )


def require_permission(resource: str, action: str, scope: str = "all"):
    """
    权限检查装饰器（作为 FastAPI Depends 使用）。

    用法:
        @router.get("/kaizen")
        async def list_kaizen(
            user: CurrentUser = Depends(require_permission("kaizen", "read")),
        ):
            ...
    """
    async def _check(user: CurrentUser = Depends(get_current_user)):
        # admin 角色拥有所有权限
        if user.role_code == "admin":
            return user

        # 检查权限
        has_perm = False
        for r, a, s in user.permissions:
            if r == resource and a == action:
                # scope 匹配：all > factory > dept > own
                if s == "all" or s == scope or scope in ("dept", "own") and s in ("factory", "dept"):
                    has_perm = True
                    break
                if s == "factory" and scope in ("dept", "own"):
                    has_perm = True
                    break
                if s == "dept" and scope == "own":
                    has_perm = True
                    break

        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"无权限执行此操作: {resource}.{action}",
            )

        return user

    return _check


def require_role(*role_codes: str):
    """
    角色检查装饰器。

    用法:
        @router.post("/kaizen")
        async def create_kaizen(
            user: CurrentUser = Depends(require_role("lean_mgr", "supervisor")),
        ):
            ...
    """
    async def _check(user: CurrentUser = Depends(get_current_user)):
        if user.role_code == "admin":
            return user
        if user.role_code not in role_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要角色: {', '.join(role_codes)}",
            )
        return user

    return _check
