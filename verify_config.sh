#!/bin/bash

# 验证数据库路径配置
# 
# 使用方法：bash verify_config.sh

set -e

echo "🔍 验证数据库路径配置"
echo "=" * 60
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 激活虚拟环境
if [ -d ".venv" ]; then
    echo "1️⃣  激活虚拟环境..."
    source .venv/bin/activate
    echo "   ✓ 虚拟环境已激活"
else
    echo "⚠️  未找到虚拟环境 (.venv)"
    exit 1
fi

# 验证配置
echo ""
echo "2️⃣  读取配置..."
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

from shuyixiao_agent.config import settings, PROJECT_ROOT
from pathlib import Path

print(f"   项目根目录: {PROJECT_ROOT}")
print(f"   数据库路径: {settings.vector_db_path}")
print()

# 验证路径
db_path = Path(settings.vector_db_path)
print("3️⃣  验证路径...")
print(f"   是绝对路径: {'✓' if db_path.is_absolute() else '✗'}")
print(f"   目录存在: {'✓' if db_path.exists() else '✗'}")
if db_path.exists():
    print(f"   可读: {'✓' if db_path.is_readable() else '✗'}")
    print(f"   可写: {'✓' if db_path.is_writable() else '✗'}")
print()

# 检查是否在项目目录内
if str(PROJECT_ROOT) in str(db_path):
    print("✅ 数据库路径正确配置在项目目录内")
else:
    print("⚠️  数据库路径不在项目目录内")

print()
print("4️⃣  配置摘要:")
print(f"   云端嵌入: {settings.use_cloud_embedding}")
print(f"   嵌入模型: {settings.cloud_embedding_model if settings.use_cloud_embedding else settings.embedding_model}")
print(f"   云端重排序: {settings.use_cloud_reranker}")
print(f"   对话模型: {settings.gitee_ai_model}")

EOF

echo ""
echo "=" * 60
echo "✅ 验证完成！"
echo ""

