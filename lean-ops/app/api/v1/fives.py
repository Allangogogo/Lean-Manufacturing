"""
5S 审核 API 接口

- GET    /fives/areas           — 区域列表
- GET    /fives/audits          — 审核列表（筛选、分页）
- POST   /fives/audits          — 创建审核计划
- GET    /fives/audits/{id}     — 审核详情
- PUT    /fives/audits/{id}/scores — 保存评分
- POST   /fives/audits/{id}/complete — 完成审核
- GET    /fives/stats           — 统计数据
- GET    /fives/improvements    — 改善项列表
- POST   /fives/audits/{id}/improvements — 创建改善项
- PUT    /fives/improvements/{id} — 更新改善项
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user
from app.schemas.fives import (
    FiveSAuditCreateRequest,
    FiveSAuditScoreRequest,
    FiveSImprovementCreateRequest,
    FiveSImprovementUpdateRequest,
)
from app.services.fives_service import FiveSService

router = APIRouter()


@router.get("/areas")
async def list_areas(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取 5S 区域列表。"""
    service = FiveSService(db)
    items = await service.list_areas(user.factory_id)
    return {"success": True, "data": items}


@router.get("/audits")
async def list_audits(
    status: Optional[str] = Query(None, description="状态筛选"),
    audit_type: Optional[str] = Query(None, description="类型筛选"),
    area_id: Optional[int] = Query(None, description="区域筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询审核列表。"""
    service = FiveSService(db)
    return await service.list_audits(
        factory_id=user.factory_id,
        status=status,
        audit_type=audit_type,
        area_id=area_id,
        page=page,
        page_size=page_size,
    )


@router.post("/audits")
async def create_audit(
    body: FiveSAuditCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建审核计划。"""
    service = FiveSService(db)
    result = await service.create_audit(
        data=body,
        user_id=user.id,
        factory_id=user.factory_id,
    )
    return {"success": True, "data": result.model_dump()}


@router.get("/stats")
async def fives_stats(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取审核统计。"""
    service = FiveSService(db)
    stats = await service.get_stats(user.factory_id)
    return stats.model_dump()


@router.get("/improvements")
async def list_improvements(
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询改善项列表。"""
    service = FiveSService(db)
    return await service.list_improvements(
        factory_id=user.factory_id,
        status=status,
        page=page,
        page_size=page_size,
    )


@router.get("/audits/{audit_id}")
async def get_audit(
    audit_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取审核详情。"""
    service = FiveSService(db)
    result = await service.get_audit(audit_id)
    return {"success": True, "data": result.model_dump()}


@router.put("/audits/{audit_id}/scores")
async def save_scores(
    audit_id: int,
    body: FiveSAuditScoreRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """保存审核评分。"""
    service = FiveSService(db)
    result = await service.save_scores(
        audit_id=audit_id,
        data=body,
        user_id=user.id,
    )
    return {"success": True, "data": result.model_dump()}


@router.post("/audits/{audit_id}/complete")
async def complete_audit(
    audit_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """完成审核。"""
    service = FiveSService(db)
    result = await service.complete_audit(
        audit_id=audit_id,
        user_id=user.id,
    )
    return {"success": True, "data": result.model_dump()}


@router.post("/audits/{audit_id}/improvements")
async def create_improvement(
    audit_id: int,
    body: FiveSImprovementCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建改善项。"""
    service = FiveSService(db)
    result = await service.create_improvement(
        audit_id=audit_id,
        data=body,
        user_id=user.id,
        factory_id=user.factory_id,
    )
    return {"success": True, "data": result.model_dump()}


@router.put("/improvements/{improvement_id}")
async def update_improvement(
    improvement_id: int,
    body: FiveSImprovementUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新改善项。"""
    service = FiveSService(db)
    result = await service.update_improvement(
        improvement_id=improvement_id,
        data=body,
        user_id=user.id,
    )
    return {"success": True, "data": result.model_dump()}
