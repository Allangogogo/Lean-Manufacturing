"""
5S 审核请求/响应模型
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# 请求模型
# ============================================================

class FiveSAuditCreateRequest(BaseModel):
    """创建 5S 审核计划。"""
    area_id: int = Field(..., description="审核区域 ID")
    audit_type: str = Field(..., description="审核类型: daily/weekly/monthly")
    scheduled_date: date = Field(..., description="计划审核日期")
    auditor_id: Optional[int] = Field(None, description="审核员 ID（默认当前用户）")
    remarks: Optional[str] = Field(None, description="备注")


class FiveSItemScoreRequest(BaseModel):
    """单个审核项评分。"""
    id: int = Field(..., description="审核项 ID")
    score: Decimal = Field(..., ge=0, description="得分")
    remarks: Optional[str] = Field(None, description="备注")
    photo_path: Optional[str] = Field(None, description="照片路径")


class FiveSAuditScoreRequest(BaseModel):
    """保存审核评分。"""
    items: List[FiveSItemScoreRequest] = Field(..., description="审核项评分列表")
    remarks: Optional[str] = Field(None, description="整体备注")


class FiveSImprovementCreateRequest(BaseModel):
    """创建改善项。"""
    item_description: str = Field(..., min_length=1, description="问题描述")
    assigned_to_id: Optional[int] = Field(None, description="负责人 ID")
    due_date: Optional[date] = Field(None, description="截止日期")


class FiveSImprovementUpdateRequest(BaseModel):
    """更新改善项。"""
    status: Optional[str] = Field(None, description="状态: open/in_progress/completed")
    assigned_to_id: Optional[int] = Field(None, description="负责人 ID")
    due_date: Optional[date] = Field(None, description="截止日期")
    evidence_path: Optional[str] = Field(None, description="完成证据路径")
    remarks: Optional[str] = Field(None, description="备注")


# ============================================================
# 响应模型
# ============================================================

class FiveSAreaResponse(BaseModel):
    """区域响应。"""
    id: int
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    responsible_id: Optional[int] = None
    responsible_name: str = ""
    is_active: bool = True


class FiveSItemResponse(BaseModel):
    """审核项响应。"""
    id: int
    s_category: str
    item_name: str
    description: Optional[str] = None
    weight: Decimal = Decimal("1.0")
    score: Optional[Decimal] = None
    max_score: Decimal = Decimal("10.0")
    photo_path: Optional[str] = None
    remarks: Optional[str] = None


class FiveSImprovementResponse(BaseModel):
    """改善项响应。"""
    id: int
    audit_id: int
    item_description: str
    assigned_to_id: Optional[int] = None
    assigned_to_name: str = ""
    status: str = "open"
    due_date: Optional[date] = None
    completed_date: Optional[date] = None
    evidence_path: Optional[str] = None
    verified_by_id: Optional[int] = None
    verified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class FiveSAuditDetailResponse(BaseModel):
    """审核详情响应。"""
    id: int
    area_id: int
    area_name: str = ""
    factory_id: int
    auditor_id: int
    auditor_name: str = ""
    audit_type: str
    score: Optional[Decimal] = None
    max_score: Decimal = Decimal("100")
    status: str
    scheduled_date: date
    completed_date: Optional[date] = None
    remarks: Optional[str] = None
    created_at: Optional[datetime] = None
    items: List[FiveSItemResponse] = []
    improvements: List[FiveSImprovementResponse] = []


class FiveSAuditListItem(BaseModel):
    """审核列表项。"""
    id: int
    area_name: str = ""
    auditor_name: str = ""
    audit_type: str
    score: Optional[Decimal] = None
    max_score: Decimal = Decimal("100")
    status: str
    scheduled_date: date
    completed_date: Optional[date] = None
    improvement_count: int = 0


class FiveSAuditStatsResponse(BaseModel):
    """审核统计。"""
    total: int = 0
    scheduled: int = 0
    in_progress: int = 0
    completed: int = 0
    avg_score: float = 0.0
    open_improvements: int = 0
