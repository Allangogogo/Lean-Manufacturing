"""
项目管理请求/响应模型
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# 请求模型
# ============================================================

class ProjectCreateRequest(BaseModel):
    """创建项目。"""
    name: str = Field(..., min_length=1, max_length=200, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    project_type: str = Field(..., description="类型: kaizen_event/vsm_redux/5s_deployment/tpm_rollout/training_program")
    priority: str = Field("medium", description="优先级: low/medium/high/urgent")
    start_date: Optional[date] = Field(None, description="开始日期")
    target_end_date: Optional[date] = Field(None, description="目标结束日期")
    budget: Decimal = Field(Decimal("0"), description="预算")
    scope: Optional[str] = Field(None, description="项目范围")
    objectives: Optional[str] = Field(None, description="项目目标")
    success_criteria: Optional[str] = Field(None, description="成功标准")
    lean20_dimensions: Optional[List[str]] = Field(None, description="Lean 2.0 dimension tags: O/D/G/R/H")


class ProjectUpdateRequest(BaseModel):
    """更新项目。"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    target_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    scope: Optional[str] = None
    objectives: Optional[str] = None
    success_criteria: Optional[str] = None
    lean20_dimensions: Optional[List[str]] = Field(None, description="Lean 2.0 dimension tags: O/D/G/R/H")
    source_assessment_id: Optional[int] = Field(None, description="ID of the assessment that created this project")


class MilestoneCreateRequest(BaseModel):
    """创建里程碑。"""
    name: str = Field(..., min_length=1, max_length=200, description="里程碑名称")
    description: Optional[str] = Field(None, description="描述")
    target_date: Optional[date] = Field(None, description="目标日期")
    sort_order: int = Field(0, description="排序")


class TaskCreateRequest(BaseModel):
    """创建任务。"""
    name: str = Field(..., min_length=1, max_length=200, description="任务名称")
    description: Optional[str] = Field(None, description="描述")
    milestone_id: Optional[int] = Field(None, description="关联里程碑")
    assigned_to_id: Optional[int] = Field(None, description="负责人 ID")
    priority: str = Field("medium", description="优先级")
    due_date: Optional[date] = Field(None, description="截止日期")
    estimated_hours: Optional[Decimal] = Field(None, description="预估工时")
    depends_on_ids: List[int] = Field(default_factory=list, description="前置任务 ID 列表")


class TaskUpdateRequest(BaseModel):
    """更新任务。"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    milestone_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    actual_hours: Optional[Decimal] = None
    depends_on_ids: Optional[List[int]] = Field(None, description="前置任务 ID 列表")


class MilestoneUpdateRequest(BaseModel):
    """更新里程碑。"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    target_date: Optional[date] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None


class MemberAddRequest(BaseModel):
    """添加成员。"""
    user_id: int = Field(..., description="用户 ID")
    role: str = Field("member", description="角色: owner/member/consultant")


class UpdateCreateRequest(BaseModel):
    """提交周报。"""
    update_date: date = Field(..., description="日期")
    progress_pct: int = Field(0, ge=0, le=100, description="进度百分比")
    accomplishments: Optional[str] = Field(None, description="本周成果")
    plan_next_week: Optional[str] = Field(None, description="下周计划")
    risks_issues: Optional[str] = Field(None, description="风险问题")


# ============================================================
# 响应模型
# ============================================================

class MilestoneResponse(BaseModel):
    """里程碑响应。"""
    id: int
    name: str
    description: Optional[str] = None
    target_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: str = "pending"
    sort_order: int = 0
    task_count: int = 0
    completed_tasks: int = 0


class TaskResponse(BaseModel):
    """任务响应。"""
    id: int
    name: str
    description: Optional[str] = None
    milestone_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    assigned_to_name: str = ""
    status: str = "todo"
    priority: str = "medium"
    due_date: Optional[date] = None
    completed_date: Optional[date] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    depends_on_ids: List[int] = Field(default_factory=list)


class MemberResponse(BaseModel):
    """成员响应。"""
    id: int
    user_id: int
    user_name: str = ""
    role: str = "member"
    joined_at: Optional[datetime] = None


class UpdateResponse(BaseModel):
    """周报响应。"""
    id: int
    author_name: str = ""
    update_date: date
    progress_pct: int = 0
    accomplishments: Optional[str] = None
    plan_next_week: Optional[str] = None
    risks_issues: Optional[str] = None
    created_at: Optional[datetime] = None


class ProjectDetailResponse(BaseModel):
    """项目详情响应。"""
    id: int
    name: str
    description: Optional[str] = None
    project_type: str
    owner_name: str = ""
    factory_id: int
    status: str
    priority: str
    start_date: Optional[date] = None
    target_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    budget: Decimal = Decimal("0")
    actual_cost: Decimal = Decimal("0")
    scope: Optional[str] = None
    objectives: Optional[str] = None
    success_criteria: Optional[str] = None
    lean20_dimensions: Optional[List[str]] = None
    source_assessment_id: Optional[int] = None
    created_at: Optional[datetime] = None
    milestones: List[MilestoneResponse] = []
    tasks: List[TaskResponse] = []
    members: List[MemberResponse] = []
    updates: List[UpdateResponse] = []


class ProjectListItem(BaseModel):
    """项目列表项。"""
    id: int
    name: str
    project_type: str
    owner_name: str = ""
    status: str
    priority: str
    start_date: Optional[date] = None
    target_end_date: Optional[date] = None
    progress_pct: int = 0
    task_count: int = 0
    completed_tasks: int = 0
    health_level: str = ""
    lean20_dimensions: Optional[List[str]] = None
    source_assessment_id: Optional[int] = None


class ProjectStatsResponse(BaseModel):
    """项目统计。"""
    total: int = 0
    planning: int = 0
    active: int = 0
    on_hold: int = 0
    completed: int = 0
    total_budget: float = 0.0
    total_actual_cost: float = 0.0
    dimension_counts: Optional[dict] = None
