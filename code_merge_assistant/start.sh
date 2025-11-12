#!/bin/bash
# macOS/Linux 快速启动脚本

echo "🔀 代码合并辅助工具 - 启动中..."
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 未检测到 Python3，请先安装 Python"
    exit 1
fi

# 检查依赖是否安装
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 正在安装依赖..."
    pip3 install -r requirements.txt
fi

echo "✅ 依赖检查完成"
echo ""
echo "🚀 启动 Web 界面..."
echo "📍 访问地址: http://localhost:5678"
echo "💡 按 Ctrl+C 停止服务"
echo ""

python3 web_ui.py
