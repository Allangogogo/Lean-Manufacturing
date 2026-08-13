"""
Lean 2.0 成熟度评估模型

Industry 5.0 扩展维度: O(运营) / D(数字) / G(绿色) / R(韧性) / H(人本)
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
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
from sqlalchemy.types import JSON

from app.models.base import BaseModel


class Lean20Assessment(BaseModel):
    """Lean 2.0 成熟度评估主表。"""

    __tablename__ = "lean20_assessments"

    assessment_date: Mapped[date] = mapped_column(Date, nullable=False)
    factory_id: Mapped[int] = mapped_column(
        ForeignKey("factories.id"), nullable=False, index=True
    )
    assessor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="draft", nullable=False, index=True
    )
    weights: Mapped[Optional[str]] = mapped_column(
        JSON,
        nullable=True,
        comment="Dimension weights, e.g. {\"O\": 0.30, \"D\": 0.25, ...}",
    )
    composite_index: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2))
    overall_level: Mapped[Optional[str]] = mapped_column(String(50))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    recommendations: Mapped[Optional[str]] = mapped_column(Text)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 关系
    dimension_scores: Mapped[list["Lean20DimensionScore"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )


class Lean20DimensionScore(BaseModel):
    """Lean 2.0 维度评分。"""

    __tablename__ = "lean20_dimension_scores"

    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("lean20_assessments.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    dimension_code: Mapped[str] = mapped_column(
        String(1), nullable=False,
        comment="O/D/G/R/H",
    )
    level: Mapped[Decimal] = mapped_column(
        Numeric(3, 1), nullable=False,
        comment="Score 1.0 - 5.0",
    )
    weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), default=Decimal("0.20"), nullable=False,
    )
    weighted_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # 关系
    assessment: Mapped["Lean20Assessment"] = relationship(
        back_populates="dimension_scores"
    )
