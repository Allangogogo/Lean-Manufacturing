"""
WIP 在制品管理 请求/响应模型
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# 请求模型
# ============================================================

class ProductionOrderCreateRequest(BaseModel):
    """创建生产工单。"""
    order_no: str = Field(..., min_length=1, max_length=30, description="工单号")
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    product_code: Optional[str] = Field(None, max_length=50, description="产品编码")
    quantity: int = Field(..., gt=0, description="计划数量")
    priority: str = Field("normal", description="优先级: high/medium/low")
    planned_start: Optional[date] = Field(None, description="计划开始")
    planned_end: Optional[date] = Field(None, description="计划结束")


class OperationMoveRequest(BaseModel):
    """工序流转登记。"""
    quantity: int = Field(..., gt=0, description="流转数量")
    move_type: str = Field("move_in", description="move_in(投入)/move_out(产出)")


# ============================================================
# 响应模型
# ============================================================

class ProductionOrderResponse(BaseModel):
    """工单响应。"""
    id: int
    order_no: str
    product_name: str
    product_code: Optional[str] = None
    quantity: int
    priority: str
    status: str
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OperationResponse(BaseModel):
    """工序响应。"""
    id: int
    order_id: int
    sequence_no: int
    operation_name: str
    equipment_id: Optional[int] = None
    input_qty: int
    output_qty: int
    wip_qty: int
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OrderDetailResponse(BaseModel):
    """工单详情（含工序）。"""
    order: ProductionOrderResponse
    operations: List[OperationResponse] = []


class OperationWIPResponse(BaseModel):
    """工序 WIP 水位。"""
    operation_name: str
    sequence_no: int
    wip_qty: int
    throughput: int
    status: str
    is_bottleneck: bool = False


class WIPOverviewResponse(BaseModel):
    """全局指标。"""
    total_wip: int
    active_orders: int
    today_throughput: int
    avg_lead_time_days: float
    bottleneck: Optional[OperationWIPResponse] = None


class WIPTrendPoint(BaseModel):
    """趋势点。"""
    date: str
    total_wip: int
    target_wip: Optional[int] = None


class WIPTrendResponse(BaseModel):
    """趋势响应。"""
    days: List[WIPTrendPoint] = []
