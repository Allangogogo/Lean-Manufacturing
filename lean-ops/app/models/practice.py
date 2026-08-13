"""
Best Practice 管理模型
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class BestPractice(BaseModel):
    """最佳实践。"""

    __tablename__ = "best_practices"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(30), nullable=False)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    factory_id: Mapped[int] = mapped_column(
        ForeignKey("factories.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="draft", nullable=False, index=True
    )
    problem_statement: Mapped[Optional[str]] = mapped_column(Text)
    root_cause: Mapped[Optional[str]] = mapped_column(Text)
    solution: Mapped[str] = mapped_column(Text, nullable=False)
    results: Mapped[Optional[str]] = mapped_column(Text)
    applicable_areas: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    estimated_saving: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    actual_saving: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    difficulty_level: Mapped[str] = mapped_column(
        String(10), default="medium", nullable=False
    )
    implementation_time_days: Mapped[Optional[int]] = mapped_column(Integer)
    tags: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 关系
    author: Mapped["User"] = relationship(foreign_keys=[author_id])
    votes: Mapped[list["BestPracticeVote"]] = relationship(
        back_populates="practice", cascade="all, delete-orphan"
    )
    comments: Mapped[list["BestPracticeComment"]] = relationship(
        back_populates="practice", cascade="all, delete-orphan"
    )
    attachments: Mapped[list["BestPracticeAttachment"]] = relationship(
        back_populates="practice", cascade="all, delete-orphan"
    )


class BestPracticeVote(BaseModel):
    """点赞/收藏。"""

    __tablename__ = "best_practice_votes"
    __table_args__ = (
        UniqueConstraint(
            "practice_id", "user_id", "vote_type", name="uq_bp_vote"
        ),
    )

    practice_id: Mapped[int] = mapped_column(
        ForeignKey("best_practices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    vote_type: Mapped[str] = mapped_column(String(10), nullable=False)

    # 关系
    practice: Mapped["BestPractice"] = relationship(back_populates="votes")


class BestPracticeComment(BaseModel):
    """实践评论。"""

    __tablename__ = "best_practice_comments"

    practice_id: Mapped[int] = mapped_column(
        ForeignKey("best_practices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[Optional[int]] = mapped_column(Integer)

    # 关系
    practice: Mapped["BestPractice"] = relationship(back_populates="comments")


class BestPracticeAttachment(BaseModel):
    """实践附件。"""

    __tablename__ = "best_practice_attachments"

    practice_id: Mapped[int] = mapped_column(
        ForeignKey("best_practices.id", ondelete="CASCADE"),
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
    practice: Mapped["BestPractice"] = relationship(back_populates="attachments")
