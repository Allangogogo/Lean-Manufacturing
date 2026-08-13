"""
成熟度评估 API 接口

- GET    /maturity/assessments            — 评估列表
- POST   /maturity/assessments            — 创建评估
- GET    /maturity/assessments/stats      — 统计数据
- GET    /maturity/trends                 — 历史趋势
- GET    /maturity/assessments/{id}       — 评估详情
- PUT    /maturity/assessments/{id}/scores — 保存评分
- POST   /maturity/assessments/{id}/complete — 完成评估
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user
from app.schemas.maturity import (
    AssessmentCompleteRequest,
    AssessmentCreateRequest,
    DimensionScoreRequest,
)
from app.services.maturity_service import MaturityService

router = APIRouter()


@router.get("/assessments")
async def list_assessments(
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MaturityService(db)
    return await service.list_assessments(
        factory_id=user.factory_id, status=status, page=page, page_size=page_size,
    )


@router.post("/assessments")
async def create_assessment(
    body: AssessmentCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MaturityService(db)
    result = await service.create_assessment(data=body, user_id=user.id, factory_id=user.factory_id)
    return {"success": True, "data": result.model_dump()}


@router.get("/assessments/stats")
async def assessment_stats(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MaturityService(db)
    return (await service.get_stats(user.factory_id)).model_dump()


@router.get("/trends")
async def trends(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MaturityService(db)
    result = await service.get_trends(user.factory_id)
    return [t.model_dump() for t in result]


@router.get("/assessments/{assessment_id}")
async def get_assessment(
    assessment_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MaturityService(db)
    result = await service.get_assessment(assessment_id)
    return {"success": True, "data": result.model_dump()}


@router.put("/assessments/{assessment_id}/scores")
async def save_scores(
    assessment_id: int, body: list[DimensionScoreRequest],
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MaturityService(db)
    result = await service.save_dimension_scores(assessment_id, body)
    return {"success": True, "data": result.model_dump()}


@router.post("/assessments/{assessment_id}/complete")
async def complete_assessment(
    assessment_id: int, body: AssessmentCompleteRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MaturityService(db)
    result = await service.complete_assessment(assessment_id, body)
    return {"success": True, "data": result.model_dump()}
