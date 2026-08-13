"""
TPM 设备管理 API 接口

- GET    /tpm/equipment              — 设备列表
- POST   /tpm/equipment              — 添加设备
- GET    /tpm/equipment/{id}         — 设备详情
- PUT    /tpm/equipment/{id}         — 更新设备
- GET    /tpm/maintenance/plans      — 维护计划列表
- POST   /tpm/maintenance/plans      — 创建维护计划
- POST   /tpm/maintenance/records    — 记录维护执行
- GET    /tpm/faults                 — 故障列表
- POST   /tpm/faults                 — 报修
- PUT    /tpm/faults/{id}            — 更新故障状态
- GET    /tpm/stats                  — 统计数据
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user
from app.schemas.tpm import (
    EquipmentCreateRequest,
    EquipmentUpdateRequest,
    FaultCreateRequest,
    FaultUpdateRequest,
    MaintenancePlanCreateRequest,
    MaintenanceRecordCreateRequest,
)
from app.services.tpm_service import TPMService

router = APIRouter()


@router.get("/equipment")
async def list_equipment(
    equipment_type: Optional[str] = Query(None, description="类型筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询设备列表。"""
    service = TPMService(db)
    return await service.list_equipment(
        factory_id=user.factory_id,
        equipment_type=equipment_type,
        status=status,
        page=page,
        page_size=page_size,
    )


@router.post("/equipment")
async def create_equipment(
    body: EquipmentCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加设备。"""
    service = TPMService(db)
    result = await service.create_equipment(data=body, factory_id=user.factory_id)
    return {"success": True, "data": result.model_dump()}


@router.get("/stats")
async def tpm_stats(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取 TPM 统计。"""
    service = TPMService(db)
    stats = await service.get_stats(user.factory_id)
    return stats.model_dump()


@router.get("/maintenance/plans")
async def list_plans(
    equipment_id: Optional[int] = Query(None, description="设备 ID"),
    plan_type: Optional[str] = Query(None, description="计划类型"),
    overdue_only: bool = Query(False, description="仅逾期"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询维护计划。"""
    service = TPMService(db)
    return await service.list_plans(
        factory_id=user.factory_id,
        equipment_id=equipment_id,
        plan_type=plan_type,
        overdue_only=overdue_only,
        page=page,
        page_size=page_size,
    )


@router.post("/maintenance/plans")
async def create_plan(
    body: MaintenancePlanCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建维护计划。"""
    service = TPMService(db)
    result = await service.create_plan(data=body, factory_id=user.factory_id)
    return {"success": True, "data": result.model_dump()}


@router.post("/maintenance/records")
async def record_maintenance(
    body: MaintenanceRecordCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """记录维护执行。"""
    service = TPMService(db)
    result = await service.record_maintenance(
        data=body, user_id=user.id, factory_id=user.factory_id
    )
    return result


@router.get("/faults")
async def list_faults(
    status: Optional[str] = Query(None, description="状态筛选"),
    severity: Optional[str] = Query(None, description="严重程度筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询故障列表。"""
    service = TPMService(db)
    return await service.list_faults(
        factory_id=user.factory_id,
        status=status,
        severity=severity,
        page=page,
        page_size=page_size,
    )


@router.post("/faults")
async def create_fault(
    body: FaultCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """报修。"""
    service = TPMService(db)
    result = await service.create_fault(
        data=body, user_id=user.id, factory_id=user.factory_id
    )
    return {"success": True, "data": result.model_dump()}


@router.put("/faults/{fault_id}")
async def update_fault(
    fault_id: int,
    body: FaultUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新故障状态。"""
    service = TPMService(db)
    result = await service.update_fault(fault_id=fault_id, data=body)
    return {"success": True, "data": result.model_dump()}


@router.get("/equipment/{equipment_id}")
async def get_equipment(
    equipment_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取设备详情。"""
    service = TPMService(db)
    result = await service.get_equipment(equipment_id)
    return {"success": True, "data": result.model_dump()}


@router.put("/equipment/{equipment_id}")
async def update_equipment(
    equipment_id: int,
    body: EquipmentUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新设备。"""
    service = TPMService(db)
    result = await service.update_equipment(equipment_id=equipment_id, data=body)
    return {"success": True, "data": result.model_dump()}
