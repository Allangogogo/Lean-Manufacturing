"""
培训管理业务逻辑层

职责：
1. 培训场次 CRUD
2. 报名/签到/评分管理
3. 培训材料管理
4. 统计查询
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.core.pagination import PaginatedResponse, paginate
from app.models.training import TrainingEnrollment, TrainingMaterial, TrainingSession
from app.models.user import User
from app.schemas.training import (
    EnrollmentActionRequest,
    EnrollmentResponse,
    TrainingMaterialResponse,
    TrainingSessionCreateRequest,
    TrainingSessionDetailResponse,
    TrainingSessionListItem,
    TrainingSessionUpdateRequest,
    TrainingStatsResponse,
)


class TrainingService:
    """培训管理业务服务。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # 查询
    # ============================================================

    async def list_sessions(
        self,
        factory_id: int,
        status: Optional[str] = None,
        training_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse:
        """查询培训列表。"""
        query = select(TrainingSession).where(
            TrainingSession.factory_id == factory_id
        )
        if status:
            query = query.where(TrainingSession.status == status)
        if training_type:
            query = query.where(TrainingSession.training_type == training_type)

        query = query.order_by(desc(TrainingSession.scheduled_date))
        result = await paginate(self.db, query, page, page_size)

        items = []
        for s in result.data:
            trainer = await self.db.get(User, s.trainer_id)
            # 报名人数
            count_result = await self.db.execute(
                select(func.count(TrainingEnrollment.id)).where(
                    TrainingEnrollment.session_id == s.id,
                    TrainingEnrollment.status != "cancelled",
                )
            )
            items.append(TrainingSessionListItem(
                id=s.id,
                title=s.title,
                trainer_name=trainer.display_name if trainer else "",
                training_type=s.training_type,
                level=s.level,
                scheduled_date=s.scheduled_date,
                duration_hours=s.duration_hours,
                location=s.location,
                status=s.status,
                enrolled_count=count_result.scalar() or 0,
                max_participants=s.max_participants,
            ))

        return PaginatedResponse.create(
            items=[i.model_dump() for i in items],
            total=result.pagination["total"],
            page=page,
            page_size=page_size,
        )

    async def get_session(self, session_id: int) -> TrainingSessionDetailResponse:
        """获取培训详情。"""
        result = await self.db.execute(
            select(TrainingSession)
            .options(
                selectinload(TrainingSession.enrollments),
                selectinload(TrainingSession.materials),
            )
            .where(TrainingSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        if session is None:
            raise NotFoundError("培训场次", session_id)

        trainer = await self.db.get(User, session.trainer_id)

        enrollments = []
        for e in (session.enrollments or []):
            user = await self.db.get(User, e.user_id)
            enrollments.append(EnrollmentResponse(
                id=e.id,
                session_id=e.session_id,
                user_id=e.user_id,
                user_name=user.display_name if user else "",
                status=e.status,
                score=e.score,
                feedback_rating=e.feedback_rating,
                enrolled_at=e.enrolled_at,
                attended_at=e.attended_at,
                certified_at=e.certified_at,
            ))

        materials = []
        for m in (session.materials or []):
            materials.append(TrainingMaterialResponse(
                id=m.id,
                material_name=m.material_name,
                material_type=m.material_type,
                filepath=m.filepath,
                filesize=m.filesize,
                uploaded_by=m.uploaded_by,
                created_at=m.created_at,
            ))

        enrolled_count = len([e for e in enrollments if e.status != "cancelled"])

        return TrainingSessionDetailResponse(
            id=session.id,
            title=session.title,
            description=session.description,
            trainer_id=session.trainer_id,
            trainer_name=trainer.display_name if trainer else "",
            factory_id=session.factory_id,
            training_type=session.training_type,
            level=session.level,
            scheduled_date=session.scheduled_date,
            start_time=session.start_time,
            end_time=session.end_time,
            duration_hours=session.duration_hours,
            location=session.location,
            max_participants=session.max_participants,
            status=session.status,
            pass_score=session.pass_score,
            enrolled_count=enrolled_count,
            created_at=session.created_at,
            enrollments=enrollments,
            materials=materials,
        )

    async def get_stats(self, factory_id: int) -> TrainingStatsResponse:
        """获取培训统计。"""
        result = await self.db.execute(
            select(
                TrainingSession.status,
                func.count(TrainingSession.id),
            )
            .where(TrainingSession.factory_id == factory_id)
            .group_by(TrainingSession.status)
        )
        status_counts = {row[0]: row[1] for row in result.all()}
        total = sum(status_counts.values())

        # 总报名数
        enroll_result = await self.db.execute(
            select(func.count(TrainingEnrollment.id))
            .join(TrainingSession, TrainingEnrollment.session_id == TrainingSession.id)
            .where(
                TrainingSession.factory_id == factory_id,
                TrainingEnrollment.status != "cancelled",
            )
        )
        total_enrollments = enroll_result.scalar() or 0

        # 平均分
        avg_result = await self.db.execute(
            select(func.avg(TrainingEnrollment.score))
            .join(TrainingSession, TrainingEnrollment.session_id == TrainingSession.id)
            .where(
                TrainingSession.factory_id == factory_id,
                TrainingEnrollment.score.isnot(None),
            )
        )
        avg_score = avg_result.scalar() or 0

        # 认证率
        cert_result = await self.db.execute(
            select(func.count(TrainingEnrollment.id))
            .join(TrainingSession, TrainingEnrollment.session_id == TrainingSession.id)
            .where(
                TrainingSession.factory_id == factory_id,
                TrainingEnrollment.status == "certified",
            )
        )
        certified = cert_result.scalar() or 0
        cert_rate = (certified / total_enrollments * 100) if total_enrollments > 0 else 0

        return TrainingStatsResponse(
            total=total,
            scheduled=status_counts.get("scheduled", 0),
            in_progress=status_counts.get("in_progress", 0),
            completed=status_counts.get("completed", 0),
            total_enrollments=total_enrollments,
            avg_score=float(avg_score),
            certification_rate=round(cert_rate, 1),
        )

    # ============================================================
    # 写操作
    # ============================================================

    async def create_session(
        self,
        data: TrainingSessionCreateRequest,
        user_id: int,
        factory_id: int,
    ) -> TrainingSessionDetailResponse:
        """创建培训场次。"""
        session = TrainingSession(
            title=data.title,
            description=data.description,
            trainer_id=user_id,
            factory_id=factory_id,
            training_type=data.training_type,
            level=data.level,
            scheduled_date=data.scheduled_date,
            start_time=data.start_time,
            end_time=data.end_time,
            duration_hours=data.duration_hours,
            location=data.location,
            max_participants=data.max_participants,
            pass_score=data.pass_score,
            status="scheduled",
        )
        self.db.add(session)
        await self.db.flush()
        return await self.get_session(session.id)

    async def update_session(
        self,
        session_id: int,
        data: TrainingSessionUpdateRequest,
        user_id: int,
    ) -> TrainingSessionDetailResponse:
        """更新培训场次。"""
        session = await self.db.get(TrainingSession, session_id)
        if session is None:
            raise NotFoundError("培训场次", session_id)

        if session.status == "completed":
            raise AppError("已完成的培训不可修改", code="VALIDATION_ERROR")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(session, field, value)

        return await self.get_session(session_id)

    async def handle_enrollment(
        self,
        session_id: int,
        data: EnrollmentActionRequest,
        user_id: int,
    ) -> TrainingSessionDetailResponse:
        """处理报名/签到/取消。"""
        session = await self.db.get(TrainingSession, session_id)
        if session is None:
            raise NotFoundError("培训场次", session_id)

        if data.action == "enroll":
            # 检查是否已报名
            existing = await self.db.execute(
                select(TrainingEnrollment).where(
                    TrainingEnrollment.session_id == session_id,
                    TrainingEnrollment.user_id == user_id,
                )
            )
            enrollment = existing.scalar_one_or_none()
            if enrollment and enrollment.status != "cancelled":
                raise AppError("已报名该培训", code="CONFLICT")

            # 检查人数限制
            count_result = await self.db.execute(
                select(func.count(TrainingEnrollment.id)).where(
                    TrainingEnrollment.session_id == session_id,
                    TrainingEnrollment.status != "cancelled",
                )
            )
            if (count_result.scalar() or 0) >= session.max_participants:
                raise AppError("培训人数已满", code="VALIDATION_ERROR")

            if enrollment:
                enrollment.status = "enrolled"
                enrollment.enrolled_at = datetime.now(timezone.utc)
            else:
                enrollment = TrainingEnrollment(
                    session_id=session_id,
                    user_id=user_id,
                    status="enrolled",
                )
                self.db.add(enrollment)

        elif data.action == "attend":
            result = await self.db.execute(
                select(TrainingEnrollment).where(
                    TrainingEnrollment.session_id == session_id,
                    TrainingEnrollment.user_id == user_id,
                )
            )
            enrollment = result.scalar_one_or_none()
            if enrollment is None:
                raise NotFoundError("报名记录")
            if enrollment.status == "cancelled":
                raise AppError("已取消报名", code="VALIDATION_ERROR")

            enrollment.status = "attended"
            enrollment.attended_at = datetime.now(timezone.utc)
            if data.score is not None:
                enrollment.score = data.score
                # 如果达到及格分，自动认证
                if data.score >= session.pass_score:
                    enrollment.status = "certified"
                    enrollment.certified_at = datetime.now(timezone.utc)
            if data.feedback_rating is not None:
                enrollment.feedback_rating = data.feedback_rating
            if data.feedback_comment is not None:
                enrollment.feedback_comment = data.feedback_comment

        elif data.action == "cancel":
            result = await self.db.execute(
                select(TrainingEnrollment).where(
                    TrainingEnrollment.session_id == session_id,
                    TrainingEnrollment.user_id == user_id,
                )
            )
            enrollment = result.scalar_one_or_none()
            if enrollment:
                enrollment.status = "cancelled"

        await self.db.flush()
        return await self.get_session(session_id)
