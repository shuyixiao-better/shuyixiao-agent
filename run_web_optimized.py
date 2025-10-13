#!/usr/bin/env python3
"""
启动 Web 界面服务（优化版 - 使用云端 API）

改进：
- ✅ 使用 Gitee AI 云端 API，无需下载模型
- ✅ 延迟加载 RAG 组件，启动速度快
- ✅ 详细的诊断和日志
- ✅ 更好的错误处理
"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_api_key():
    """检查 API Key 配置"""
    print("🔍 检查配置...")
    
    from shuyixiao_agent.config import settings
    
    if not settings.gitee_ai_api_key:
        print()
        print("⚠️  警告: API Key 未配置！")
        print()
        print("📝 配置方法：")
        print()
        print("方法 1: 创建 .env 文件")
        print("-------")
        print("复制 env.example 为 .env，然后编辑：")
        print("  GITEE_AI_API_KEY=你的API密钥")
        print()
        print("方法 2: 设置环境变量")
        print("-------")
        print("PowerShell:")
        print('  $env:GITEE_AI_API_KEY="你的API密钥"')
        print()
        print("Bash/Linux:")
        print('  export GITEE_AI_API_KEY="你的API密钥"')
        print()
        print("💡 获取 API Key: https://ai.gitee.com/dashboard/settings/tokens")
        print()
        
        response = input("是否继续启动？(y/N): ").strip().lower()
        if response != 'y':
            print("👋 退出")
            return False
    else:
        print(f"   ✓ API Key 已配置")
        print(f"   ✓ 使用模型: {settings.gitee_ai_model}")
        print(f"   ✓ 嵌入服务: {'云端 API' if settings.use_cloud_embedding else '本地模型'}")
        
        if settings.use_cloud_embedding:
            print(f"   ✓ 云端嵌入模型: {settings.cloud_embedding_model}")
            print("   ✓ 优势: 无需下载模型，启动速度快")
    
    return True

def main():
    print("=" * 60)
    print("🚀 启动 ShuYixiao Agent Web 界面（优化版）")
    print("=" * 60)
    print()
    
    # 检查配置
    if not check_api_key():
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("🎉 配置检查通过，正在启动服务器...")
    print("=" * 60)
    print()
    print("📍 访问地址:")
    print("   🌐 Web 界面: http://localhost:8001")
    print("   📖 API 文档: http://localhost:8001/docs")
    print()
    print("💡 功能说明:")
    print("   💬 智能对话 - 简单对话和工具调用")
    print("   📚 RAG 问答 - 基于知识库的智能问答")
    print("   🗄️  知识库管理 - 上传和管理文档")
    print()
    print("⚡ 性能优化:")
    print("   ✓ 使用云端 API，无需下载模型")
    print("   ✓ 延迟加载 RAG 组件")
    print("   ✓ 启动速度: ~3 秒（vs 之前的 1-2 分钟）")
    print()
    print("📝 提示:")
    print("   - 按 Ctrl+C 停止服务")
    print("   - 首次使用 RAG 功能时会初始化组件")
    print()
    print("=" * 60)
    print()
    
    import uvicorn
    
    try:
        uvicorn.run(
            "shuyixiao_agent.web_app:app",
            host="0.0.0.0",
            port=8001,
            reload=False,  # 禁用 reload，更稳定
            log_level="info",
            timeout_keep_alive=60,  # 增加超时时间
            access_log=True
        )
    except KeyboardInterrupt:
        print()
        print("=" * 60)
        print("👋 服务已停止")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ 启动失败: {e}")
        print("=" * 60)
        print()
        print("🔧 故障排除:")
        print("   1. 检查端口 8000 是否被占用")
        print("      netstat -ano | findstr :8000")
        print()
        print("   2. 确认虚拟环境已激活")
        print("      .venv\\Scripts\\Activate.ps1")
        print()
        print("   3. 检查依赖是否安装完整")
        print("      pip install -r requirements.txt")
        print()
        print("   4. 查看详细日志")
        print("      python run_web_optimized.py 2>&1 | Out-File error.log")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

