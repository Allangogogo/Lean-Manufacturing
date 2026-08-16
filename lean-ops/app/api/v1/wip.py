"""
WIP 在制品管理 API 接口

- GET    /wip/overview            全局指标卡
- GET    /wip/operations          工序 WIP 水位
- GET    /wip/trends              水位趋势
- GET    /wip/orders              工单列表
- POST   /wip/orders              创建工单
- GET    /wip/orders/{id}         工单详情
- POST   /wip/operations/{id}/move  工序流转登记
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import CurrentUser, get_current_user
from app.database import get_db
from app.schemas.wip import (
    OperationMoveRequest,
    ProductionOrderCreateRequest,
)
from app.services.wip_service import WIPService

router = APIRouter()


@router.get("/overview")
async def wip_overview(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """全局指标卡。"""
    service = WIPService(db)
    result = await service.get_overview(factory_id=user.factory_id)
    return {"success": True, "data": result.model_dump()}


@router.get("/operations")
async def wip_operations(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """各工序 WIP 水位。"""
    service = WIPService(db)
    results = await service.get_operation_wip(factory_id=user.factory_id)
    return {
        "success": True,
        "data": [r.model_dump() for r in results],
    }


@router.get("/trends")
async def wip_trends(
    days: int = Query(30, ge=1, le=90, description="趋势天数"),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """WIP 水位趋势。"""
    service = WIPService(db)
    results = await service.get_trend(factory_id=user.factory_id, days=days)
    return {
        "success": True,
        "data": [r.model_dump() for r in results],
    }


@router.get("/orders")
async def list_orders(
    status: Optional[str] = Query(None, description="状态过滤"),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """工单列表。"""
    service = WIPService(db)
    orders = await service.list_orders(factory_id=user.factory_id, status=status)
    return {
        "success": True,
        "data": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "product_name": o.product_name,
                "product_code": o.product_code,
                "quantity": o.quantity,
                "priority": o.priority,
                "status": o.status,
                "planned_start": o.planned_start.isoformat() if o.planned_start else None,
                "planned_end": o.planned_end.isoformat() if o.planned_end else None,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in orders
        ],
    }


@router.post("/orders")
async def create_order(
    body: ProductionOrderCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建工单。"""
    service = WIPService(db)
    order = await service.create_order(
        data=body, factory_id=user.factory_id, user_id=user.id
    )
    return {"success": True, "data": {"id": order.id, "order_no": order.order_no}}


@router.get("/orders/{order_id}")
async def order_detail(
    order_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """工单详情（含工序进度）。"""
    service = WIPService(db)
    order = await service.get_order_detail(order_id)
    return {
        "success": True,
        "data": {
            "order": {
                "id": order.id,
                "order_no": order.order_no,
                "product_name": order.product_name,
                "quantity": order.quantity,
                "priority": order.priority,
                "status": order.status,
            },
            "operations": [
                {
                    "id": op.id,
                    "sequence_no": op.sequence_no,
                    "operation_name": op.operation_name,
                    "input_qty": op.input_qty,
                    "output_qty": op.output_qty,
                    "wip_qty": op.wip_qty,
                    "status": op.status,
                }
                for op in sorted(order.operations, key=lambda x: x.sequence_no)
            ],
        },
    }


@router.post("/operations/{operation_id}/move")
async def move_operation(
    operation_id: int,
    body: OperationMoveRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """工序流转登记。"""
    service = WIPService(db)
    op = await service.move_operation(
        operation_id=operation_id, data=body, user_id=user.id
    )
    return {
        "success": True,
        "data": {
            "id": op.id,
            "operation_name": op.operation_name,
            "input_qty": op.input_qty,
            "output_qty": op.output_qty,
            "wip_qty": op.wip_qty,
            "status": op.status,
        },
    }
