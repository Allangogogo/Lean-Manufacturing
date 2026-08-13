"""
TPM 设备管理模型
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class TPMEquipment(BaseModel):
    """设备台账。"""

    __tablename__ = "tpm_equipment"

    equipment_code: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False
    )
    equipment_name: Mapped[str] = mapped_column(String(200), nullable=False)
    equipment_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    factory_id: Mapped[int] = mapped_column(
        ForeignKey("factories.id"), nullable=False, index=True
    )
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    serial_number: Mapped[Optional[str]] = mapped_column(String(100))
    install_date: Mapped[Optional[date]] = mapped_column(Date)
    warranty_until: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(20), default="normal", nullable=False, index=True
    )
    responsible_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # 关系
    maintenance_plans: Mapped[list["TPMMaintenancePlan"]] = relationship(
        back_populates="equipment", cascade="all, delete-orphan"
    )
    maintenance_records: Mapped[list["TPMMaintenanceRecord"]] = relationship(
        back_populates="equipment"
    )
    faults: Mapped[list["TPMFault"]] = relationship(back_populates="equipment")


class TPMMaintenancePlan(BaseModel):
    """TPM 维护计划。"""

    __tablename__ = "tpm_maintenance_plans"

    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("tpm_equipment.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    plan_type: Mapped[str] = mapped_column(String(20), nullable=False)
    task_description: Mapped[str] = mapped_column(Text, nullable=False)
    checklist_items: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    frequency_days: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    last_executed: Mapped[Optional[date]] = mapped_column(Date)
    next_due: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    assigned_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 关系
    equipment: Mapped["TPMEquipment"] = relationship(
        back_populates="maintenance_plans"
    )
    records: Mapped[list["TPMMaintenanceRecord"]] = relationship(
        back_populates="plan"
    )


class TPMMaintenanceRecord(BaseModel):
    """维护执行记录。"""

    __tablename__ = "tpm_maintenance_records"

    plan_id: Mapped[int] = mapped_column(
        ForeignKey("tpm_maintenance_plans.id"), nullable=False, index=True
    )
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("tpm_equipment.id"), nullable=False, index=True
    )
    executor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="planned", nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    findings: Mapped[Optional[str]] = mapped_column(Text)
    issues_found: Mapped[Optional[str]] = mapped_column(Text)
    parts_replaced: Mapped[Optional[str]] = mapped_column(Text)
    downtime_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )

    # 关系
    plan: Mapped["TPMMaintenancePlan"] = relationship(back_populates="records")
    equipment: Mapped["TPMEquipment"] = relationship(
        back_populates="maintenance_records"
    )


class TPMFault(BaseModel):
    """设备故障记录。"""

    __tablename__ = "tpm_faults"

    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("tpm_equipment.id"), nullable=False, index=True
    )
    reporter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    fault_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(10), default="minor", nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="reported", nullable=False, index=True
    )
    reported_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    diagnosed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    repaired_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    root_cause: Mapped[Optional[str]] = mapped_column(Text)
    corrective_action: Mapped[Optional[str]] = mapped_column(Text)
    downtime_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    repair_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, nullable=False
    )

    # 关系
    equipment: Mapped["TPMEquipment"] = relationship(back_populates="faults")
