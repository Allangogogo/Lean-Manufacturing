"""风险管理 API。"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user
from app.services.risk_service import RiskService

router = APIRouter()


class RiskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    probability: str = Field("medium", description="low/medium/high/critical")
    impact: str = Field("medium", description="low/medium/high/critical")
    status: str = Field("identified")
    response_plan: Optional[str] = None
    mitigation_actions: Optional[str] = None


class RiskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    probability: Optional[str] = None
    impact: Optional[str] = None
    status: Optional[str] = None
    response_plan: Optional[str] = None
    mitigation_actions: Optional[str] = None


@router.get("/{project_id}/risks")
async def list_risks(
    project_id: int,
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = RiskService(db)
    return await service.list_risks(project_id, status=status, page=page, page_size=page_size)


@router.get("/{project_id}/risks/matrix")
async def get_risk_matrix(
    project_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = RiskService(db)
    return await service.get_matrix(project_id)


@router.post("/{project_id}/risks")
async def create_risk(
    project_id: int, body: RiskCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = RiskService(db)
    risk = await service.create_risk(project_id, body.model_dump(), user.id)
    return {"success": True, "data": {"id": risk.id, "title": risk.title}}


@router.put("/{project_id}/risks/{risk_id}")
async def update_risk(
    project_id: int, risk_id: int, body: RiskUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = RiskService(db)
    risk = await service.update_risk(project_id, risk_id, body.model_dump(exclude_unset=True))
    return {"success": True, "data": {"id": risk.id, "status": risk.status}}


@router.delete("/{project_id}/risks/{risk_id}")
async def delete_risk(
    project_id: int, risk_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = RiskService(db)
    await service.delete_risk(project_id, risk_id)
    return {"success": True, "message": "风险已删除"}
