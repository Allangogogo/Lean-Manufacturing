"""
LeanOps 启动脚本

用法:
    python run.py              # 默认 0.0.0.0:8000
    python run.py --port 8080  # 自定义端口
    python run.py --reload     # 开发模式（热重载）
"""

from __future__ import annotations

import argparse

import uvicorn

from app.config import get_settings


def main():
    parser = argparse.ArgumentParser(description="LeanOps 精益运营管理系统")
    parser.add_argument("--host", default=None, help="绑定地址")
    parser.add_argument("--port", type=int, default=None, help="端口号")
    parser.add_argument("--reload", action="store_true", help="开发模式热重载")
    args = parser.parse_args()

    settings = get_settings()

    host = args.host or settings.SERVER_HOST
    port = args.port or settings.SERVER_PORT

    print(f"LeanOps v{settings.APP_VERSION} starting on {host}:{port}")
    print(f"API Docs: http://{host}:{port}/docs")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=args.reload or settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()
