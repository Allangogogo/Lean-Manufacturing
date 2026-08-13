"""
成熟度评估请求/响应模型
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# 请求模型
# ============================================================

class AssessmentCreateRequest(BaseModel):
    """创建评估。"""
    assessment_type: str = Field(..., description="overall/process/department")
    area_name: str = Field(..., min_length=1, max_length=100, description="评估区域")
    assessment_date: Optional[date] = Field(None, description="评估日期")
    max_score: Decimal = Field(Decimal("100"), description="满分")


class CriterionScoreRequest(BaseModel):
    """细项评分。"""
    criterion_id: int
    score: Decimal = Field(..., ge=0, description="得分")
    level: Optional[str] = Field(None, description="等级 L1-L5")
    evidence: Optional[str] = Field(None, description="证据")
    remarks: Optional[str] = Field(None, description="备注")
    improvement_suggestion: Optional[str] = Field(None, description="改善建议")


class DimensionScoreRequest(BaseModel):
    """维度评分。"""
    dimension_id: int
    score: Optional[Decimal] = Field(None, ge=0, description="得分（如直接给维度评分）")
    level: Optional[str] = Field(None, description="等级")
    findings: Optional[str] = Field(None, description="发现")
    action_items: Optional[str] = Field(None, description="行动项")
    criteria_scores: Optional[List[CriterionScoreRequest]] = Field(None, description="细项评分")


class AssessmentCompleteRequest(BaseModel):
    """完成评估。"""
    summary: Optional[str] = Field(None, description="总结")
    recommendations: Optional[str] = Field(None, description="建议")


# ============================================================
# 响应模型
# ============================================================

class CriterionResponse(BaseModel):
    """细项响应。"""
    id: int
    criterion_name: str
    description: Optional[str] = None
    weight: Decimal
    score: Optional[Decimal] = None
    max_score: Decimal
    level: Optional[str] = None
    evidence: Optional[str] = None
    remarks: Optional[str] = None
    improvement_suggestion: Optional[str] = None


class DimensionResponse(BaseModel):
    """维度响应。"""
    id: int
    dimension_name: str
    weight: Decimal
    score: Optional[Decimal] = None
    max_score: Decimal
    level: Optional[str] = None
    findings: Optional[str] = None
    action_items: Optional[str] = None
    criteria: List[CriterionResponse] = []


class AssessmentDetailResponse(BaseModel):
    """评估详情。"""
    id: int
    assessment_type: str
    area_name: str
    assessor_name: str = ""
    assessment_date: Optional[date] = None
    overall_level: Optional[str] = None
    total_score: Optional[Decimal] = None
    max_score: Decimal
    status: str
    summary: Optional[str] = None
    recommendations: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    dimensions: List[DimensionResponse] = []


class AssessmentListItem(BaseModel):
    """评估列表项。"""
    id: int
    assessment_type: str
    area_name: str
    assessor_name: str = ""
    overall_level: Optional[str] = None
    total_score: Optional[Decimal] = None
    max_score: Decimal
    status: str
    assessment_date: Optional[date] = None
    created_at: Optional[datetime] = None


class MaturityStatsResponse(BaseModel):
    """成熟度统计。"""
    total: int = 0
    completed: int = 0
    in_progress: int = 0
    draft: int = 0
    avg_score: float = 0.0


class TrendResponse(BaseModel):
    """历史趋势。"""
    assessment_id: int
    area_name: str
    assessment_date: Optional[date] = None
    total_score: Optional[Decimal] = None
    overall_level: Optional[str] = None
