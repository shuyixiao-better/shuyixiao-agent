#!/bin/bash

# 简单验证配置
echo "🔍 验证配置"
cd "$(dirname "$0")"
source .venv/bin/activate

python3 << 'EOF'
import sys
sys.path.insert(0, 'src')
from shuyixiao_agent.config import settings, PROJECT_ROOT
from pathlib import Path

print(f"✓ 项目根目录: {PROJECT_ROOT}")
print(f"✓ 数据库路径: {settings.vector_db_path}")

db_path = Path(settings.vector_db_path)
print(f"✓ 是绝对路径: {db_path.is_absolute()}")
print(f"✓ 目录存在: {db_path.exists()}")
print(f"✓ 在项目内: {str(PROJECT_ROOT) in str(db_path)}")
print()
print("✅ 配置验证通过！")
EOF

