"""
项目管理模型
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

# 任务依赖关联表（多对多）
task_dependencies = Table(
    "task_dependencies",
    BaseModel.metadata,
    Column("task_id", ForeignKey("project_tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("depends_on_id", ForeignKey("project_tasks.id", ondelete="CASCADE"), primary_key=True),
)


class Project(BaseModel):
    """精益项目。"""

    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    project_type: Mapped[str] = mapped_column(String(30), nullable=False)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    factory_id: Mapped[int] = mapped_column(
        ForeignKey("factories.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="planning", nullable=False, index=True
    )
    priority: Mapped[str] = mapped_column(String(10), default="medium", nullable=False)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    target_end_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_end_date: Mapped[Optional[date]] = mapped_column(Date)
    budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    actual_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, nullable=False
    )
    scope: Mapped[Optional[str]] = mapped_column(Text)
    objectives: Mapped[Optional[str]] = mapped_column(Text)
    success_criteria: Mapped[Optional[str]] = mapped_column(Text)
    lean20_dimensions: Mapped[Optional[str]] = mapped_column(
        JSON,
        nullable=True,
        comment="Lean 2.0 dimension tags, e.g. [\"D\", \"G\"]",
    )
    source_assessment_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="ID of the Lean 2.0 assessment that triggered this project",
    )
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 关系
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id])
    milestones: Mapped[list["ProjectMilestone"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["ProjectTask"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    members: Mapped[list["ProjectMember"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    updates: Mapped[list["ProjectUpdate"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    risks: Mapped[list["ProjectRisk"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class ProjectMilestone(BaseModel):
    """项目里程碑。"""

    __tablename__ = "project_milestones"

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    target_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 关系
    project: Mapped["Project"] = relationship(back_populates="milestones")
    tasks: Mapped[list["ProjectTask"]] = relationship(
        back_populates="milestone"
    )


class ProjectTask(BaseModel):
    """项目任务。"""

    __tablename__ = "project_tasks"

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    milestone_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("project_milestones.id")
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    assigned_to_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="todo", nullable=False, index=True
    )
    priority: Mapped[str] = mapped_column(String(10), default="medium", nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_date: Mapped[Optional[date]] = mapped_column(Date)
    estimated_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 1))
    actual_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 1))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 依赖关系（多前置任务）
    # 关系
    project: Mapped["Project"] = relationship(back_populates="tasks")
    milestone: Mapped[Optional["ProjectMilestone"]] = relationship(
        back_populates="tasks"
    )


class ProjectMember(BaseModel):
    """项目成员。"""

    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_member"),
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(20), default="member", nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 关系
    project: Mapped["Project"] = relationship(back_populates="members")


class ProjectUpdate(BaseModel):
    """项目周报/进展。"""

    __tablename__ = "project_updates"

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    update_date: Mapped[date] = mapped_column(Date, nullable=False)
    progress_pct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    accomplishments: Mapped[Optional[str]] = mapped_column(Text)
    plan_next_week: Mapped[Optional[str]] = mapped_column(Text)
    risks_issues: Mapped[Optional[str]] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 关系
    project: Mapped["Project"] = relationship(back_populates="updates")
