"""
培训管理请求/响应模型
"""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# 请求模型
# ============================================================

class TrainingSessionCreateRequest(BaseModel):
    """创建培训场次。"""
    title: str = Field(..., min_length=1, max_length=200, description="培训标题")
    description: Optional[str] = Field(None, description="培训描述")
    training_type: str = Field(..., description="类型: lean_tool/safety/quality/other")
    level: str = Field(..., description="级别: L1_basics/L2_intermediate/L3_advanced/L4_expert")
    scheduled_date: date = Field(..., description="计划日期")
    start_time: Optional[time] = Field(None, description="开始时间")
    end_time: Optional[time] = Field(None, description="结束时间")
    duration_hours: Decimal = Field(Decimal("1.0"), description="时长（小时）")
    location: Optional[str] = Field(None, description="培训地点")
    max_participants: int = Field(30, description="最大参与人数")
    pass_score: Decimal = Field(Decimal("60.0"), description="及格分数")


class TrainingSessionUpdateRequest(BaseModel):
    """更新培训场次。"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    training_type: Optional[str] = None
    level: Optional[str] = None
    scheduled_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration_hours: Optional[Decimal] = None
    location: Optional[str] = None
    max_participants: Optional[int] = None
    pass_score: Optional[Decimal] = None
    status: Optional[str] = None


class EnrollmentActionRequest(BaseModel):
    """报名/签到/评分操作。"""
    action: str = Field(..., description="操作: enroll/attend/cancel")
    score: Optional[Decimal] = Field(None, description="成绩（签到时可选）")
    feedback_rating: Optional[int] = Field(None, ge=1, le=5, description="反馈评分")
    feedback_comment: Optional[str] = Field(None, description="反馈评论")


# ============================================================
# 响应模型
# ============================================================

class TrainingMaterialResponse(BaseModel):
    """培训材料响应。"""
    id: int
    material_name: str
    material_type: str
    filepath: str
    filesize: Optional[int] = None
    uploaded_by: int
    created_at: Optional[datetime] = None


class EnrollmentResponse(BaseModel):
    """报名响应。"""
    id: int
    session_id: int
    user_id: int
    user_name: str = ""
    status: str
    score: Optional[Decimal] = None
    feedback_rating: Optional[int] = None
    enrolled_at: Optional[datetime] = None
    attended_at: Optional[datetime] = None
    certified_at: Optional[datetime] = None


class TrainingSessionDetailResponse(BaseModel):
    """培训详情响应。"""
    id: int
    title: str
    description: Optional[str] = None
    trainer_id: int
    trainer_name: str = ""
    factory_id: int
    training_type: str
    level: str
    scheduled_date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration_hours: Decimal = Decimal("1.0")
    location: Optional[str] = None
    max_participants: int = 30
    status: str
    pass_score: Decimal = Decimal("60.0")
    enrolled_count: int = 0
    created_at: Optional[datetime] = None
    enrollments: List[EnrollmentResponse] = []
    materials: List[TrainingMaterialResponse] = []


class TrainingSessionListItem(BaseModel):
    """培训列表项。"""
    id: int
    title: str
    trainer_name: str = ""
    training_type: str
    level: str
    scheduled_date: date
    duration_hours: Decimal = Decimal("1.0")
    location: Optional[str] = None
    status: str
    enrolled_count: int = 0
    max_participants: int = 30


class TrainingStatsResponse(BaseModel):
    """培训统计。"""
    total: int = 0
    scheduled: int = 0
    in_progress: int = 0
    completed: int = 0
    total_enrollments: int = 0
    avg_score: float = 0.0
    certification_rate: float = 0.0
