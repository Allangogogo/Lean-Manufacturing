"""
WIP 在制品管理模型

生产工单、工序在制、流转记录、每日水位快照。
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ProductionOrder(BaseModel):
    """生产工单。"""

    __tablename__ = "production_orders"

    order_no: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    product_code: Mapped[Optional[str]] = mapped_column(String(50))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[str] = mapped_column(
        String(10), default="normal", nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False, index=True
    )
    factory_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("factories.id"), index=True
    )
    planned_start: Mapped[Optional[date]] = mapped_column(Date)
    planned_end: Mapped[Optional[date]] = mapped_column(Date)
    actual_start: Mapped[Optional[datetime]] = mapped_column(DateTime)
    actual_end: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    # 关系
    operations: Mapped[list["WorkOrderOperation"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class WorkOrderOperation(BaseModel):
    """工序在制记录（WIP 核心表）。"""

    __tablename__ = "work_order_operations"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("production_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    operation_name: Mapped[str] = mapped_column(String(50), nullable=False)
    equipment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tpm_equipment.id"), index=True
    )
    input_qty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_qty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wip_qty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False, index=True
    )
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 关系
    order: Mapped["ProductionOrder"] = relationship(
        back_populates="operations"
    )
    equipment: Mapped[Optional["TPMEquipment"]] = relationship(
        foreign_keys=[equipment_id]
    )
    transactions: Mapped[list["WIPTransaction"]] = relationship(
        back_populates="operation",
        cascade="all, delete-orphan",
        foreign_keys="WIPTransaction.operation_id",
    )


class WIPTransaction(BaseModel):
    """流转记录（审计/趋势）。"""

    __tablename__ = "wip_transactions"

    operation_id: Mapped[int] = mapped_column(
        ForeignKey("work_order_operations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transaction_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # move_in / move_out / complete
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    from_operation: Mapped[Optional[int]] = mapped_column(
        ForeignKey("work_order_operations.id")
    )
    to_operation: Mapped[Optional[int]] = mapped_column(
        ForeignKey("work_order_operations.id")
    )
    operator_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # 关系
    operation: Mapped["WorkOrderOperation"] = relationship(
        back_populates="transactions",
        foreign_keys=[operation_id],
    )


class WIPDailySnapshot(BaseModel):
    """每日水位快照（趋势图数据）。"""

    __tablename__ = "wip_daily_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "snapshot_date", "factory_id", "operation_name",
            name="uq_wip_snapshot_date_factory_op",
        ),
    )

    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    factory_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("factories.id"), index=True
    )
    operation_name: Mapped[str] = mapped_column(String(50), nullable=False)
    wip_qty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    throughput: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cycle_time_min: Mapped[Optional[int]] = mapped_column(Integer)
