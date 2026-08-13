"""
认证接口

- POST /auth/login  — 登录（返回 JWT Token）
- POST /auth/logout — 登出
- GET  /auth/me     — 获取当前用户信息
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.core.security import (
    create_access_token,
    get_user_id_from_token,
    verify_password,
)
from app.core.permissions import CurrentUser, get_current_user
from app.models.user import Factory, Role, User, UserFactoryRole

router = APIRouter()
settings = get_settings()


# ============================================================
# 请求/响应模型
# ============================================================

class LoginRequest(BaseModel):
    username: str
    password: str
    factory_id: int | None = None  # 指定工厂（可选）


class LoginResponse(BaseModel):
    success: bool = True
    token: str
    user: dict
    factory: dict


class UserInfo(BaseModel):
    id: int
    username: str
    display_name: str
    email: str | None = None
    phone: str | None = None
    factory_id: int
    factory_name: str
    role_code: str
    role_name: str
    department_id: int | None = None


# ============================================================
# 接口
# ============================================================

@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """用户登录。"""
    # 查询用户
    result = await db.execute(
        select(User).where(User.username == body.username)
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已禁用",
        )

    # 确定工厂
    factory_id = body.factory_id or user.default_factory_id
    if factory_id is None:
        # 查询用户所属的第一个工厂
        ufr_result = await db.execute(
            select(UserFactoryRole)
            .where(UserFactoryRole.user_id == user.id)
            .limit(1)
        )
        ufr = ufr_result.scalar_one_or_none()
        if ufr is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户未分配任何工厂",
            )
        factory_id = ufr.factory_id

    # 查询工厂角色
    ufr_result = await db.execute(
        select(UserFactoryRole, Role, Factory)
        .join(Role, UserFactoryRole.role_id == Role.id)
        .join(Factory, UserFactoryRole.factory_id == Factory.id)
        .where(
            UserFactoryRole.user_id == user.id,
            UserFactoryRole.factory_id == factory_id,
        )
    )
    ufr_row = ufr_result.first()
    if ufr_row is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户在该工厂无角色",
        )

    ufr, role, factory = ufr_row

    # 签发 Token
    token = create_access_token(data={"sub": str(user.id)})

    # 更新最后登录时间
    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    # 设置 Cookie
    response.set_cookie(
        key="leanops_token",
        value=token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="leanops_factory_id",
        value=str(factory_id),
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return LoginResponse(
        token=token,
        user={
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "email": user.email,
            "role_code": role.code,
            "role_name": role.name,
        },
        factory={
            "id": factory.id,
            "name": factory.name,
            "code": factory.code,
        },
    )


@router.post("/logout")
async def logout(response: Response):
    """用户登出。"""
    response.delete_cookie("leanops_token")
    response.delete_cookie("leanops_factory_id")
    return {"success": True, "message": "已登出"}


@router.get("/me", response_model=UserInfo)
async def get_me(user: CurrentUser = Depends(get_current_user)):
    """获取当前用户信息。"""
    return UserInfo(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        factory_id=user.factory_id,
        factory_name=user.factory_name,
        role_code=user.role_code,
        role_name=user.role_code,  # 后续可查 Role 表获取中文名
        department_id=user.department_id,
    )
