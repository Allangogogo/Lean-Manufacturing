"""
改善提案请求/响应模型
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# 请求模型
# ============================================================

class KaizenCreateRequest(BaseModel):
    """创建改善提案。"""
    title: str = Field(..., min_length=1, max_length=200, description="提案标题")
    description: str = Field(..., min_length=1, description="问题描述")
    category: str = Field(..., description="分类: quality/cost/delivery/safety/morale/environment")
    priority: str = Field("medium", description="优先级: low/medium/high/urgent")
    expected_benefit: Optional[str] = Field(None, description="预期收益描述")
    expected_saving: Optional[Decimal] = Field(None, description="预期节约金额（元）")
    root_cause: Optional[str] = Field(None, description="根因分析")
    solution: Optional[str] = Field(None, description="解决方案")
    implementation_plan: Optional[str] = Field(None, description="实施计划")
    due_date: Optional[date] = Field(None, description="截止日期")


class KaizenUpdateRequest(BaseModel):
    """更新改善提案。"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = None
    priority: Optional[str] = None
    expected_benefit: Optional[str] = None
    expected_saving: Optional[Decimal] = None
    root_cause: Optional[str] = None
    solution: Optional[str] = None
    implementation_plan: Optional[str] = None
    actual_benefit: Optional[str] = None
    actual_saving: Optional[Decimal] = None
    result: Optional[str] = None
    due_date: Optional[date] = None


class KaizenActionRequest(BaseModel):
    """审批操作。"""
    action: str = Field(..., description="操作: submit/approve/reject/return/start/complete/close")
    comment: Optional[str] = Field(None, description="审批意见")


class KaizenCommentRequest(BaseModel):
    """添加评论。"""
    comment: str = Field(..., min_length=1, description="评论内容")


# ============================================================
# 响应模型
# ============================================================

class KaizenCommentResponse(BaseModel):
    """评论响应。"""
    id: int
    user_id: int
    user_name: str = ""
    action: str
    comment: Optional[str] = None
    created_at: Optional[datetime] = None


class KaizenAttachmentResponse(BaseModel):
    """附件响应。"""
    id: int
    filename: str
    filepath: str
    filesize: Optional[int] = None
    uploaded_by: int
    created_at: Optional[datetime] = None


class KaizenWorkflowLog(BaseModel):
    """工作流日志。"""
    from_state: Optional[str] = None
    to_state: str
    action: str
    operator_id: int
    operator_name: str = ""
    comment: Optional[str] = None
    created_at: Optional[str] = None


class KaizenDetailResponse(BaseModel):
    """提案详情响应。"""
    id: int
    title: str
    description: str
    category: str
    priority: str
    status: str
    submitter_id: int
    submitter_name: str = ""
    factory_id: int
    department_id: Optional[int] = None
    expected_benefit: Optional[str] = None
    expected_saving: Optional[Decimal] = None
    actual_benefit: Optional[str] = None
    actual_saving: Optional[Decimal] = None
    root_cause: Optional[str] = None
    solution: Optional[str] = None
    implementation_plan: Optional[str] = None
    result: Optional[str] = None
    due_date: Optional[date] = None
    closed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    allowed_actions: List[str] = []
    comments: List[KaizenCommentResponse] = []
    attachments: List[KaizenAttachmentResponse] = []
    workflow_history: List[KaizenWorkflowLog] = []


class KaizenListItem(BaseModel):
    """提案列表项。"""
    id: int
    title: str
    category: str
    priority: str
    status: str
    submitter_name: str = ""
    expected_saving: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    due_date: Optional[date] = None


class KaizenStatsResponse(BaseModel):
    """提案统计。"""
    total: int = 0
    draft: int = 0
    submitted: int = 0
    reviewing: int = 0
    approved: int = 0
    implementing: int = 0
    verified: int = 0
    closed: int = 0
    total_saving: float = 0.0
