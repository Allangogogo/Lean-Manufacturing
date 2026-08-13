# app/api/v1/project_dashboard.py
"""项目 KPI 仪表板 API。"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/{project_id}/dashboard")
async def get_project_dashboard(
    project_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DashboardService(db)
    data = await service.get_dashboard(project_id)
    return data
