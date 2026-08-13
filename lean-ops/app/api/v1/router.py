"""
API v1 路由聚合

所有 /api/v1/ 下的路由在此注册。
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.kaizen import router as kaizen_router
from app.api.v1.fives import router as fives_router
from app.api.v1.training import router as training_router
from app.api.v1.tpm import router as tpm_router
from app.api.v1.projects import router as projects_router
from app.api.v1.practices import router as practices_router
from app.api.v1.maturity import router as maturity_router
from app.api.v1.admin import router as admin_router
from app.api.v1.reports import router as reports_router
from app.api.v1 import gantt as gantt_router

api_router = APIRouter()

# 认证
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])

# 仪表板
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["仪表板"])

# 改善提案
api_router.include_router(kaizen_router, prefix="/kaizen", tags=["改善提案"])

# 5S 审核
api_router.include_router(fives_router, prefix="/fives", tags=["5S审核"])

# 培训管理
api_router.include_router(training_router, prefix="/training", tags=["培训管理"])

# TPM 设备管理
api_router.include_router(tpm_router, prefix="/tpm", tags=["TPM设备"])

# 项目管理
api_router.include_router(projects_router, prefix="/projects", tags=["项目管理"])

# Best Practice 管理
api_router.include_router(practices_router, prefix="/practices", tags=["Best Practice"])

# 成熟度评估
api_router.include_router(maturity_router, prefix="/maturity", tags=["成熟度评估"])

# 系统管理
api_router.include_router(admin_router, prefix="/admin", tags=["系统管理"])

# 报表中心
api_router.include_router(reports_router, prefix="/reports", tags=["报表中心"])

# 甘特图
api_router.include_router(gantt_router.router, prefix="/projects", tags=["gantt"])

# 项目仪表板
from app.api.v1 import project_dashboard as project_dashboard_router
api_router.include_router(project_dashboard_router.router, prefix="/projects", tags=["project-dashboard"])

# 风险管理
from app.api.v1 import risks as risks_router
api_router.include_router(risks_router.router, prefix="/projects", tags=["risks"])

# Lean 2.0 成熟度评估 (Industry 5.0 扩展维度)
from app.api.v1.lean20 import router as lean20_router
api_router.include_router(lean20_router, prefix="/lean20", tags=["Lean2.0成熟度"])

# Value Pillars (Better / Faster / Closer)
from app.api.v1.pillars import router as pillars_router
api_router.include_router(pillars_router, prefix="/pillars", tags=["价值支柱"])

# Automation Maturity & ROI
from app.api.v1.automation import router as automation_router
api_router.include_router(automation_router, prefix="/automation", tags=["自动化成熟度"])
