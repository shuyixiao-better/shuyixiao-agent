#!/bin/bash

# 重置 ChromaDB 数据库（清空所有数据）
# 
# ⚠️ 警告：此操作将删除所有知识库数据，无法恢复！
# 
# 使用方法：bash reset_database.sh

set -e

echo "⚠️  警告：此操作将删除所有知识库数据！"
echo ""
read -p "确定要继续吗？(输入 YES 确认): " confirm

if [ "$confirm" != "YES" ]; then
    echo "❌ 操作已取消"
    exit 0
fi

echo ""
echo "🗑️  开始重置数据库..."
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 数据库目录
DB_DIR="./data/chroma"

# 1. 备份旧数据库（如果存在）
if [ -d "$DB_DIR" ] && [ "$(ls -A $DB_DIR)" ]; then
    BACKUP_DIR="./data/chroma_backup_$(date +%Y%m%d_%H%M%S)"
    echo "📦 备份旧数据到: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    cp -r "$DB_DIR"/* "$BACKUP_DIR/" 2>/dev/null || true
    echo "   ✓ 备份完成"
    echo ""
fi

# 2. 删除旧数据库
echo "🗑️  删除旧数据库..."
if [ -d "$DB_DIR" ]; then
    rm -rf "$DB_DIR"
    echo "   ✓ 旧数据库已删除"
else
    echo "   ℹ️  数据库目录不存在"
fi

# 3. 重新创建目录
echo ""
echo "📁 创建新的数据库目录..."
mkdir -p "$DB_DIR"
chmod 755 "$DB_DIR"
echo "   ✓ 目录创建完成"

# 4. 设置正确的权限
echo ""
echo "🔐 设置目录权限..."
chmod 755 "$DB_DIR"
echo "   ✓ 权限设置完成"

# 5. 验证
echo ""
echo "✅ 数据库重置完成！"
echo ""
echo "📊 当前状态："
ls -lah "$DB_DIR"
echo ""
echo "💡 接下来的步骤："
echo "   1. 重新启动 Web 服务器: python run_web.py"
echo "   2. 重新上传文档到知识库"
if [ -d "./data/chroma_backup_"* ]; then
    echo "   3. 如需恢复，备份文件在: data/chroma_backup_*"
fi
echo ""

