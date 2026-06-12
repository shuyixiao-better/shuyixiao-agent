# ============================================
# 多阶段构建：第一阶段安装依赖
# ============================================
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml README.md requirements.txt ./

# 安装 Python 依赖（不安装项目本身，利用缓存）
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# ============================================
# 第二阶段：运行镜像
# ============================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从 builder 阶段复制已安装的 Python 包
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制项目文件
COPY pyproject.toml README.md ./
COPY src ./src
COPY run_web.py ./
COPY run_web_auto.py ./
COPY entrypoint.sh ./

# 安装项目本身（仅安装包引用，不重新安装依赖）
RUN pip install --no-deps -e .

# 创建必要目录（data 目录通过 volume 挂载）
RUN mkdir -p /app/data/chroma /app/data/memories

# 设置 entrypoint 脚本权限
RUN chmod +x /app/entrypoint.sh

# 暴露端口（可通过 PORT 环境变量修改）
EXPOSE ${PORT:-8000}

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -fsS http://127.0.0.1:${PORT:-8000}/api/health || exit 1

# 使用 entrypoint 脚本启动
ENTRYPOINT ["/app/entrypoint.sh"]
