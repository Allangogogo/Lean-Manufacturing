"""
成熟度评估模型
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

from app.models.base import BaseModel


class MaturityAssessment(BaseModel):
    """成熟度评估主表。"""

    __tablename__ = "maturity_assessments"

    assessment_type: Mapped[str] = mapped_column(String(30), nullable=False)
    area_name: Mapped[str] = mapped_column(String(100), nullable=False)
    assessor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    factory_id: Mapped[int] = mapped_column(
        ForeignKey("factories.id"), nullable=False, index=True
    )
    overall_level: Mapped[Optional[str]] = mapped_column(String(20))
    total_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    max_score: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), default=100, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="draft", nullable=False, index=True
    )
    summary: Mapped[Optional[str]] = mapped_column(Text)
    recommendations: Mapped[Optional[str]] = mapped_column(Text)
    assessment_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 关系
    dimensions: Mapped[list["MaturityDimension"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )


class MaturityDimension(BaseModel):
    """评估维度（一级指标）。"""

    __tablename__ = "maturity_dimensions"

    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("maturity_assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dimension_name: Mapped[str] = mapped_column(String(100), nullable=False)
    weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), default=0.25, nullable=False
    )
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    max_score: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), default=25, nullable=False
    )
    level: Mapped[Optional[str]] = mapped_column(String(20))
    findings: Mapped[Optional[str]] = mapped_column(Text)
    action_items: Mapped[Optional[str]] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 关系
    assessment: Mapped["MaturityAssessment"] = relationship(
        back_populates="dimensions"
    )
    criteria: Mapped[list["MaturityCriterion"]] = relationship(
        back_populates="dimension", cascade="all, delete-orphan"
    )


class MaturityCriterion(BaseModel):
    """评估细项（二级指标）。"""

    __tablename__ = "maturity_criteria"

    dimension_id: Mapped[int] = mapped_column(
        ForeignKey("maturity_dimensions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    criterion_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), default=0.1, nullable=False
    )
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    max_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=5, nullable=False
    )
    level: Mapped[Optional[str]] = mapped_column(String(10))
    evidence: Mapped[Optional[str]] = mapped_column(Text)
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    improvement_suggestion: Mapped[Optional[str]] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 关系
    dimension: Mapped["MaturityDimension"] = relationship(
        back_populates="criteria"
    )
