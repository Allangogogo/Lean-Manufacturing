# ============================================================
# LeanOps Dockerfile
# 多阶段构建：Python 3.11 slim + uvicorn
# ============================================================

FROM python:3.11-slim AS base

# 环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data /app/app/static/uploads

# 暴露端口
EXPOSE 8000

# 启动
CMD ["python", "run.py", "--host", "0.0.0.0", "--port", "8000"]
