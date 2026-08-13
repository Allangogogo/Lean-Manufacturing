"""甘特图 API。"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.permissions import CurrentUser, get_current_user
from app.services.gantt_service import GanttService

router = APIRouter()


class GanttUpdateRequest(BaseModel):
    start: str
    end: str


@router.get("/{project_id}/gantt")
async def get_gantt(
    project_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = GanttService(db)
    data = await service.get_gantt_data(project_id)
    return data


@router.patch("/{project_id}/tasks/{task_id}/gantt")
async def update_gantt_task(
    project_id: int, task_id: int, body: GanttUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = GanttService(db)
    result = await service.update_task_dates(project_id, task_id, body.start, body.end)
    return {"success": True, "data": result}
