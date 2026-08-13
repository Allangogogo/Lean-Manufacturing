"""
中间件模块

职责：
1. CORS 跨域配置
2. 请求日志
3. 操作审计日志（写操作自动记录）
"""

from __future__ import annotations

import json
import time
import logging
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger("leanops")


# ============================================================
# CORS 中间件
# ============================================================

def setup_cors(app: FastAPI) -> None:
    """配置 CORS 跨域。"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ============================================================
# 请求日志中间件
# ============================================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """记录每个请求的耗时和状态码。"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "%s %s %d %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response


# ============================================================
# 操作审计中间件
# ============================================================

# 需要审计的 HTTP 方法
AUDIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# 需要审计的路径前缀
AUDIT_PATH_PREFIXES = {"/api/v1/"}


class AuditLogMiddleware(BaseHTTPMiddleware):
    """自动记录写操作到审计日志。"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # 只审计写操作
        if request.method not in AUDIT_METHODS:
            return response

        # 只审计 API 路径
        if not any(request.url.path.startswith(p) for p in AUDIT_PATH_PREFIXES):
            return response

        # 异步记录审计日志（不阻塞响应）
        try:
            await self._log_audit(request, response)
        except Exception as e:
            logger.warning("审计日志记录失败: %s", e)

        return response

    async def _log_audit(self, request: Request, response: Response) -> None:
        """写入审计日志。"""
        from app.database import get_db_context
        from app.models.audit_log import AuditLog
        from app.core.security import get_user_id_from_token

        # 提取用户 ID
        token = request.cookies.get("leanops_token") or ""
        if not token:
            auth = request.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                token = auth[7:]
        user_id = get_user_id_from_token(token) if token else None

        # 解析路径中的资源和 ID
        path_parts = request.url.path.strip("/").split("/")
        resource = path_parts[2] if len(path_parts) > 2 else "unknown"
        resource_id = int(path_parts[3]) if len(path_parts) > 3 and path_parts[3].isdigit() else None

        # 映射 HTTP 方法到动作
        action_map = {
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
        }

        async with get_db_context() as db:
            log = AuditLog(
                user_id=user_id,
                action=action_map.get(request.method, request.method),
                resource=resource,
                resource_id=resource_id,
                detail=json.dumps({
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                }, ensure_ascii=False),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("User-Agent", "")[:255],
            )
            db.add(log)


# ============================================================
# 注册所有中间件
# ============================================================

def setup_middleware(app: FastAPI) -> None:
    """注册所有中间件（注意顺序：后添加的先执行）。"""
    setup_cors(app)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(AuditLogMiddleware)
