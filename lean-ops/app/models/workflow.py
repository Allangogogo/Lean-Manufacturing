"""
工作流模型

通用状态机：workflow_states + workflow_logs
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class WorkflowState(Base):
    """工作流状态表（每个实体一条记录，跟踪当前状态）。"""

    __tablename__ = "workflow_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    current_state: Mapped[str] = mapped_column(String(30), nullable=False)
    assigned_to_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), index=True
    )
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    factory_id: Mapped[int] = mapped_column(
        ForeignKey("factories.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # 关系
    logs: Mapped[list["WorkflowLog"]] = relationship(
        back_populates="state", cascade="all, delete-orphan"
    )


class WorkflowLog(Base):
    """工作流日志表（审批记录）。"""

    __tablename__ = "workflow_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    state_id: Mapped[int] = mapped_column(
        ForeignKey("workflow_states.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_state: Mapped[Optional[str]] = mapped_column(String(30))
    to_state: Mapped[str] = mapped_column(String(30), nullable=False)
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    operator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # 关系
    state: Mapped["WorkflowState"] = relationship(back_populates="logs")
