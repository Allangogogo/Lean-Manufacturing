"""
TPM 设备管理请求/响应模型
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# 请求模型
# ============================================================

class EquipmentCreateRequest(BaseModel):
    """添加设备。"""
    equipment_code: str = Field(..., min_length=1, max_length=30, description="设备编号")
    equipment_name: str = Field(..., min_length=1, max_length=200, description="设备名称")
    equipment_type: str = Field(..., description="类型: cold_header/thread_roller/heat_treat/electroplating/sorter/packager")
    location: Optional[str] = Field(None, description="位置")
    manufacturer: Optional[str] = Field(None, description="制造商")
    model: Optional[str] = Field(None, description="型号")
    serial_number: Optional[str] = Field(None, description="序列号")
    install_date: Optional[date] = Field(None, description="安装日期")
    warranty_until: Optional[date] = Field(None, description="保修到期")
    responsible_id: Optional[int] = Field(None, description="负责人 ID")
    notes: Optional[str] = Field(None, description="备注")


class EquipmentUpdateRequest(BaseModel):
    """更新设备。"""
    equipment_name: Optional[str] = Field(None, max_length=200)
    equipment_type: Optional[str] = None
    location: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    install_date: Optional[date] = None
    warranty_until: Optional[date] = None
    status: Optional[str] = None
    responsible_id: Optional[int] = None
    notes: Optional[str] = None


class MaintenancePlanCreateRequest(BaseModel):
    """创建维护计划。"""
    equipment_id: int = Field(..., description="设备 ID")
    plan_type: str = Field(..., description="类型: daily/weekly/monthly/quarterly/yearly")
    task_description: str = Field(..., min_length=1, description="任务描述")
    frequency_days: int = Field(1, description="执行间隔天数")
    next_due: date = Field(..., description="下次执行日期")
    assigned_to_id: Optional[int] = Field(None, description="负责人 ID")


class MaintenanceRecordCreateRequest(BaseModel):
    """记录维护执行。"""
    plan_id: Optional[int] = Field(None, description="关联计划 ID")
    equipment_id: int = Field(..., description="设备 ID")
    findings: Optional[str] = Field(None, description="检查发现")
    issues_found: Optional[str] = Field(None, description="发现问题")
    parts_replaced: Optional[str] = Field(None, description="更换零件")
    downtime_hours: Decimal = Field(Decimal("0"), description="停机时长")


class FaultCreateRequest(BaseModel):
    """报修。"""
    equipment_id: int = Field(..., description="设备 ID")
    fault_type: str = Field(..., min_length=1, description="故障类型")
    description: str = Field(..., min_length=1, description="故障描述")
    severity: str = Field("minor", description="严重程度: minor/major/critical")


class FaultUpdateRequest(BaseModel):
    """更新故障状态。"""
    status: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    downtime_hours: Optional[Decimal] = None
    repair_cost: Optional[Decimal] = None


# ============================================================
# 响应模型
# ============================================================

class EquipmentResponse(BaseModel):
    """设备响应。"""
    id: int
    equipment_code: str
    equipment_name: str
    equipment_type: str
    location: Optional[str] = None
    factory_id: int
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    install_date: Optional[date] = None
    warranty_until: Optional[date] = None
    status: str
    responsible_id: Optional[int] = None
    responsible_name: str = ""
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    active_plans: int = 0
    open_faults: int = 0


class MaintenancePlanResponse(BaseModel):
    """维护计划响应。"""
    id: int
    equipment_id: int
    equipment_name: str = ""
    plan_type: str
    task_description: str
    frequency_days: int = 1
    last_executed: Optional[date] = None
    next_due: date
    assigned_to_id: Optional[int] = None
    assigned_to_name: str = ""
    is_active: bool = True


class FaultResponse(BaseModel):
    """故障响应。"""
    id: int
    equipment_id: int
    equipment_name: str = ""
    reporter_name: str = ""
    fault_type: str
    description: str
    severity: str
    status: str
    reported_at: Optional[datetime] = None
    diagnosed_at: Optional[datetime] = None
    repaired_at: Optional[datetime] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    downtime_hours: Decimal = Decimal("0")
    repair_cost: Decimal = Decimal("0")


class TPMStatsResponse(BaseModel):
    """TPM 统计。"""
    total_equipment: int = 0
    normal: int = 0
    fault: int = 0
    maintenance: int = 0
    overdue_maintenance: int = 0
    open_faults: int = 0
    total_downtime: float = 0.0
