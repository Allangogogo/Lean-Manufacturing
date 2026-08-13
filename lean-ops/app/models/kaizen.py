"""
改善提案模型
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


class KaizenProposal(BaseModel):
    """改善提案主表。"""

    __tablename__ = "kaizen_proposals"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    submitter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    factory_id: Mapped[int] = mapped_column(
        ForeignKey("factories.id"), nullable=False
    )
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))
    status: Mapped[str] = mapped_column(
        String(20), default="draft", nullable=False, index=True
    )
    priority: Mapped[str] = mapped_column(String(10), default="medium", nullable=False)
    current_approver_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id")
    )
    expected_benefit: Mapped[Optional[str]] = mapped_column(Text)
    expected_saving: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    actual_benefit: Mapped[Optional[str]] = mapped_column(Text)
    actual_saving: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    root_cause: Mapped[Optional[str]] = mapped_column(Text)
    solution: Mapped[Optional[str]] = mapped_column(Text)
    implementation_plan: Mapped[Optional[str]] = mapped_column(Text)
    result: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 关系
    submitter: Mapped["User"] = relationship(foreign_keys=[submitter_id])
    comments: Mapped[list["KaizenComment"]] = relationship(
        back_populates="proposal", cascade="all, delete-orphan"
    )
    attachments: Mapped[list["KaizenAttachment"]] = relationship(
        back_populates="proposal", cascade="all, delete-orphan"
    )


class KaizenComment(BaseModel):
    """提案评论/审批记录。"""

    __tablename__ = "kaizen_comments"

    proposal_id: Mapped[int] = mapped_column(
        ForeignKey("kaizen_proposals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # 关系
    proposal: Mapped["KaizenProposal"] = relationship(back_populates="comments")
    user: Mapped["User"] = relationship()


class KaizenAttachment(BaseModel):
    """提案附件。"""

    __tablename__ = "kaizen_attachments"

    proposal_id: Mapped[int] = mapped_column(
        ForeignKey("kaizen_proposals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filepath: Mapped[str] = mapped_column(String(500), nullable=False)
    filesize: Mapped[Optional[int]] = mapped_column(Integer)
    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    # 关系
    proposal: Mapped["KaizenProposal"] = relationship(back_populates="attachments")
