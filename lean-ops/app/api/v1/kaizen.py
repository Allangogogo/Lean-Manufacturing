"""
改善提案 API 接口

- GET    /kaizen           — 列表（筛选、分页）
- POST   /kaizen           — 创建提案
- GET    /kaizen/{id}      — 详情
- PUT    /kaizen/{id}      — 更新（草稿/退回状态）
- POST   /kaizen/{id}/action — 执行工作流操作
- POST   /kaizen/{id}/comment — 添加评论
- GET    /kaizen/stats     — 统计数据
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user
from app.schemas.kaizen import (
    KaizenActionRequest,
    KaizenCommentRequest,
    KaizenCreateRequest,
    KaizenUpdateRequest,
)
from app.services.kaizen_service import KaizenService

router = APIRouter()


@router.get("")
async def list_kaizen(
    status: Optional[str] = Query(None, description="状态筛选"),
    category: Optional[str] = Query(None, description="分类筛选"),
    submitter_id: Optional[int] = Query(None, description="提交者ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询改善提案列表。"""
    service = KaizenService(db)
    return await service.list_proposals(
        factory_id=user.factory_id,
        status=status,
        category=category,
        submitter_id=submitter_id,
        page=page,
        page_size=page_size,
    )


@router.post("")
async def create_kaizen(
    body: KaizenCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建改善提案。"""
    service = KaizenService(db)
    result = await service.create_proposal(
        data=body,
        user_id=user.id,
        factory_id=user.factory_id,
        department_id=user.department_id,
    )
    return {"success": True, "data": result.model_dump()}


@router.get("/stats")
async def kaizen_stats(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取提案统计数据。"""
    service = KaizenService(db)
    stats = await service.get_stats(user.factory_id)
    return stats.model_dump()


@router.get("/{proposal_id}")
async def get_kaizen(
    proposal_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取提案详情。"""
    service = KaizenService(db)
    result = await service.get_proposal(proposal_id)
    return {"success": True, "data": result.model_dump()}


@router.put("/{proposal_id}")
async def update_kaizen(
    proposal_id: int,
    body: KaizenUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新提案（仅草稿/退回状态可编辑）。"""
    service = KaizenService(db)
    result = await service.update_proposal(
        proposal_id=proposal_id,
        data=body,
        user_id=user.id,
    )
    return {"success": True, "data": result.model_dump()}


@router.post("/{proposal_id}/action")
async def kaizen_action(
    proposal_id: int,
    body: KaizenActionRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """执行工作流操作（提交/审批/拒绝/退回/开始实施/完成/关闭）。"""
    service = KaizenService(db)
    result = await service.execute_action(
        proposal_id=proposal_id,
        data=body,
        user_id=user.id,
        role_code=user.role_code,
    )
    return {"success": True, "data": result.model_dump()}


@router.post("/{proposal_id}/comment")
async def kaizen_comment(
    proposal_id: int,
    body: KaizenCommentRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加评论。"""
    service = KaizenService(db)
    result = await service.add_comment(
        proposal_id=proposal_id,
        data=body,
        user_id=user.id,
    )
    return {"success": True, "data": result.model_dump()}
