#!/bin/bash
set -e

# ============================================
# ShuYixiao Agent 容器启动脚本
# ============================================

echo "=========================================="
echo "🚀 ShuYixiao Agent 容器启动中..."
echo "=========================================="

# 设置默认端口
PORT=${PORT:-8000}

# 确保数据目录存在
echo "📁 检查数据目录..."
mkdir -p /app/data/chroma /app/data/memories

# 检查目录权限
if [ ! -w /app/data ]; then
    echo "⚠️  警告: /app/data 目录没有写权限"
    echo "请确保 volume 挂载时设置了正确的权限"
fi

# 检查 API Key 配置
if [ -z "$GITEE_AI_API_KEY" ]; then
    echo "⚠️  警告: GITEE_AI_API_KEY 环境变量未设置"
    echo "请在 .env 文件或 docker-compose.yml 中配置 API Key"
    echo ""
    echo "获取 API Key: https://ai.gitee.com/dashboard/settings/tokens"
    echo ""
fi

# 显示配置信息
echo "📋 配置信息:"
echo "   端口: $PORT"
echo "   API Key: $(if [ -n "$GITEE_AI_API_KEY" ]; then echo '已配置'; else echo '未配置'; fi)"
echo "   模型: ${GITEE_AI_MODEL:-DeepSeek-V3}"
echo "   数据目录: /app/data"
echo ""

# 启动应用
echo "=========================================="
echo "🌐 启动 Web 服务 (端口: $PORT)..."
echo "=========================================="
echo ""

exec python -m uvicorn shuyixiao_agent.web_app:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --log-level info \
    --timeout-keep-alive 60 \
    --timeout-graceful-shutdown 30 \
    --access-log \
    --workers 1
