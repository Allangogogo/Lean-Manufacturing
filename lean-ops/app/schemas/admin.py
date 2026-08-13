"""
系统管理请求/响应模型
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# 请求模型
# ============================================================

class UserCreateRequest(BaseModel):
    """创建用户。"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")
    display_name: str = Field(..., min_length=1, max_length=100, description="显示名称")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="电话")
    role_code: str = Field("worker", description="角色代码: lean_mgr/worker/supervisor/manager")
    department_id: Optional[int] = Field(None, description="部门 ID")


class UserUpdateRequest(BaseModel):
    """更新用户。"""
    display_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    role_code: Optional[str] = None
    department_id: Optional[int] = None


class PasswordResetRequest(BaseModel):
    """重置密码。"""
    new_password: str = Field(..., min_length=6, description="新密码")


# ============================================================
# 响应模型
# ============================================================

class RoleResponse(BaseModel):
    """角色响应。"""
    id: int
    name: str
    code: str
    description: Optional[str] = None


class UserListItem(BaseModel):
    """用户列表项。"""
    id: int
    username: str
    display_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role_name: str = ""
    role_code: str = ""
    department_name: str = ""
    is_active: bool = True
    last_login_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class AdminStatsResponse(BaseModel):
    """系统统计。"""
    total_users: int = 0
    active_users: int = 0
    total_proposals: int = 0
    total_audits: int = 0
    total_training: int = 0
    total_equipment: int = 0
    total_projects: int = 0
    total_practices: int = 0
