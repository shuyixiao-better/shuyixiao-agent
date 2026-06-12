#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动 Web 界面服务（自动化版本）

特点：
- ✅ 自动检测并使用可用端口
- ✅ 无需用户交互
- ✅ 完整的诊断日志
"""

import sys
import os
import socket

# 设置 Windows 控制台支持 UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

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

def is_port_available(port):
    """检查端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('localhost', port))
        return result != 0

def find_available_port(start_port=8000, max_attempts=10):
    """查找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    return None

def main():
    print("=" * 70)
    print("🚀 启动 ShuYixiao Agent Web 界面（自动化版）")
    print("=" * 70)
    print()

    # 检查 API Key
    try:
        from shuyixiao_agent.config import settings

        if not settings.gitee_ai_api_key:
            print("⚠️  警告: API Key 未配置")
            print()
            print("建议配置 API Key 以使用完整功能：")
            print("1. 复制 env.example 为 .env")
            print("2. 编辑 .env 文件，添加：")
            print("   GITEE_AI_API_KEY=你的API密钥")
            print()
            print("获取 API Key: https://ai.gitee.com/dashboard/settings/tokens")
            print()
        else:
            print("✓ API Key 已配置")
            print(f"✓ 使用模型: {settings.gitee_ai_model}")
            print()

        # 使用配置中的端口作为起始端口
        start_port = settings.port
    except Exception as e:
        print(f"⚠️  配置加载失败: {e}")
        print()
        start_port = 8000

    # 查找可用端口
    print("🔍 查找可用端口...")
    port = find_available_port(start_port)

    if port is None:
        print(f"❌ 无法找到可用端口 ({start_port}-{start_port + 9} 都被占用)")
        print()
        print("请手动释放端口后再试：")
        print(f"  netstat -ano | findstr :{start_port}")
        print("  taskkill /PID <PID> /F")
        sys.exit(1)

    if port != start_port:
        print(f"⚠️  端口 {start_port} 被占用，使用端口 {port}")
    else:
        print(f"✓ 使用端口 {port}")

    print()
    
    local_ip = get_local_ip()
    
    print("=" * 70)
    print("🎉 正在启动服务器...")
    print("=" * 70)
    print()
    print("📍 访问地址:")
    print(f"   🏠 本地访问:")
    print(f"      🌐 Web 界面: http://localhost:{port}")
    print(f"      📖 API 文档: http://localhost:{port}/docs")
    if local_ip:
        print(f"   🌐 局域网访问:")
        print(f"      🌐 Web 界面: http://{local_ip}:{port}")
        print(f"      📖 API 文档: http://{local_ip}:{port}/docs")
    print()
    print("💡 功能说明:")
    print("   💬 智能对话 - 简单对话和工具调用")
    print("   📚 RAG 问答 - 基于知识库的智能问答")
    print("   🗄️  知识库管理 - 上传和管理文档")
    print()
    print("📝 提示:")
    print("   - 局域网内其他设备可通过局域网IP访问此服务")
    print("   - 按 Ctrl+C 停止服务")
    print("   - 首次使用 RAG 功能时会初始化组件")
    print()
    print("=" * 70)
    print()
    
    import uvicorn
    
    try:
        uvicorn.run(
            "shuyixiao_agent.web_app:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="info",
            timeout_keep_alive=60,
            timeout_graceful_shutdown=30,
            access_log=True,
            workers=1
        )
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("👋 服务已停止")
        print("=" * 70)
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ 启动失败: {e}")
        print("=" * 70)
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

