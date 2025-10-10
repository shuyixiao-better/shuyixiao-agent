#!/usr/bin/env python3
"""
启动 Web 界面服务

这个脚本会启动 FastAPI 服务，提供 Web 界面来与 Agent 交互
"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🚀 启动 ShuYixiao Agent Web 界面")
    print("=" * 60)
    print()
    print("📍 服务地址: http://localhost:8000")
    print("📖 API 文档: http://localhost:8000/docs")
    print()
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "shuyixiao_agent.web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

