#!/bin/bash

# 清理所有旧的 ChromaDB 数据
# 
# 使用方法：bash clean_old_data.sh

set -e

echo "🗑️  清理旧的 ChromaDB 数据"
echo "=" * 60
echo ""

# 进入项目目录
cd "$(dirname "$0")"
PROJECT_ROOT="/Users/shuyixiao/PycharmProjects/shuyixiao-agent"

echo "📁 项目根目录: $PROJECT_ROOT"
echo ""

# 1. 停止可能正在运行的服务器
echo "1️⃣  检查并停止正在运行的服务器..."
pkill -f "run_web.py" 2>/dev/null && echo "   ✓ 已停止运行中的服务器" || echo "   ℹ️  没有运行中的服务器"
sleep 1

# 2. 备份现有数据（如果存在）
BACKUP_DIR="$PROJECT_ROOT/data/chroma_backup_$(date +%Y%m%d_%H%M%S)"
if [ -d "$PROJECT_ROOT/data/chroma" ] && [ "$(ls -A $PROJECT_ROOT/data/chroma 2>/dev/null)" ]; then
    echo ""
    echo "2️⃣  备份现有数据..."
    mkdir -p "$BACKUP_DIR"
    cp -r "$PROJECT_ROOT/data/chroma"/* "$BACKUP_DIR/" 2>/dev/null || true
    echo "   ✓ 备份到: $BACKUP_DIR"
else
    echo ""
    echo "2️⃣  没有现有数据需要备份"
fi

# 3. 查找并清理可能的其他位置的数据
echo ""
echo "3️⃣  查找并清理其他位置的数据..."

# 查找用户目录下的 ChromaDB 数据（排除备份目录）
FOUND_FILES=$(find ~ -type f -name "chroma.sqlite3" 2>/dev/null | grep -v "chroma_backup_" | grep -v "Library" || true)

if [ -n "$FOUND_FILES" ]; then
    echo "   找到以下数据库文件："
    echo "$FOUND_FILES" | while read -r file; do
        echo "   - $file"
    done
    echo ""
    read -p "   是否删除这些文件？(y/N): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        echo "$FOUND_FILES" | while read -r file; do
            rm -f "$file"
            # 同时删除相关的 WAL 和 SHM 文件
            rm -f "${file}-wal" "${file}-shm"
            echo "   ✓ 已删除: $file"
        done
    else
        echo "   ⊘ 跳过删除"
    fi
else
    echo "   ℹ️  没有找到其他位置的数据库文件"
fi

# 4. 清空项目数据目录
echo ""
echo "4️⃣  清空项目数据目录..."
if [ -d "$PROJECT_ROOT/data/chroma" ]; then
    rm -rf "$PROJECT_ROOT/data/chroma"/*
    echo "   ✓ 已清空: $PROJECT_ROOT/data/chroma/"
else
    echo "   ℹ️  目录不存在"
fi

# 5. 重新创建干净的目录
echo ""
echo "5️⃣  创建新的数据目录..."
mkdir -p "$PROJECT_ROOT/data/chroma"
chmod 755 "$PROJECT_ROOT/data/chroma"
echo "   ✓ 目录已创建: $PROJECT_ROOT/data/chroma"
echo "   ✓ 权限已设置: 755"

# 6. 清理临时文件和缓存
echo ""
echo "6️⃣  清理临时文件..."
find "$PROJECT_ROOT" -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -name ".DS_Store" -delete 2>/dev/null || true
echo "   ✓ Python 缓存已清理"

# 7. 验证配置
echo ""
echo "7️⃣  验证配置..."
if grep -q "PROJECT_ROOT" "$PROJECT_ROOT/src/shuyixiao_agent/config.py"; then
    echo "   ✓ 配置文件已更新（使用项目根目录）"
else
    echo "   ⚠️  配置文件可能需要手动检查"
fi

# 8. 显示最终状态
echo ""
echo "8️⃣  最终状态："
echo "   数据库路径: $PROJECT_ROOT/data/chroma"
ls -la "$PROJECT_ROOT/data/chroma" 2>/dev/null | head -10 || echo "   (空目录)"

if [ -d "$BACKUP_DIR" ]; then
    echo ""
    echo "   备份位置: $BACKUP_DIR"
    du -sh "$BACKUP_DIR" 2>/dev/null || true
fi

echo ""
echo "=" * 60
echo "✅ 清理完成！"
echo ""
echo "📝 接下来的步骤："
echo ""
echo "   # 1. 激活虚拟环境"
echo "   source .venv/bin/activate"
echo ""
echo "   # 2. 启动 Web 服务器"
echo "   python run_web.py"
echo ""
echo "   # 3. 访问 http://localhost:8000"
echo "   # 4. 重新上传文档到知识库"
echo ""
echo "💡 数据库现在将固定保存在："
echo "   $PROJECT_ROOT/data/chroma/"
echo ""
if [ -d "$BACKUP_DIR" ]; then
    echo "🔖 如需恢复旧数据："
    echo "   cp -r $BACKUP_DIR/* $PROJECT_ROOT/data/chroma/"
    echo ""
fi

