"""
LeanOps 精益运营管理系统 — FastAPI 应用入口

职责：
1. 创建 FastAPI 应用实例
2. 注册中间件（CORS、日志、审计）
3. 注册异常处理器
4. 注册路由
5. 生命周期管理（启动/关闭）
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.middleware import setup_middleware

settings = get_settings()

# 日志配置
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("leanops")


# ============================================================
# 生命周期
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库，关闭时释放连接。"""
    # 启动
    logger.info("LeanOps v%s 启动中... (env=%s)", settings.APP_VERSION, settings.APP_ENV)

    from app.database import init_db
    await init_db()
    logger.info("数据库初始化完成")

    yield

    # 关闭
    from app.database import close_db
    await close_db()
    logger.info("LeanOps 已关闭")


# ============================================================
# 创建应用
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="精益运营管理系统 — 企业级精益管理 Web 应用",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)

# 注册中间件
setup_middleware(app)

# 注册异常处理器
register_exception_handlers(app)

# 静态文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# ============================================================
# 注册路由
# ============================================================

from app.api.v1.router import api_router  # noqa: E402

app.include_router(api_router, prefix="/api/v1")


# ============================================================
# 页面路由（Jinja2 模板）
# ============================================================

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页 — 重定向到仪表板。"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录页。"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """仪表板。"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/kaizen", response_class=HTMLResponse)
async def kaizen_list_page(request: Request):
    """改善提案列表。"""
    return templates.TemplateResponse("kaizen/list.html", {"request": request})


@app.get("/kaizen/create", response_class=HTMLResponse)
async def kaizen_create_page(request: Request):
    """新建改善提案。"""
    return templates.TemplateResponse("kaizen/create.html", {"request": request})


@app.get("/kaizen/{proposal_id}", response_class=HTMLResponse)
async def kaizen_detail_page(request: Request, proposal_id: int):
    """改善提案详情。"""
    return templates.TemplateResponse("kaizen/detail.html", {"request": request})


@app.get("/fives", response_class=HTMLResponse)
async def fives_list_page(request: Request):
    """5S 审核列表。"""
    return templates.TemplateResponse("fives/list.html", {"request": request})


@app.get("/fives/audit/{audit_id}", response_class=HTMLResponse)
async def fives_audit_page(request: Request, audit_id: int):
    """5S 审核评分。"""
    return templates.TemplateResponse("fives/audit_form.html", {"request": request})


@app.get("/fives/improvements", response_class=HTMLResponse)
async def fives_improvements_page(request: Request):
    """5S 改善跟踪。"""
    return templates.TemplateResponse("fives/improvements.html", {"request": request})


@app.get("/training", response_class=HTMLResponse)
async def training_list_page(request: Request):
    """培训列表。"""
    return templates.TemplateResponse("training/sessions.html", {"request": request})


@app.get("/training/session/{session_id}", response_class=HTMLResponse)
async def training_detail_page(request: Request, session_id: int):
    """培训详情。"""
    return templates.TemplateResponse("training/detail.html", {"request": request})


@app.get("/tpm", response_class=HTMLResponse)
async def tpm_equipment_page(request: Request):
    """设备台账。"""
    return templates.TemplateResponse("tpm/equipment.html", {"request": request})


@app.get("/tpm/faults", response_class=HTMLResponse)
async def tpm_faults_page(request: Request):
    """故障管理。"""
    return templates.TemplateResponse("tpm/faults.html", {"request": request})


@app.get("/projects", response_class=HTMLResponse)
async def projects_list_page(request: Request):
    """项目列表。"""
    return templates.TemplateResponse("project/list.html", {"request": request})


@app.get("/project/{project_id}", response_class=HTMLResponse)
async def project_detail_page(request: Request, project_id: int):
    """项目详情。"""
    return templates.TemplateResponse("project/detail.html", {"request": request})


@app.get("/project/{project_id}/gantt", response_class=HTMLResponse)
async def project_gantt_page(request: Request, project_id: int):
    """项目甘特图。"""
    return templates.TemplateResponse("project/gantt.html", {"request": request})


@app.get("/project/{project_id}/dashboard", response_class=HTMLResponse)
async def project_dashboard_page(request: Request, project_id: int):
    """项目 KPI 仪表板。"""
    return templates.TemplateResponse("project/dashboard.html", {"request": request})


@app.get("/project/{project_id}/risks", response_class=HTMLResponse)
async def project_risks_page(request: Request, project_id: int):
    """项目风险管理。"""
    return templates.TemplateResponse("project/risks.html", {"request": request})


@app.get("/practices", response_class=HTMLResponse)
async def practices_list_page(request: Request):
    """最佳实践库。"""
    return templates.TemplateResponse("practice/list.html", {"request": request})


@app.get("/practice/{practice_id}", response_class=HTMLResponse)
async def practice_detail_page(request: Request, practice_id: int):
    """最佳实践详情。"""
    return templates.TemplateResponse("practice/detail.html", {"request": request})


@app.get("/maturity", response_class=HTMLResponse)
async def maturity_list_page(request: Request):
    """成熟度评估列表。"""
    return templates.TemplateResponse("maturity/list.html", {"request": request})


@app.get("/maturity/assessment/{assessment_id}", response_class=HTMLResponse)
async def maturity_assessment_page(request: Request, assessment_id: int):
    """成熟度评估打分。"""
    return templates.TemplateResponse("maturity/assessment_form.html", {"request": request})


@app.get("/maturity/trends", response_class=HTMLResponse)
async def maturity_trends_page(request: Request):
    """成熟度历史趋势。"""
    return templates.TemplateResponse("maturity/trends.html", {"request": request})


@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(request: Request):
    """用户管理。"""
    return templates.TemplateResponse("admin/users.html", {"request": request})


@app.get("/reports", response_class=HTMLResponse)
async def reports_center_page(request: Request):
    """报表中心。"""
    return templates.TemplateResponse("reports/center.html", {"request": request})


# ============================================================
# 健康检查
# ============================================================

@app.get("/health")
async def health_check():
    """健康检查端点。"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV,
    }
