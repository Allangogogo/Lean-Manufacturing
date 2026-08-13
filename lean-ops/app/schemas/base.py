"""
通用响应模型

统一 API 响应格式：
{
    "success": true/false,
    "data": ...,
    "error": {"code": "...", "message": "..."},
    "pagination": {...}
}
"""

from __future__ import annotations

from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel):
    """成功响应。"""
    success: bool = True
    data: Any = None
    message: str = "操作成功"


class ErrorResponse(BaseModel):
    """错误响应。"""
    success: bool = False
    error: dict = Field(default_factory=lambda: {"code": "ERROR", "message": "操作失败"})


class PaginatedData(BaseModel):
    """分页数据。"""
    items: List[Any] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False


class LoginRequest(BaseModel):
    """登录请求。"""
    username: str
    password: str
    factory_id: Optional[int] = None  # 指定工厂（可选）


class LoginResponse(BaseModel):
    """登录响应。"""
    success: bool = True
    token: str
    user: dict
    factory: dict
