"""
Best Practice 管理业务逻辑层

职责：
1. 最佳实践 CRUD
2. 发布/归档
3. 点赞/收藏
4. 评论管理
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError, NotFoundError
from app.core.pagination import PaginatedResponse, paginate
from app.models.practice import (
    BestPractice,
    BestPracticeComment,
    BestPracticeVote,
)
from app.models.user import User
from app.schemas.practice import (
    CommentCreateRequest,
    CommentResponse,
    PracticeCreateRequest,
    PracticeDetailResponse,
    PracticeListItem,
    PracticeStatsResponse,
    PracticeUpdateRequest,
    VoteRequest,
)


class PracticeService:
    """Best Practice 管理业务服务。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # 查询
    # ============================================================

    async def list_practices(
        self,
        factory_id: int,
        category: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        sort_by: str = "newest",
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse:
        """查询最佳实践列表。"""
        query = select(BestPractice).where(BestPractice.factory_id == factory_id)
        if category:
            query = query.where(BestPractice.category == category)
        if status:
            query = query.where(BestPractice.status == status)
        if keyword:
            query = query.where(BestPractice.title.contains(keyword))

        if sort_by == "popular":
            query = query.order_by(desc(BestPractice.view_count))
        elif sort_by == "saving":
            query = query.order_by(desc(BestPractice.estimated_saving))
        else:
            query = query.order_by(desc(BestPractice.created_at))

        result = await paginate(self.db, query, page, page_size)

        items = []
        for p in result.data:
            author = await self.db.get(User, p.author_id)
            like_count = await self.db.execute(
                select(func.count(BestPracticeVote.id)).where(
                    BestPracticeVote.practice_id == p.id,
                    BestPracticeVote.vote_type == "like",
                )
            )
            comment_count = await self.db.execute(
                select(func.count(BestPracticeComment.id)).where(
                    BestPracticeComment.practice_id == p.id
                )
            )
            items.append(PracticeListItem(
                id=p.id, title=p.title, category=p.category,
                subcategory=p.subcategory,
                author_name=author.display_name if author else "",
                status=p.status, difficulty_level=p.difficulty_level,
                estimated_saving=p.estimated_saving,
                view_count=p.view_count, usage_count=p.usage_count,
                like_count=like_count.scalar() or 0,
                comment_count=comment_count.scalar() or 0,
                tags=p.tags, created_at=p.created_at,
            ))

        return PaginatedResponse.create(
            items=[i.model_dump() for i in items],
            total=result.pagination["total"], page=page, page_size=page_size,
        )

    async def get_practice(
        self, practice_id: int, user_id: Optional[int] = None,
    ) -> PracticeDetailResponse:
        """获取最佳实践详情。"""
        result = await self.db.execute(
            select(BestPractice)
            .options(
                selectinload(BestPractice.comments),
                selectinload(BestPractice.votes),
            )
            .where(BestPractice.id == practice_id)
        )
        practice = result.scalar_one_or_none()
        if practice is None:
            raise NotFoundError("最佳实践", practice_id)

        # 增加浏览量
        practice.view_count += 1
        await self.db.flush()

        author = await self.db.get(User, practice.author_id)

        # 统计
        like_count = sum(1 for v in (practice.votes or []) if v.vote_type == "like")
        bookmark_count = sum(1 for v in (practice.votes or []) if v.vote_type == "bookmark")

        # 当前用户状态
        user_liked = False
        user_bookmarked = False
        if user_id:
            user_liked = any(
                v.user_id == user_id and v.vote_type == "like"
                for v in (practice.votes or [])
            )
            user_bookmarked = any(
                v.user_id == user_id and v.vote_type == "bookmark"
                for v in (practice.votes or [])
            )

        comments = []
        for c in (practice.comments or []):
            commenter = await self.db.get(User, c.user_id)
            comments.append(CommentResponse(
                id=c.id, user_name=commenter.display_name if commenter else "",
                comment=c.comment, rating=c.rating, created_at=c.created_at,
            ))
        # 按时间排序
        comments.sort(key=lambda x: x.created_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

        return PracticeDetailResponse(
            id=practice.id, title=practice.title, description=practice.description,
            category=practice.category, subcategory=practice.subcategory,
            author_name=author.display_name if author else "",
            status=practice.status,
            problem_statement=practice.problem_statement,
            root_cause=practice.root_cause, solution=practice.solution,
            results=practice.results, applicable_areas=practice.applicable_areas,
            estimated_saving=practice.estimated_saving,
            actual_saving=practice.actual_saving,
            difficulty_level=practice.difficulty_level,
            implementation_time_days=practice.implementation_time_days,
            tags=practice.tags, view_count=practice.view_count,
            usage_count=practice.usage_count,
            like_count=like_count, bookmark_count=bookmark_count,
            user_liked=user_liked, user_bookmarked=user_bookmarked,
            published_at=practice.published_at, created_at=practice.created_at,
            comments=comments,
        )

    # ============================================================
    # CRUD
    # ============================================================

    async def create_practice(
        self, data: PracticeCreateRequest, user_id: int, factory_id: int,
    ) -> PracticeDetailResponse:
        """提交最佳实践。"""
        practice = BestPractice(
            title=data.title, description=data.description,
            category=data.category, subcategory=data.subcategory,
            author_id=user_id, factory_id=factory_id, status="draft",
            problem_statement=data.problem_statement,
            root_cause=data.root_cause, solution=data.solution,
            results=data.results, applicable_areas=data.applicable_areas,
            estimated_saving=data.estimated_saving,
            actual_saving=data.actual_saving,
            difficulty_level=data.difficulty_level,
            implementation_time_days=data.implementation_time_days,
            tags=data.tags,
        )
        self.db.add(practice)
        await self.db.flush()
        return await self.get_practice(practice.id, user_id)

    async def update_practice(
        self, practice_id: int, data: PracticeUpdateRequest, user_id: int,
    ) -> PracticeDetailResponse:
        """更新最佳实践。"""
        practice = await self.db.get(BestPractice, practice_id)
        if practice is None:
            raise NotFoundError("最佳实践", practice_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(practice, field, value)
        await self.db.flush()
        return await self.get_practice(practice_id, user_id)

    async def publish_practice(
        self, practice_id: int, user_id: int,
    ) -> PracticeDetailResponse:
        """发布最佳实践（精益经理审核后发布）。"""
        practice = await self.db.get(BestPractice, practice_id)
        if practice is None:
            raise NotFoundError("最佳实践", practice_id)
        if practice.status not in ("draft", "submitted"):
            raise AppError("当前状态不允许发布", code="INVALID_STATE")
        practice.status = "published"
        practice.published_at = datetime.now(timezone.utc)
        await self.db.flush()
        return await self.get_practice(practice_id, user_id)

    async def archive_practice(
        self, practice_id: int, user_id: int,
    ) -> PracticeDetailResponse:
        """归档最佳实践。"""
        practice = await self.db.get(BestPractice, practice_id)
        if practice is None:
            raise NotFoundError("最佳实践", practice_id)
        practice.status = "archived"
        await self.db.flush()
        return await self.get_practice(practice_id, user_id)

    # ============================================================
    # 点赞/收藏
    # ============================================================

    async def toggle_vote(
        self, practice_id: int, data: VoteRequest, user_id: int,
    ) -> PracticeDetailResponse:
        """切换点赞/收藏。"""
        if data.vote_type not in ("like", "bookmark"):
            raise AppError("无效的投票类型", code="INVALID_PARAMS")
        existing = await self.db.execute(
            select(BestPracticeVote).where(
                BestPracticeVote.practice_id == practice_id,
                BestPracticeVote.user_id == user_id,
                BestPracticeVote.vote_type == data.vote_type,
            )
        )
        vote = existing.scalar_one_or_none()
        if vote:
            await self.db.delete(vote)
        else:
            self.db.add(BestPracticeVote(
                practice_id=practice_id, user_id=user_id,
                vote_type=data.vote_type,
            ))
        await self.db.flush()
        return await self.get_practice(practice_id, user_id)

    # ============================================================
    # 评论
    # ============================================================

    async def add_comment(
        self, practice_id: int, data: CommentCreateRequest, user_id: int,
    ) -> PracticeDetailResponse:
        """添加评论。"""
        practice = await self.db.get(BestPractice, practice_id)
        if practice is None:
            raise NotFoundError("最佳实践", practice_id)
        comment = BestPracticeComment(
            practice_id=practice_id, user_id=user_id,
            comment=data.comment, rating=data.rating,
        )
        self.db.add(comment)
        await self.db.flush()
        return await self.get_practice(practice_id, user_id)

    # ============================================================
    # 统计
    # ============================================================

    async def get_stats(self, factory_id: int) -> PracticeStatsResponse:
        """获取最佳实践统计。"""
        result = await self.db.execute(
            select(BestPractice.status, func.count(BestPractice.id))
            .where(BestPractice.factory_id == factory_id)
            .group_by(BestPractice.status)
        )
        status_counts = {row[0]: row[1] for row in result.all()}
        total = sum(status_counts.values())

        views_result = await self.db.execute(
            select(func.sum(BestPractice.view_count))
            .where(BestPractice.factory_id == factory_id)
        )
        total_views = views_result.scalar() or 0

        likes_result = await self.db.execute(
            select(func.count(BestPracticeVote.id))
            .join(BestPractice, BestPractice.id == BestPracticeVote.practice_id)
            .where(
                BestPractice.factory_id == factory_id,
                BestPracticeVote.vote_type == "like",
            )
        )
        total_likes = likes_result.scalar() or 0

        savings_result = await self.db.execute(
            select(func.sum(BestPractice.estimated_saving))
            .where(
                BestPractice.factory_id == factory_id,
                BestPractice.estimated_saving.isnot(None),
            )
        )
        total_savings = float(savings_result.scalar() or 0)

        return PracticeStatsResponse(
            total=total,
            published=status_counts.get("published", 0),
            draft=status_counts.get("draft", 0),
            total_views=total_views,
            total_likes=total_likes,
            total_savings=total_savings,
        )
