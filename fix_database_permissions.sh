#!/bin/bash

# 修复 ChromaDB 数据库权限问题
# 
# 使用方法：bash fix_database_permissions.sh

set -e

echo "🔧 开始修复 ChromaDB 数据库权限问题..."
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 数据库目录
DB_DIR="./data/chroma"

# 1. 确保目录存在
echo "📁 检查数据库目录..."
if [ ! -d "$DB_DIR" ]; then
    echo "   ✓ 创建数据库目录: $DB_DIR"
    mkdir -p "$DB_DIR"
else
    echo "   ✓ 数据库目录已存在"
fi

# 2. 修复目录权限
echo ""
echo "🔐 修复目录权限..."
chmod 755 "$DB_DIR"
echo "   ✓ 目录权限已设置为 755"

# 3. 修复文件权限（如果文件存在）
if [ -f "$DB_DIR/chroma.sqlite3" ]; then
    echo ""
    echo "📝 修复数据库文件权限..."
    chmod 644 "$DB_DIR/chroma.sqlite3"
    echo "   ✓ 数据库文件权限已设置为 644"
else
    echo ""
    echo "ℹ️  数据库文件不存在（首次运行会自动创建）"
fi

# 4. 修复所有子目录和文件的权限
if [ -d "$DB_DIR" ] && [ "$(ls -A $DB_DIR)" ]; then
    echo ""
    echo "🔄 修复所有文件权限..."
    find "$DB_DIR" -type d -exec chmod 755 {} \;
    find "$DB_DIR" -type f -exec chmod 644 {} \;
    echo "   ✓ 所有文件权限已修复"
fi

# 5. 检查磁盘空间
echo ""
echo "💾 检查磁盘空间..."
df -h "$DB_DIR" | tail -1 | awk '{print "   可用空间: " $4 " (使用率: " $5 ")"}'

# 6. 显示当前权限
echo ""
echo "📊 当前权限状态："
ls -lah "$DB_DIR" | head -10

echo ""
echo "✅ 权限修复完成！"
echo ""
echo "💡 接下来的步骤："
echo "   1. 重新启动 Web 服务器: python run_web.py"
echo "   2. 尝试上传文本到知识库"
echo "   3. 如果仍有问题，请运行: bash reset_database.sh"
echo ""

