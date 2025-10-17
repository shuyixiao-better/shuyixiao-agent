#!/usr/bin/env python3
"""
启动 Web 界面服务

这个脚本会启动 FastAPI 服务，提供 Web 界面来与 Agent 交互
"""

import sys
import os
import socket

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 创建一个UDP socket来获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 不需要真正连接，只是为了获取本机IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

if __name__ == "__main__":
    import uvicorn
    
    port = 8001
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("🚀 启动 ShuYixiao Agent Web 界面")
    print("=" * 60)
    print()
    print("📍 服务地址:")
    print(f"   🏠 本地访问: http://localhost:{port}")
    if local_ip:
        print(f"   🌐 局域网访问: http://{local_ip}:{port}")
    print()
    print("📖 API 文档:")
    print(f"   🏠 本地访问: http://localhost:{port}/docs")
    if local_ip:
        print(f"   🌐 局域网访问: http://{local_ip}:{port}/docs")
    print()
    print("💡 提示: 局域网内其他设备可通过局域网IP访问此服务")
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "shuyixiao_agent.web_app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

