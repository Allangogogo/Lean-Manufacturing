"""
用户与组织模型

包含：工厂、部门、角色、权限、用户、用户-工厂-角色关联
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


# ============================================================
# 工厂
# ============================================================

class Factory(Base, TimestampMixin):
    """工厂表。"""

    __tablename__ = "factories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text)
    contact: Mapped[Optional[str]] = mapped_column(String(50))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 关系
    departments: Mapped[list["Department"]] = relationship(back_populates="factory")
    users: Mapped[list["UserFactoryRole"]] = relationship(back_populates="factory")


# ============================================================
# 部门
# ============================================================

class Department(Base, TimestampMixin):
    """部门表（支持多级）。"""

    __tablename__ = "departments"
    __table_args__ = (
        UniqueConstraint("factory_id", "code", name="uq_dept_factory_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id"), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 关系
    factory: Mapped["Factory"] = relationship(back_populates="departments")
    parent: Mapped[Optional["Department"]] = relationship(remote_side="Department.id")
    children: Mapped[list["Department"]] = relationship(back_populates="parent")


# ============================================================
# 角色
# ============================================================

class Role(Base):
    """角色表。"""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # 关系
    permissions: Mapped[list["Permission"]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )
    user_factory_roles: Mapped[list["UserFactoryRole"]] = relationship(
        back_populates="role"
    )


# ============================================================
# 权限
# ============================================================

class Permission(Base):
    """RBAC 权限表。"""

    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "resource", "action", name="uq_perm_role_res_act"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )
    resource: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    scope: Mapped[str] = mapped_column(String(20), default="own", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # 关系
    role: Mapped["Role"] = relationship(back_populates="permissions")


# ============================================================
# 用户
# ============================================================

class User(Base, TimestampMixin):
    """用户表。"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    avatar: Mapped[Optional[str]] = mapped_column(String(255))
    default_factory_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("factories.id")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 关系
    factory_roles: Mapped[list["UserFactoryRole"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


# ============================================================
# 用户-工厂-角色 关联
# ============================================================

class UserFactoryRole(Base):
    """用户在工厂的角色关联表（多工厂多角色）。"""

    __tablename__ = "user_factory_roles"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "factory_id", "role_id", name="uq_ufr_user_factory_role"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    factory_id: Mapped[int] = mapped_column(
        ForeignKey("factories.id"), nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"), nullable=False
    )
    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id")
    )
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # 关系
    user: Mapped["User"] = relationship(back_populates="factory_roles")
    factory: Mapped["Factory"] = relationship(back_populates="users")
    role: Mapped["Role"] = relationship(back_populates="user_factory_roles")
