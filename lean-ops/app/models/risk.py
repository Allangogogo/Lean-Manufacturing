"""风险管理模型。"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ProjectRisk(BaseModel):
    """项目风险。"""

    __tablename__ = "project_risks"

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    probability: Mapped[str] = mapped_column(
        String(20), default="medium", nullable=False
    )
    impact: Mapped[str] = mapped_column(
        String(20), default="medium", nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="identified", nullable=False, index=True
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    response_plan: Mapped[Optional[str]] = mapped_column(Text)
    mitigation_actions: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 关系
    project = relationship("Project", back_populates="risks")
    owner = relationship("User")
