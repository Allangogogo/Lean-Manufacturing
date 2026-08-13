"""
全局异常处理模块

职责：
1. 定义业务异常类
2. 注册 FastAPI 全局异常处理器
3. 统一错误响应格式
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError


# ============================================================
# 业务异常类
# ============================================================

class AppError(Exception):
    """业务异常基类。"""

    def __init__(
        self,
        message: str = "操作失败",
        code: str = "APP_ERROR",
        status_code: int = 400,
        detail: Optional[Any] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class NotFoundError(AppError):
    """资源不存在。"""

    def __init__(self, resource: str = "资源", resource_id: Any = None):
        msg = f"{resource}不存在" if resource_id is None else f"{resource} (ID={resource_id}) 不存在"
        super().__init__(
            message=msg,
            code="NOT_FOUND",
            status_code=404,
        )


class ForbiddenError(AppError):
    """权限不足。"""

    def __init__(self, message: str = "权限不足，无法执行此操作"):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
        )


class ConflictError(AppError):
    """数据冲突（如重复提交）。"""

    def __init__(self, message: str = "数据冲突"):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
        )


class ValidationError_(AppError):
    """业务校验失败。"""

    def __init__(self, message: str = "数据校验失败", detail: Any = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            detail=detail,
        )


class WorkflowError(AppError):
    """工作流状态转换错误。"""

    def __init__(self, message: str = "当前状态不允许此操作"):
        super().__init__(
            message=message,
            code="WORKFLOW_ERROR",
            status_code=400,
        )


# ============================================================
# 错误响应格式
# ============================================================

def error_response(
    message: str,
    code: str = "ERROR",
    status_code: int = 400,
    detail: Any = None,
) -> JSONResponse:
    """统一错误响应格式。"""
    body = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
    if detail is not None:
        body["error"]["detail"] = detail
    return JSONResponse(
        status_code=status_code,
        content=body,
    )


# ============================================================
# 注册全局异常处理器
# ============================================================

def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。"""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return error_response(
            message=exc.message,
            code=exc.code,
            status_code=exc.status_code,
            detail=exc.detail,
        )

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException):
        return error_response(
            message=str(exc.detail),
            code="HTTP_ERROR",
            status_code=exc.status_code,
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return error_response(
            message="请求参数校验失败",
            code="VALIDATION_ERROR",
            status_code=422,
            detail=exc.errors(),
        )

    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception):
        return error_response(
            message="服务器内部错误",
            code="INTERNAL_ERROR",
            status_code=500,
        )
