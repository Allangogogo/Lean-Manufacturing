"""
改善提案业务逻辑层

职责：
1. 提案 CRUD
2. 工作流状态管理（提交/审批/实施/关闭）
3. 评论管理
4. 统计查询
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError, ForbiddenError, NotFoundError, WorkflowError
from app.core.pagination import PaginatedResponse, paginate
from app.core.workflow import WorkflowEngine
from app.models.kaizen import KaizenAttachment, KaizenComment, KaizenProposal
from app.models.user import User
from app.schemas.kaizen import (
    KaizenActionRequest,
    KaizenCommentRequest,
    KaizenCreateRequest,
    KaizenDetailResponse,
    KaizenListItem,
    KaizenStatsResponse,
    KaizenUpdateRequest,
)


class KaizenService:
    """改善提案业务服务。"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.workflow = WorkflowEngine(db)

    # ============================================================
    # 查询
    # ============================================================

    async def list_proposals(
        self,
        factory_id: int,
        status: Optional[str] = None,
        category: Optional[str] = None,
        submitter_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse:
        """查询提案列表（支持筛选、分页）。"""
        query = select(KaizenProposal).where(
            KaizenProposal.factory_id == factory_id
        )

        if status:
            query = query.where(KaizenProposal.status == status)
        if category:
            query = query.where(KaizenProposal.category == category)
        if submitter_id:
            query = query.where(KaizenProposal.submitter_id == submitter_id)

        query = query.order_by(desc(KaizenProposal.created_at))

        result = await paginate(self.db, query, page, page_size)

        # 补充提交者姓名
        items = []
        for p in result.data:
            user = await self.db.get(User, p.submitter_id)
            items.append(KaizenListItem(
                id=p.id,
                title=p.title,
                category=p.category,
                priority=p.priority,
                status=p.status,
                submitter_name=user.display_name if user else "",
                expected_saving=p.expected_saving,
                created_at=p.created_at,
                due_date=p.due_date,
            ))

        return PaginatedResponse.create(
            items=[i.model_dump() for i in items],
            total=result.pagination["total"],
            page=page,
            page_size=page_size,
        )

    async def get_proposal(self, proposal_id: int) -> KaizenDetailResponse:
        """获取提案详情。"""
        result = await self.db.execute(
            select(KaizenProposal)
            .options(
                selectinload(KaizenProposal.comments),
                selectinload(KaizenProposal.attachments),
            )
            .where(KaizenProposal.id == proposal_id)
        )
        proposal = result.scalar_one_or_none()
        if proposal is None:
            raise NotFoundError("改善提案", proposal_id)

        # 补充用户信息
        submitter = await self.db.get(User, proposal.submitter_id)

        # 获取工作流日志
        history = await self.workflow.get_history("kaizen", proposal_id)

        # 获取允许的操作
        allowed_actions = self.workflow.get_allowed_actions(
            proposal.status, ""  # 角色在 API 层检查
        )

        # 补充评论中的用户名
        comments = []
        for c in (proposal.comments or []):
            user = await self.db.get(User, c.user_id)
            comments.append({
                "id": c.id,
                "user_id": c.user_id,
                "user_name": user.display_name if user else "",
                "action": c.action,
                "comment": c.comment,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            })

        # 补充附件上传者
        attachments = []
        for a in (proposal.attachments or []):
            attachments.append({
                "id": a.id,
                "filename": a.filename,
                "filepath": a.filepath,
                "filesize": a.filesize,
                "uploaded_by": a.uploaded_by,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            })

        return KaizenDetailResponse(
            id=proposal.id,
            title=proposal.title,
            description=proposal.description,
            category=proposal.category,
            priority=proposal.priority,
            status=proposal.status,
            submitter_id=proposal.submitter_id,
            submitter_name=submitter.display_name if submitter else "",
            factory_id=proposal.factory_id,
            department_id=proposal.department_id,
            expected_benefit=proposal.expected_benefit,
            expected_saving=proposal.expected_saving,
            actual_benefit=proposal.actual_benefit,
            actual_saving=proposal.actual_saving,
            root_cause=proposal.root_cause,
            solution=proposal.solution,
            implementation_plan=proposal.implementation_plan,
            result=proposal.result,
            due_date=proposal.due_date,
            closed_at=proposal.closed_at,
            created_at=proposal.created_at,
            updated_at=proposal.updated_at,
            allowed_actions=allowed_actions,
            comments=comments,
            attachments=attachments,
            workflow_history=[
                {
                    "from_state": h.get("from_state"),
                    "to_state": h["to_state"],
                    "action": h["action"],
                    "operator_id": h["operator_id"],
                    "operator_name": "",  # 后续可查
                    "comment": h.get("comment"),
                    "created_at": h.get("created_at"),
                }
                for h in history
            ],
        )

    async def get_stats(self, factory_id: int) -> KaizenStatsResponse:
        """获取提案统计。"""
        result = await self.db.execute(
            select(
                KaizenProposal.status,
                func.count(KaizenProposal.id),
            )
            .where(KaizenProposal.factory_id == factory_id)
            .group_by(KaizenProposal.status)
        )
        status_counts = {row[0]: row[1] for row in result.all()}

        total = sum(status_counts.values())

        # 总节约金额
        saving_result = await self.db.execute(
            select(func.sum(KaizenProposal.actual_saving)).where(
                KaizenProposal.factory_id == factory_id,
                KaizenProposal.actual_saving.isnot(None),
            )
        )
        total_saving = saving_result.scalar() or 0

        return KaizenStatsResponse(
            total=total,
            draft=status_counts.get("draft", 0),
            submitted=status_counts.get("submitted", 0),
            reviewing=status_counts.get("reviewing", 0),
            approved=status_counts.get("approved", 0),
            implementing=status_counts.get("implementing", 0),
            verified=status_counts.get("verified", 0),
            closed=status_counts.get("closed", 0),
            total_saving=float(total_saving),
        )

    # ============================================================
    # 写操作
    # ============================================================

    async def create_proposal(
        self,
        data: KaizenCreateRequest,
        user_id: int,
        factory_id: int,
        department_id: Optional[int] = None,
    ) -> KaizenDetailResponse:
        """创建改善提案。"""
        proposal = KaizenProposal(
            title=data.title,
            description=data.description,
            category=data.category,
            priority=data.priority,
            expected_benefit=data.expected_benefit,
            expected_saving=data.expected_saving,
            root_cause=data.root_cause,
            solution=data.solution,
            implementation_plan=data.implementation_plan,
            due_date=data.due_date,
            submitter_id=user_id,
            factory_id=factory_id,
            department_id=department_id,
            status="draft",
        )
        self.db.add(proposal)
        await self.db.flush()

        # 初始化工作流
        await self.workflow.init_state(
            entity_type="kaizen",
            entity_id=proposal.id,
            initial_state="draft",
            created_by_id=user_id,
            factory_id=factory_id,
            assigned_to_id=user_id,
        )

        return await self.get_proposal(proposal.id)

    async def update_proposal(
        self,
        proposal_id: int,
        data: KaizenUpdateRequest,
        user_id: int,
    ) -> KaizenDetailResponse:
        """更新提案（仅草稿/退回状态可编辑）。"""
        proposal = await self.db.get(KaizenProposal, proposal_id)
        if proposal is None:
            raise NotFoundError("改善提案", proposal_id)

        if proposal.status not in ("draft", "returned"):
            raise AppError("当前状态不允许编辑", code="VALIDATION_ERROR")

        if proposal.submitter_id != user_id:
            raise ForbiddenError("只能编辑自己提交的提案")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(proposal, field, value)

        return await self.get_proposal(proposal_id)

    async def execute_action(
        self,
        proposal_id: int,
        data: KaizenActionRequest,
        user_id: int,
        role_code: str,
    ) -> KaizenDetailResponse:
        """执行工作流操作（提交/审批/拒绝/退回/开始实施/完成/关闭）。"""
        proposal = await self.db.get(KaizenProposal, proposal_id)
        if proposal is None:
            raise NotFoundError("改善提案", proposal_id)

        # 执行状态转换
        new_state = await self.workflow.transition(
            entity_type="kaizen",
            entity_id=proposal_id,
            action=data.action,
            operator_id=user_id,
            operator_role=role_code,
            comment=data.comment,
        )

        # 更新提案状态
        proposal.status = new_state

        # 如果关闭，记录关闭时间
        if new_state == "closed":
            proposal.closed_at = datetime.now(timezone.utc)

        # 添加评论记录
        if data.comment:
            comment = KaizenComment(
                proposal_id=proposal_id,
                user_id=user_id,
                action=data.action,
                comment=data.comment,
            )
            self.db.add(comment)

        return await self.get_proposal(proposal_id)

    async def add_comment(
        self,
        proposal_id: int,
        data: KaizenCommentRequest,
        user_id: int,
    ) -> KaizenDetailResponse:
        """添加评论。"""
        proposal = await self.db.get(KaizenProposal, proposal_id)
        if proposal is None:
            raise NotFoundError("改善提案", proposal_id)

        comment = KaizenComment(
            proposal_id=proposal_id,
            user_id=user_id,
            action="comment",
            comment=data.comment,
        )
        self.db.add(comment)

        return await self.get_proposal(proposal_id)
