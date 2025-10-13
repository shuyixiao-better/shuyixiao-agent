#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动 Web 界面服务（修复版）

修复内容：
- ✅ 完整的依赖检查
- ✅ 禁用 reload 避免导入问题
- ✅ 增加超时时间
- ✅ 详细的诊断日志
- ✅ 延迟加载 RAG 组件
"""

import sys
import os
import importlib.util

# 设置 Windows 控制台支持 UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_dependencies():
    """检查必要的依赖"""
    print("🔍 检查依赖...")
    print()
    
    required_packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pydantic', 'Pydantic'),
        ('langchain_core', 'LangChain Core'),
    ]
    
    missing = []
    for module_name, display_name in required_packages:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"   ❌ {display_name} 未安装")
            missing.append(display_name)
        else:
            print(f"   ✓ {display_name} 已安装")
    
    print()
    
    if missing:
        print("❌ 缺少依赖，请先安装：")
        print()
        print("   pip install -r requirements.txt")
        print()
        print("或使用 Poetry:")
        print()
        print("   poetry install")
        print()
        return False
    
    return True

def test_app_import():
    """测试应用是否可以正常导入"""
    print("🔍 测试应用导入...")
    print()
    
    try:
        # 尝试导入 web_app
        from shuyixiao_agent.web_app import app
        print("   ✓ web_app 导入成功")
        print()
        return True
    except Exception as e:
        print(f"   ❌ web_app 导入失败: {e}")
        print()
        print("详细错误信息：")
        import traceback
        traceback.print_exc()
        print()
        return False

def check_port(port=8000):
    """检查端口是否被占用"""
    import socket
    
    print(f"🔍 检查端口 {port}...")
    print()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('localhost', port))
        if result == 0:
            print(f"   ⚠️  端口 {port} 已被占用")
            print()
            print("   解决方案：")
            print(f"   1. 查找占用端口的进程: netstat -ano | findstr :{port}")
            print("   2. 结束该进程: taskkill /PID <PID> /F")
            print("   3. 或使用其他端口启动")
            print()
            return False
        else:
            print(f"   ✓ 端口 {port} 可用")
            print()
            return True

def check_api_key():
    """检查 API Key 配置"""
    print("🔍 检查配置...")
    print()
    
    from shuyixiao_agent.config import settings
    
    if not settings.gitee_ai_api_key:
        print("   ⚠️  警告: API Key 未配置！")
        print()
        print("   配置方法：")
        print()
        print("   方法 1: 创建 .env 文件")
        print("   复制 env.example 为 .env，然后编辑：")
        print("     GITEE_AI_API_KEY=你的API密钥")
        print()
        print("   方法 2: 设置环境变量")
        print("   PowerShell:")
        print('     $env:GITEE_AI_API_KEY="你的API密钥"')
        print()
        print("   💡 获取 API Key: https://ai.gitee.com/dashboard/settings/tokens")
        print()
        
        response = input("   是否继续启动？(y/N): ").strip().lower()
        if response != 'y':
            return False
    else:
        print(f"   ✓ API Key 已配置")
        print(f"   ✓ 使用模型: {settings.gitee_ai_model}")
        print()
    
    return True

def main():
    print("=" * 70)
    print("🚀 启动 ShuYixiao Agent Web 界面（修复版）")
    print("=" * 70)
    print()
    
    # 步骤 1: 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 步骤 2: 测试应用导入
    if not test_app_import():
        print("💡 提示：如果是 pydantic 相关错误，请尝试：")
        print("   pip install pydantic-settings")
        print()
        sys.exit(1)
    
    # 步骤 3: 检查端口
    port = 8000
    if not check_port(port):
        response = input("   是否使用其他端口 8001？(Y/n): ").strip().lower()
        if response != 'n':
            port = 8001
            if not check_port(port):
                print("   端口 8001 也被占用，请手动释放端口后重试")
                sys.exit(1)
        else:
            sys.exit(1)
    
    # 步骤 4: 检查配置
    if not check_api_key():
        print("👋 退出")
        sys.exit(1)
    
    print("=" * 70)
    print("🎉 所有检查通过，正在启动服务器...")
    print("=" * 70)
    print()
    print("📍 访问地址:")
    print(f"   🌐 Web 界面: http://localhost:{port}")
    print(f"   📖 API 文档: http://localhost:{port}/docs")
    print()
    print("💡 功能说明:")
    print("   💬 智能对话 - 简单对话和工具调用")
    print("   📚 RAG 问答 - 基于知识库的智能问答")
    print("   🗄️  知识库管理 - 上传和管理文档")
    print()
    print("⚡ 优化配置:")
    print("   ✓ 禁用 reload 模式（更稳定）")
    print("   ✓ 延迟加载 RAG 组件（快速启动）")
    print("   ✓ 增加超时时间（避免连接中断）")
    print()
    print("📝 提示:")
    print("   - 按 Ctrl+C 停止服务")
    print("   - 首次使用 RAG 功能时会初始化组件")
    print("   - 如果浏览器无法访问，请等待 30 秒后刷新")
    print()
    print("=" * 70)
    print()
    
    import uvicorn
    
    try:
        uvicorn.run(
            "shuyixiao_agent.web_app:app",
            host="0.0.0.0",
            port=port,
            reload=False,  # 禁用 reload，避免导入问题
            log_level="info",
            timeout_keep_alive=60,  # 增加保活超时
            timeout_graceful_shutdown=30,  # 增加优雅关闭超时
            access_log=True,
            workers=1  # 单进程模式
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
        print("🔧 详细错误信息:")
        import traceback
        traceback.print_exc()
        print()
        print("💡 故障排除:")
        print("   1. 确认虚拟环境已激活")
        print("      .venv\\Scripts\\Activate.ps1")
        print()
        print("   2. 重新安装依赖")
        print("      pip install --upgrade -r requirements.txt")
        print()
        print("   3. 检查防火墙设置")
        print("      临时关闭防火墙测试")
        print()
        print("   4. 查看故障排除文档")
        print("      WEB_SERVER_TROUBLESHOOTING.md")
        print()
        sys.exit(1)

if __name__ == "__main__":
    main()

