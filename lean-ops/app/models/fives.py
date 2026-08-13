"""
5S 审核模型
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


class FiveSArea(BaseModel):
    """5S 审核区域。"""

    __tablename__ = "five_s_areas"

    factory_id: Mapped[int] = mapped_column(
        ForeignKey("factories.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(20))
    description: Mapped[Optional[str]] = mapped_column(Text)
    responsible_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 关系
    audits: Mapped[list["FiveSAudit"]] = relationship(back_populates="area")


class FiveSAudit(BaseModel):
    """5S 审核记录。"""

    __tablename__ = "five_s_audits"

    area_id: Mapped[int] = mapped_column(
        ForeignKey("five_s_areas.id"), nullable=False, index=True
    )
    factory_id: Mapped[int] = mapped_column(
        ForeignKey("factories.id"), nullable=False, index=True
    )
    auditor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    audit_type: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    max_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=100, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="scheduled", nullable=False, index=True
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed_date: Mapped[Optional[date]] = mapped_column(Date)
    remarks: Mapped[Optional[str]] = mapped_column(Text)

    # 关系
    area: Mapped["FiveSArea"] = relationship(back_populates="audits")
    items: Mapped[list["FiveSItem"]] = relationship(
        back_populates="audit", cascade="all, delete-orphan"
    )
    improvements: Mapped[list["FiveSImprovement"]] = relationship(
        back_populates="audit", cascade="all, delete-orphan"
    )


class FiveSItem(BaseModel):
    """5S 审核细项。"""

    __tablename__ = "five_s_items"

    audit_id: Mapped[int] = mapped_column(
        ForeignKey("five_s_audits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    s_category: Mapped[str] = mapped_column(String(20), nullable=False)
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 1), default=1.0, nullable=False
    )
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    max_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=10.0, nullable=False
    )
    photo_path: Mapped[Optional[str]] = mapped_column(String(500))
    remarks: Mapped[Optional[str]] = mapped_column(Text)

    # 关系
    audit: Mapped["FiveSAudit"] = relationship(back_populates="items")


class FiveSImprovement(BaseModel):
    """5S 改善跟踪。"""

    __tablename__ = "five_s_improvements"

    audit_id: Mapped[int] = mapped_column(
        ForeignKey("five_s_audits.id"), nullable=False, index=True
    )
    item_description: Mapped[str] = mapped_column(Text, nullable=False)
    assigned_to_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="open", nullable=False, index=True
    )
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_date: Mapped[Optional[date]] = mapped_column(Date)
    evidence_path: Mapped[Optional[str]] = mapped_column(String(500))
    verified_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 关系
    audit: Mapped["FiveSAudit"] = relationship(back_populates="improvements")
