#!/bin/bash

# 一键修复 ChromaDB 数据库只读错误
# 
# 使用方法：bash quick_fix.sh

set -e

echo "🚀 一键修复 ChromaDB 数据库只读错误"
echo "=" * 60
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 1. 停止可能正在运行的服务器
echo "1️⃣  检查并停止正在运行的服务器..."
pkill -f "run_web.py" 2>/dev/null && echo "   ✓ 已停止运行中的服务器" || echo "   ℹ️  没有运行中的服务器"
sleep 1

# 2. 创建/修复数据库目录
echo ""
echo "2️⃣  创建/修复数据库目录..."
mkdir -p data/chroma
chmod 755 data/chroma
echo "   ✓ 目录权限已设置"

# 3. 修复现有文件权限
echo ""
echo "3️⃣  修复文件权限..."
if [ -d "data/chroma" ] && [ "$(ls -A data/chroma 2>/dev/null)" ]; then
    find data/chroma -type d -exec chmod 755 {} \;
    find data/chroma -type f -exec chmod 644 {} \;
    echo "   ✓ 所有文件权限已修复"
else
    echo "   ℹ️  目录为空（首次运行会自动创建）"
fi

# 4. 检查磁盘空间
echo ""
echo "4️⃣  检查磁盘空间..."
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
AVAIL_SPACE=$(df -h . | tail -1 | awk '{print $4}')
echo "   可用空间: $AVAIL_SPACE (使用率: $DISK_USAGE%)"
if [ "$DISK_USAGE" -gt 95 ]; then
    echo "   ⚠️  警告：磁盘空间不足！请清理磁盘"
else
    echo "   ✓ 磁盘空间充足"
fi

# 5. 清理临时文件
echo ""
echo "5️⃣  清理临时文件..."
find data/chroma -name "*.tmp" -type f -delete 2>/dev/null || true
find data/chroma -name "*-shm" -type f -delete 2>/dev/null || true
find data/chroma -name "*-wal" -type f -delete 2>/dev/null || true
echo "   ✓ 临时文件已清理"

# 6. 显示当前状态
echo ""
echo "6️⃣  当前状态："
if [ -d "data/chroma" ]; then
    ls -lah data/chroma | head -10
else
    echo "   ⚠️  目录不存在"
fi

echo ""
echo "=" * 60
echo "✅ 修复完成！"
echo ""
echo "📝 接下来的步骤："
echo ""
echo "   # 1. 激活虚拟环境（如果有）"
echo "   source .venv/bin/activate"
echo ""
echo "   # 2. 启动 Web 服务器"
echo "   python run_web.py"
echo ""
echo "   # 3. 访问 http://localhost:8000"
echo "   # 4. 尝试上传文本到知识库"
echo ""
echo "💡 如果仍有问题："
echo "   - 查看详细日志: tail -f logs/*.log"
echo "   - 运行诊断: python diagnose_database.py"  
echo "   - 完全重置: bash reset_database.sh"
echo ""

