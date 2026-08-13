"""
Best Practice 管理 API 接口

- GET    /practices             — 最佳实践列表
- POST   /practices             — 提交实践
- GET    /practices/popular     — 热门实践排行
- GET    /practices/stats       — 统计数据
- GET    /practices/{id}        — 实践详情
- PUT    /practices/{id}        — 更新实践
- POST   /practices/{id}/publish — 发布
- POST   /practices/{id}/vote   — 点赞/收藏
- POST   /practices/{id}/comment — 添加评论
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user
from app.schemas.practice import (
    CommentCreateRequest,
    PracticeCreateRequest,
    PracticeUpdateRequest,
    VoteRequest,
)
from app.services.practice_service import PracticeService

router = APIRouter()


@router.get("")
async def list_practices(
    category: Optional[str] = Query(None, description="类别筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: str = Query("newest", description="排序: newest/popular/saving"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PracticeService(db)
    return await service.list_practices(
        factory_id=user.factory_id, category=category, status=status,
        keyword=keyword, sort_by=sort_by, page=page, page_size=page_size,
    )


@router.post("")
async def create_practice(
    body: PracticeCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PracticeService(db)
    result = await service.create_practice(data=body, user_id=user.id, factory_id=user.factory_id)
    return {"success": True, "data": result.model_dump()}


@router.get("/stats")
async def practice_stats(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PracticeService(db)
    return (await service.get_stats(user.factory_id)).model_dump()


@router.get("/popular")
async def popular_practices(
    limit: int = Query(10, ge=1, le=50),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PracticeService(db)
    result = await service.list_practices(
        factory_id=user.factory_id, status="published",
        sort_by="popular", page=1, page_size=limit,
    )
    return result.model_dump()


@router.get("/{practice_id}")
async def get_practice(
    practice_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PracticeService(db)
    result = await service.get_practice(practice_id, user_id=user.id)
    return {"success": True, "data": result.model_dump()}


@router.put("/{practice_id}")
async def update_practice(
    practice_id: int, body: PracticeUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PracticeService(db)
    result = await service.update_practice(practice_id=practice_id, data=body, user_id=user.id)
    return {"success": True, "data": result.model_dump()}


@router.post("/{practice_id}/publish")
async def publish_practice(
    practice_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PracticeService(db)
    result = await service.publish_practice(practice_id, user_id=user.id)
    return {"success": True, "data": result.model_dump()}


@router.post("/{practice_id}/vote")
async def vote_practice(
    practice_id: int, body: VoteRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PracticeService(db)
    result = await service.toggle_vote(practice_id=practice_id, data=body, user_id=user.id)
    return {"success": True, "data": result.model_dump()}


@router.post("/{practice_id}/comment")
async def comment_practice(
    practice_id: int, body: CommentCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PracticeService(db)
    result = await service.add_comment(practice_id=practice_id, data=body, user_id=user.id)
    return {"success": True, "data": result.model_dump()}
