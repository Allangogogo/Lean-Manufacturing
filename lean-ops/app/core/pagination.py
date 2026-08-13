"""
通用分页模块

职责：
1. 定义分页请求/响应模型
2. 提供通用分页查询工具函数
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, List, Optional, Sequence, TypeVar

from pydantic import BaseModel, Field
from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


# ============================================================
# 请求模型
# ============================================================

class PaginationParams(BaseModel):
    """分页请求参数。"""
    page: int = Field(1, ge=1, description="页码，从 1 开始")
    page_size: int = Field(20, ge=1, le=100, description="每页条数，最大 100")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


# ============================================================
# 响应模型
# ============================================================

class PaginatedResponse(BaseModel):
    """通用分页响应。"""
    success: bool = True
    data: List[Any] = []
    pagination: dict = Field(default_factory=dict)

    @classmethod
    def create(
        cls,
        items: Sequence[Any],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse":
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            success=True,
            data=list(items),
            pagination={
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        )


# ============================================================
# 工具函数
# ============================================================

async def paginate(
    db: AsyncSession,
    query: Select,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse:
    """
    通用分页查询。

    Args:
        db: 数据库 Session
        query: SQLAlchemy Select 查询（不含 LIMIT/OFFSET）
        page: 页码
        page_size: 每页条数

    Returns:
        PaginatedResponse 分页结果
    """
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页查询
    offset = (page - 1) * page_size
    paginated_query = query.offset(offset).limit(page_size)
    result = await db.execute(paginated_query)
    items = result.scalars().all()

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


def get_pagination_params(
    page: int = 1,
    page_size: int = 20,
) -> PaginationParams:
    """构建分页参数（自动限制范围）。"""
    return PaginationParams(
        page=max(1, page),
        page_size=min(100, max(1, page_size)),
    )
