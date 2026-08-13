"""
培训管理模型
"""

from __future__ import annotations

from datetime import date, datetime, time
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
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class TrainingSession(BaseModel):
    """培训场次。"""

    __tablename__ = "training_sessions"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    factory_id: Mapped[int] = mapped_column(
        ForeignKey("factories.id"), nullable=False, index=True
    )
    training_type: Mapped[str] = mapped_column(String(30), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[Optional[time]] = mapped_column(Time)
    end_time: Mapped[Optional[time]] = mapped_column(Time)
    duration_hours: Mapped[Decimal] = mapped_column(
        Numeric(4, 1), default=1.0, nullable=False
    )
    location: Mapped[Optional[str]] = mapped_column(String(200))
    max_participants: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="scheduled", nullable=False, index=True
    )
    pass_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=60.0, nullable=False
    )

    # 关系
    trainer: Mapped["User"] = relationship(foreign_keys=[trainer_id])
    enrollments: Mapped[list["TrainingEnrollment"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    materials: Mapped[list["TrainingMaterial"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class TrainingEnrollment(BaseModel):
    """培训报名/签到/成绩。"""

    __tablename__ = "training_enrollments"
    __table_args__ = (
        UniqueConstraint("session_id", "user_id", name="uq_enrollment_session_user"),
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey("training_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="enrolled", nullable=False
    )
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    feedback_rating: Mapped[Optional[int]] = mapped_column(Integer)
    feedback_comment: Mapped[Optional[str]] = mapped_column(Text)
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    attended_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    certified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 关系
    session: Mapped["TrainingSession"] = relationship(back_populates="enrollments")
    user: Mapped["User"] = relationship()


class TrainingMaterial(BaseModel):
    """培训材料。"""

    __tablename__ = "training_materials"

    session_id: Mapped[int] = mapped_column(
        ForeignKey("training_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    material_name: Mapped[str] = mapped_column(String(200), nullable=False)
    material_type: Mapped[str] = mapped_column(String(20), nullable=False)
    filepath: Mapped[str] = mapped_column(String(500), nullable=False)
    filesize: Mapped[Optional[int]] = mapped_column(Integer)
    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    # 关系
    session: Mapped["TrainingSession"] = relationship(back_populates="materials")
