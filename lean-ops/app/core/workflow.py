"""
通用工作流引擎

职责：
1. 定义状态转换规则
2. 执行状态转换
3. 记录审批日志
4. 支持多业务线（Kaizen、5S、项目等）

设计思路：
- workflow_states 表存储每个实体的当前状态
- workflow_logs 表记录每次状态变更
- 通过 STATE_RULES 字典定义哪些角色可以执行哪些操作
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import WorkflowError
from app.models.user import User


# ============================================================
# 状态转换规则定义
# ============================================================

# 格式: { (当前状态, 动作): (目标状态, {允许的角色}) }
# 动作: submit/approve/reject/return/close/reopen/start/complete

STATE_RULES: Dict[Tuple[str, str], Tuple[str, Set[str]]] = {
    # ---- 改善提案 ----
    ("draft", "submit"):         ("submitted",    {"worker", "supervisor", "lean_mgr"}),
    ("submitted", "approve"):    ("approved",     {"supervisor", "lean_mgr"}),
    ("submitted", "reject"):     ("rejected",     {"supervisor", "lean_mgr"}),
    ("submitted", "return"):     ("returned",     {"supervisor", "lean_mgr"}),
    ("returned", "submit"):      ("submitted",    {"worker", "supervisor", "lean_mgr"}),
    ("returned", "close"):       ("closed",       {"lean_mgr"}),
    ("approved", "start"):       ("implementing", {"worker", "supervisor", "lean_mgr"}),
    ("implementing", "complete"): ("verified",    {"supervisor", "lean_mgr"}),
    ("verified", "close"):       ("closed",       {"lean_mgr"}),
    ("rejected", "submit"):      ("submitted",    {"worker", "supervisor", "lean_mgr"}),
    ("rejected", "close"):       ("closed",       {"lean_mgr"}),

    # ---- 5S 审核 ----
    # (在 fives_service 中自定义处理)

    # ---- 项目 ----
    ("planning", "start"):       ("active",       {"lean_mgr"}),
    ("active", "hold"):          ("on_hold",      {"lean_mgr"}),
    ("on_hold", "resume"):       ("active",       {"lean_mgr"}),
    ("active", "complete"):      ("completed",    {"lean_mgr"}),
    ("active", "cancel"):        ("cancelled",    {"lean_mgr"}),
    ("planning", "cancel"):      ("cancelled",    {"lean_mgr"}),
    ("on_hold", "cancel"):       ("cancelled",    {"lean_mgr"}),

    # ---- Best Practice ----
    ("draft", "submit"):         ("published",    {"worker", "supervisor", "lean_mgr", "admin"}),
    ("published", "archive"):    ("archived",     {"lean_mgr", "admin"}),
    ("archived", "reopen"):      ("published",    {"lean_mgr", "admin"}),

    # ---- 成熟度评估 ----
    ("draft", "start"):          ("in_progress",  {"lean_mgr"}),
    ("in_progress", "complete"): ("completed",    {"lean_mgr"}),
    ("completed", "reopen"):     ("in_progress",  {"lean_mgr"}),
}


# ============================================================
# 工作流引擎
# ============================================================

class WorkflowEngine:
    """通用工作流引擎。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_state(
        self,
        entity_type: str,
        entity_id: int,
    ) -> Optional[str]:
        """获取实体当前状态。"""
        from app.models.workflow import WorkflowState

        result = await self.db.execute(
            select(WorkflowState).where(
                WorkflowState.entity_type == entity_type,
                WorkflowState.entity_id == entity_id,
            )
        )
        state = result.scalar_one_or_none()
        return state.current_state if state else None

    async def init_state(
        self,
        entity_type: str,
        entity_id: int,
        initial_state: str,
        created_by_id: int,
        factory_id: int,
        assigned_to_id: Optional[int] = None,
    ) -> None:
        """初始化实体工作流状态。"""
        from app.models.workflow import WorkflowState

        state = WorkflowState(
            entity_type=entity_type,
            entity_id=entity_id,
            current_state=initial_state,
            assigned_to_id=assigned_to_id or created_by_id,
            created_by_id=created_by_id,
            factory_id=factory_id,
        )
        self.db.add(state)
        await self.db.flush()

    async def transition(
        self,
        entity_type: str,
        entity_id: int,
        action: str,
        operator_id: int,
        operator_role: str,
        comment: Optional[str] = None,
    ) -> str:
        """
        执行状态转换。

        Args:
            entity_type: 实体类型
            entity_id: 实体 ID
            action: 动作名称
            operator_id: 操作人 ID
            operator_role: 操作人角色编码
            comment: 审批意见

        Returns:
            转换后的新状态

        Raises:
            WorkflowError: 状态转换不允许
        """
        from app.models.workflow import WorkflowState, WorkflowLog

        # 查询当前状态
        result = await self.db.execute(
            select(WorkflowState).where(
                WorkflowState.entity_type == entity_type,
                WorkflowState.entity_id == entity_id,
            )
        )
        state = result.scalar_one_or_none()
        if state is None:
            raise WorkflowError(f"实体 {entity_type}:{entity_id} 无工作流状态记录")

        current_state = state.current_state

        # 查找转换规则
        rule_key = (current_state, action)
        if rule_key not in STATE_RULES:
            raise WorkflowError(
                f"当前状态 [{current_state}] 不允许执行操作 [{action}]"
            )

        target_state, allowed_roles = STATE_RULES[rule_key]

        # 检查角色权限
        if operator_role not in allowed_roles and operator_role != "admin":
            raise WorkflowError(
                f"角色 [{operator_role}] 无权执行此操作"
            )

        # 执行状态转换
        from_state = state.current_state
        state.current_state = target_state

        # 记录日志
        log = WorkflowLog(
            state_id=state.id,
            from_state=from_state,
            to_state=target_state,
            action=action,
            operator_id=operator_id,
            comment=comment,
        )
        self.db.add(log)
        await self.db.flush()

        return target_state

    async def get_history(
        self,
        entity_type: str,
        entity_id: int,
    ) -> List[dict]:
        """获取实体的工作流历史。"""
        from app.models.workflow import WorkflowState, WorkflowLog

        # 查询状态
        result = await self.db.execute(
            select(WorkflowState).where(
                WorkflowState.entity_type == entity_type,
                WorkflowState.entity_id == entity_id,
            )
        )
        state = result.scalar_one_or_none()
        if state is None:
            return []

        # 查询日志
        log_result = await self.db.execute(
            select(WorkflowLog)
            .where(WorkflowLog.state_id == state.id)
            .order_by(WorkflowLog.created_at)
        )
        logs = log_result.scalars().all()

        return [
            {
                "from_state": log.from_state,
                "to_state": log.to_state,
                "action": log.action,
                "operator_id": log.operator_id,
                "comment": log.comment,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]

    def get_allowed_actions(
        self,
        current_state: str,
        role_code: str,
    ) -> List[str]:
        """获取当前状态下允许执行的动作列表。"""
        actions = []
        for (state, action), (_, allowed_roles) in STATE_RULES.items():
            if state == current_state and (role_code in allowed_roles or role_code == "admin"):
                actions.append(action)
        return actions
