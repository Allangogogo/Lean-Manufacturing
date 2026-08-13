"""
Automation Maturity & ROI Models

Supports:
- Automation maturity assessment (per dimension)
- ROI calculation and tracking
- PDCA cycle tracking for automation projects
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AutomationMaturity(Base):
    """Automation maturity assessment per factory/department."""

    __tablename__ = "automation_maturity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    factory_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("factories.id"), nullable=True)
    assessor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    assessor_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Five dimensions: quality, tooling, feeding, heat_treatment, logistics
    quality_score: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=Decimal("0"))
    tooling_score: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=Decimal("0"))
    feeding_score: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=Decimal("0"))
    heat_treatment_score: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=Decimal("0"))
    logistics_score: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=Decimal("0"))

    composite_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)
    maturity_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    items: Mapped[list["AutomationChecklistItem"]] = relationship(back_populates="assessment", cascade="all, delete-orphan")
    projects: Mapped[list["AutomationProject"]] = relationship(back_populates="assessment")


class AutomationChecklistItem(Base):
    """Checklist items for automation maturity assessment."""

    __tablename__ = "automation_checklist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(Integer, ForeignKey("automation_maturity.id"), nullable=False)
    dimension: Mapped[str] = mapped_column(String(20), nullable=False)
    item_text: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_checked: Mapped[bool] = mapped_column(Boolean, default=False)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)

    assessment: Mapped["AutomationMaturity"] = relationship(back_populates="items")


class AutomationProject(Base):
    """Automation project with ROI tracking and PDCA cycles."""

    __tablename__ = "automation_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("automation_maturity.id"), nullable=True)
    project_name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(10), default="P1")

    # Investment
    investment_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    investment_breakdown: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Expected returns
    expected_annual_benefit: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    expected_roi: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    expected_payback_months: Mapped[Decimal | None] = mapped_column(Numeric(6, 1), nullable=True)

    # Actual returns
    actual_annual_benefit: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    actual_roi: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    actual_payback_months: Mapped[Decimal | None] = mapped_column(Numeric(6, 1), nullable=True)

    # PDCA tracking
    pdca_phase: Mapped[str] = mapped_column(String(20), default="plan")
    pdca_cycle: Mapped[int] = mapped_column(Integer, default=1)

    status: Mapped[str] = mapped_column(String(20), default="planned")
    start_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    target_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    completed_date: Mapped[str | None] = mapped_column(String(20), nullable=True)

    owner: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now())

    assessment: Mapped["AutomationMaturity"] = relationship(back_populates="projects")
    reviews: Mapped[list["AutomationReview"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class AutomationReview(Base):
    """PDCA review records for automation projects."""

    __tablename__ = "automation_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("automation_projects.id"), nullable=False)
    pdca_phase: Mapped[str] = mapped_column(String(20), nullable=False)
    cycle_number: Mapped[int] = mapped_column(Integer, default=1)
    reviewer: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Plan
    plan_goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    plan_actions: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Do
    do_progress: Mapped[str | None] = mapped_column(Text, nullable=True)
    do_issues: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Check
    check_results: Mapped[str | None] = mapped_column(Text, nullable=True)
    check_roi_actual: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)

    # Act
    act_decision: Mapped[str | None] = mapped_column(String(50), nullable=True)
    act_next_steps: Mapped[str | None] = mapped_column(Text, nullable=True)

    review_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    project: Mapped["AutomationProject"] = relationship(back_populates="reviews")
