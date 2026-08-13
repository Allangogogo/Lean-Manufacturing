"""
Best Practice 管理请求/响应模型
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# 请求模型
# ============================================================

class PracticeCreateRequest(BaseModel):
    """提交最佳实践。"""
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    description: str = Field(..., min_length=1, description="详细描述")
    category: str = Field(..., description="类别: tool/method/mindset/process")
    subcategory: str = Field(..., description="子类别: kanban/5s/smed/poka_yoke/vsm/tpm/kaizen/etc.")
    problem_statement: Optional[str] = Field(None, description="问题描述")
    root_cause: Optional[str] = Field(None, description="根本原因")
    solution: str = Field(..., min_length=1, description="解决方案")
    results: Optional[str] = Field(None, description="实施效果")
    applicable_areas: Optional[str] = Field(None, description="适用领域 (JSON)")
    estimated_saving: Optional[Decimal] = Field(None, description="预估节省 (万元)")
    actual_saving: Optional[Decimal] = Field(None, description="实际节省 (万元)")
    difficulty_level: str = Field("medium", description="难度: easy/medium/hard")
    implementation_time_days: Optional[int] = Field(None, description="实施天数")
    tags: Optional[str] = Field(None, description="标签 (JSON)")


class PracticeUpdateRequest(BaseModel):
    """更新最佳实践。"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    problem_statement: Optional[str] = None
    root_cause: Optional[str] = None
    solution: Optional[str] = None
    results: Optional[str] = None
    applicable_areas: Optional[str] = None
    estimated_saving: Optional[Decimal] = None
    actual_saving: Optional[Decimal] = None
    difficulty_level: Optional[str] = None
    implementation_time_days: Optional[int] = None
    tags: Optional[str] = None


class VoteRequest(BaseModel):
    """点赞/收藏。"""
    vote_type: str = Field(..., description="like/bookmark")


class CommentCreateRequest(BaseModel):
    """添加评论。"""
    comment: str = Field(..., min_length=1, description="评论内容")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分 1-5")


# ============================================================
# 响应模型
# ============================================================

class CommentResponse(BaseModel):
    """评论响应。"""
    id: int
    user_name: str = ""
    comment: str
    rating: Optional[int] = None
    created_at: Optional[datetime] = None


class PracticeDetailResponse(BaseModel):
    """最佳实践详情。"""
    id: int
    title: str
    description: str
    category: str
    subcategory: str
    author_name: str = ""
    status: str
    problem_statement: Optional[str] = None
    root_cause: Optional[str] = None
    solution: str
    results: Optional[str] = None
    applicable_areas: Optional[str] = None
    estimated_saving: Optional[Decimal] = None
    actual_saving: Optional[Decimal] = None
    difficulty_level: str = "medium"
    implementation_time_days: Optional[int] = None
    tags: Optional[str] = None
    view_count: int = 0
    usage_count: int = 0
    like_count: int = 0
    bookmark_count: int = 0
    user_liked: bool = False
    user_bookmarked: bool = False
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    comments: List[CommentResponse] = []


class PracticeListItem(BaseModel):
    """最佳实践列表项。"""
    id: int
    title: str
    category: str
    subcategory: str
    author_name: str = ""
    status: str
    difficulty_level: str = "medium"
    estimated_saving: Optional[Decimal] = None
    view_count: int = 0
    usage_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    tags: Optional[str] = None
    created_at: Optional[datetime] = None


class PracticeStatsResponse(BaseModel):
    """最佳实践统计。"""
    total: int = 0
    published: int = 0
    draft: int = 0
    total_views: int = 0
    total_likes: int = 0
    total_savings: float = 0.0
