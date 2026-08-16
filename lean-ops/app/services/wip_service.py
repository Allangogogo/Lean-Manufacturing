"""
WIP 在制品管理业务逻辑层

职责：
1. 工单 CRUD
2. 工序流转登记（自动更新 WIP 水位）
3. 全局指标与瓶颈识别
4. 趋势聚合
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List, Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError, NotFoundError
from app.models.wip import (
    ProductionOrder,
    WIPDailySnapshot,
    WIPTransaction,
    WorkOrderOperation,
)
from app.schemas.wip import (
    OperationMoveRequest,
    OperationWIPResponse,
    ProductionOrderCreateRequest,
    WIPOverviewResponse,
    WIPTrendPoint,
)


class WIPService:
    """WIP 在制品管理业务服务。"""

    # 标准工序链
    OPERATION_CHAIN = [
        "机加工",
        "精加工",
        "热处理",
        "表面处理",
        "装配",
        "包装",
    ]

    # 目标水位（每工序，演示值，后续按节拍计算）
    TARGET_WIP = {
        "机加工": 400,
        "精加工": 300,
        "热处理": 600,
        "表面处理": 400,
        "装配": 200,
        "包装": 100,
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # 工单管理
    # ============================================================

    async def create_order(
        self, data: ProductionOrderCreateRequest, factory_id: int, user_id: int
    ) -> ProductionOrder:
        """创建工单（自动生成 6 道工序）。"""
        # 工单号查重
        existing = await self.db.scalar(
            select(ProductionOrder).where(ProductionOrder.order_no == data.order_no)
        )
        if existing:
            raise AppError(f"工单号 {data.order_no} 已存在")

        order = ProductionOrder(
            order_no=data.order_no,
            product_name=data.product_name,
            product_code=data.product_code,
            quantity=data.quantity,
            priority=data.priority,
            status="pending",
            factory_id=factory_id,
            planned_start=data.planned_start,
            planned_end=data.planned_end,
            created_by=user_id,
        )
        self.db.add(order)
        await self.db.flush()

        # 生成标准工序链
        for seq, op_name in enumerate(self.OPERATION_CHAIN, start=1):
            op = WorkOrderOperation(
                order_id=order.id,
                sequence_no=seq,
                operation_name=op_name,
                status="pending",
            )
            self.db.add(op)

        await self.db.flush()
        return order

    async def list_orders(
        self, factory_id: int, status: Optional[str] = None
    ) -> List[ProductionOrder]:
        """工单列表。"""
        stmt = (
            select(ProductionOrder)
            .where(ProductionOrder.factory_id == factory_id)
            .order_by(desc(ProductionOrder.created_at))
        )
        if status:
            stmt = stmt.where(ProductionOrder.status == status)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get_order_detail(self, order_id: int) -> ProductionOrder:
        """工单详情（含工序）。"""
        stmt = (
            select(ProductionOrder)
            .where(ProductionOrder.id == order_id)
            .options(selectinload(ProductionOrder.operations))
        )
        order = await self.db.scalar(stmt)
        if not order:
            raise NotFoundError("工单不存在")
        return order

    # ============================================================
    # 工序流转
    # ============================================================

    async def move_operation(
        self,
        operation_id: int,
        data: OperationMoveRequest,
        user_id: int,
    ) -> WorkOrderOperation:
        """登记工序流转，自动更新 WIP 水位。

        move_in:  投入本工序（本工序 input_qty += n）
        move_out: 本工序产出（本工序 output_qty += n, wip_qty -= n）
        """
        op = await self.db.get(WorkOrderOperation, operation_id)
        if not op:
            raise NotFoundError("工序不存在")

        if data.move_type == "move_in":
            op.input_qty += data.quantity
            op.wip_qty += data.quantity
            op.status = "in_progress"
        elif data.move_type == "move_out":
            if data.quantity > op.wip_qty:
                raise AppError("产出数量超过当前在制量")
            op.output_qty += data.quantity
            op.wip_qty -= data.quantity
            # 全部产出 → 完成
            if op.wip_qty == 0 and op.output_qty > 0:
                op.status = "completed"
                op.end_time = datetime.utcnow()
            else:
                op.status = "in_progress"
        else:
            raise AppError("move_type 必须为 move_in 或 move_out")

        # 流转记录
        tx = WIPTransaction(
            operation_id=operation_id,
            transaction_type=data.move_type,
            quantity=data.quantity,
            operator_id=user_id,
        )
        self.db.add(tx)
        await self.db.flush()
        return op

    # ============================================================
    # 指标计算
    # ============================================================

    async def get_overview(self, factory_id: int) -> WIPOverviewResponse:
        """全局指标卡数据。"""
        # 总在制
        total_wip = (
            await self.db.scalar(
                select(func.coalesce(func.sum(WorkOrderOperation.wip_qty), 0)).where(
                    WorkOrderOperation.status.in_(["in_progress", "pending"])
                )
            )
        ) or 0

        # 在制工单数
        active_orders = (
            await self.db.scalar(
                select(func.count(ProductionOrder.id)).where(
                    ProductionOrder.factory_id == factory_id,
                    ProductionOrder.status == "in_progress",
                )
            )
        ) or 0

        # 今日产出（今日 move_out 总量）
        today = date.today()
        today_throughput = (
            await self.db.scalar(
                select(func.coalesce(func.sum(WIPTransaction.quantity), 0)).where(
                    WIPTransaction.transaction_type == "move_out",
                    func.date(WIPTransaction.occurred_at) == today.isoformat(),
                )
            )
        ) or 0

        # 平均提前期（完成工单：actual_end - actual_start，天）
        completed = await self.db.scalars(
            select(ProductionOrder).where(ProductionOrder.status == "completed")
        )
        lead_times = []
        for o in completed.all():
            if o.actual_start and o.actual_end:
                lead_times.append(
                    (o.actual_end - o.actual_start).total_seconds() / 86400.0
                )
        avg_lt = round(sum(lead_times) / len(lead_times), 1) if lead_times else 0.0

        # 瓶颈：WIP 最高的工序
        bottlenecks = await self.get_operation_wip(factory_id)
        bottleneck = bottlenecks[0] if bottlenecks else None

        return WIPOverviewResponse(
            total_wip=total_wip,
            active_orders=active_orders,
            today_throughput=today_throughput,
            avg_lead_time_days=avg_lt,
            bottleneck=bottleneck,
        )

    async def get_operation_wip(
        self, factory_id: int
    ) -> List[OperationWIPResponse]:
        """各工序 WIP 水位（按工序聚合，识别瓶颈）。"""
        stmt = (
            select(
                WorkOrderOperation.operation_name,
                func.min(WorkOrderOperation.sequence_no).label("seq"),
                func.sum(WorkOrderOperation.wip_qty).label("wip"),
                func.sum(WorkOrderOperation.output_qty).label("out"),
            )
            .join(ProductionOrder)
            .where(
                ProductionOrder.factory_id == factory_id,
                WorkOrderOperation.status.in_(["in_progress", "pending"]),
            )
            .group_by(WorkOrderOperation.operation_name)
            .order_by("seq")
        )
        rows = (await self.db.execute(stmt)).all()

        results: List[OperationWIPResponse] = []
        for row in rows:
            results.append(
                OperationWIPResponse(
                    operation_name=row.operation_name,
                    sequence_no=row.seq,
                    wip_qty=row.wip or 0,
                    throughput=row.out or 0,
                    status="in_progress",
                )
            )

        # 瓶颈识别：WIP 水位 / 目标水位 比值最高
        if results:
            max_ratio = max(
                (r.wip_qty / self.TARGET_WIP.get(r.operation_name, 1))
                for r in results
            )
            for r in results:
                ratio = r.wip_qty / self.TARGET_WIP.get(r.operation_name, 1)
                r.is_bottleneck = ratio == max_ratio and ratio > 1.0

        return results

    async def get_trend(
        self, factory_id: int, days: int = 30
    ) -> List[WIPTrendPoint]:
        """WIP 水位趋势（按日汇总）。"""
        stmt = (
            select(
                WIPDailySnapshot.snapshot_date,
                func.sum(WIPDailySnapshot.wip_qty).label("total"),
            )
            .where(
                WIPDailySnapshot.factory_id == factory_id,
                WIPDailySnapshot.snapshot_date
                >= (date.today() - timedelta(days=days)),
            )
            .group_by(WIPDailySnapshot.snapshot_date)
            .order_by(WIPDailySnapshot.snapshot_date)
        )
        rows = (await self.db.execute(stmt)).all()

        return [
            WIPTrendPoint(
                date=row.snapshot_date.isoformat(),
                total_wip=row.total or 0,
            )
            for row in rows
        ]
