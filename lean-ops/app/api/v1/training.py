"""
培训管理 API 接口

- GET    /training/sessions          — 培训列表
- POST   /training/sessions          — 创建培训
- GET    /training/sessions/{id}     — 培训详情
- PUT    /training/sessions/{id}     — 更新培训
- POST   /training/sessions/{id}/enroll — 报名/签到/取消
- GET    /training/stats             — 统计数据
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user
from app.schemas.training import (
    EnrollmentActionRequest,
    TrainingSessionCreateRequest,
    TrainingSessionUpdateRequest,
)
from app.services.training_service import TrainingService

router = APIRouter()


@router.get("/sessions")
async def list_sessions(
    status: Optional[str] = Query(None, description="状态筛选"),
    training_type: Optional[str] = Query(None, description="类型筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询培训列表。"""
    service = TrainingService(db)
    return await service.list_sessions(
        factory_id=user.factory_id,
        status=status,
        training_type=training_type,
        page=page,
        page_size=page_size,
    )


@router.post("/sessions")
async def create_session(
    body: TrainingSessionCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建培训场次。"""
    service = TrainingService(db)
    result = await service.create_session(
        data=body,
        user_id=user.id,
        factory_id=user.factory_id,
    )
    return {"success": True, "data": result.model_dump()}


@router.get("/stats")
async def training_stats(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取培训统计。"""
    service = TrainingService(db)
    stats = await service.get_stats(user.factory_id)
    return stats.model_dump()


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取培训详情。"""
    service = TrainingService(db)
    result = await service.get_session(session_id)
    return {"success": True, "data": result.model_dump()}


@router.put("/sessions/{session_id}")
async def update_session(
    session_id: int,
    body: TrainingSessionUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新培训场次。"""
    service = TrainingService(db)
    result = await service.update_session(
        session_id=session_id,
        data=body,
        user_id=user.id,
    )
    return {"success": True, "data": result.model_dump()}


@router.post("/sessions/{session_id}/enroll")
async def handle_enrollment(
    session_id: int,
    body: EnrollmentActionRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """报名/签到/取消。"""
    service = TrainingService(db)
    result = await service.handle_enrollment(
        session_id=session_id,
        data=body,
        user_id=user.id,
    )
    return {"success": True, "data": result.model_dump()}


@router.get("/enrollments")
async def list_enrollments(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取报名记录列表（含场次标题与用户名）。"""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.training import TrainingEnrollment

    query = (
        select(TrainingEnrollment)
        .options(
            selectinload(TrainingEnrollment.session),
            selectinload(TrainingEnrollment.user),
        )
        .order_by(TrainingEnrollment.enrolled_at.desc())
    )
    result = await db.execute(query)
    rows = result.scalars().all()
    return [
        {
            "id": r.id,
            "session_id": r.session_id,
            "user_id": r.user_id,
            "status": r.status,
            "enrolled_at": r.enrolled_at.isoformat() if r.enrolled_at else None,
            "session_title": r.session.title if r.session else None,
            "user_name": r.user.display_name if r.user else None,
        }
        for r in rows
    ]


@router.get("/materials")
async def list_materials(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取培训材料列表（含场次标题）。"""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.training import TrainingMaterial

    query = (
        select(TrainingMaterial)
        .options(selectinload(TrainingMaterial.session))
        .order_by(TrainingMaterial.created_at.desc())
    )
    result = await db.execute(query)
    rows = result.scalars().all()
    return [
        {
            "id": r.id,
            "session_id": r.session_id,
            "material_name": r.material_name,
            "material_type": r.material_type,
            "filepath": r.filepath,
            "filesize": r.filesize,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "session_title": r.session.title if r.session else None,
        }
        for r in rows
    ]
