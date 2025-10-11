#!/usr/bin/env python
"""
SSL 修复验证脚本

用于测试 SSL 配置是否正确，以及 API 连接是否正常
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_config():
    """测试配置加载"""
    print("=" * 60)
    print("1. 测试配置加载...")
    print("=" * 60)
    
    try:
        from shuyixiao_agent.config import settings
        
        print(f"[OK] 配置加载成功")
        print(f"   - API Key: {'已配置' if settings.gitee_ai_api_key else '未配置'}")
        print(f"   - Base URL: {settings.gitee_ai_base_url}")
        print(f"   - Model: {settings.gitee_ai_model}")
        print(f"   - SSL Verify: {settings.ssl_verify}")
        print(f"   - Max Retries: {settings.max_retries}")
        print(f"   - Timeout: {settings.request_timeout}秒")
        
        if not settings.gitee_ai_api_key:
            print("\n[WARNING] 警告: API Key 未配置，请在 .env 文件中设置 GITEE_AI_API_KEY")
            return False
            
        return True
        
    except Exception as e:
        print(f"[ERROR] 配置加载失败: {str(e)}")
        return False


def test_client_creation():
    """测试客户端创建"""
    print("\n" + "=" * 60)
    print("2. 测试客户端创建...")
    print("=" * 60)
    
    try:
        from shuyixiao_agent.gitee_ai_client import GiteeAIClient
        
        client = GiteeAIClient()
        print(f"[OK] 客户端创建成功")
        print(f"   - SSL Verify: {client.ssl_verify}")
        print(f"   - Session: {'已创建' if client.session else '未创建'}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 客户端创建失败: {str(e)}")
        return False


def test_api_connection():
    """测试 API 连接"""
    print("\n" + "=" * 60)
    print("3. 测试 API 连接...")
    print("=" * 60)
    
    try:
        from shuyixiao_agent.gitee_ai_client import GiteeAIClient
        
        client = GiteeAIClient()
        
        print("发送测试消息: '你好'")
        print("等待响应...")
        
        response = client.simple_chat("你好，请用一句话回复我。")
        
        print(f"[OK] API 连接成功")
        print(f"   AI 回复: {response}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] API 连接失败: {str(e)}")
        print("\n可能的解决方案:")
        print("1. 检查 .env 文件中的 SSL_VERIFY=false 是否已设置")
        print("2. 检查 API Key 是否正确")
        print("3. 检查网络连接")
        print("4. 查看 docs/ssl_troubleshooting.md 获取更多帮助")
        return False


def test_web_health():
    """测试 Web 服务健康检查（如果服务正在运行）"""
    print("\n" + "=" * 60)
    print("4. 测试 Web 服务...")
    print("=" * 60)
    
    try:
        import requests
        
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Web 服务正在运行")
            print(f"   - 状态: {data.get('status')}")
            print(f"   - API Key: {'已配置' if data.get('api_key_configured') else '未配置'}")
            print(f"   - 模型: {data.get('model')}")
            return True
        else:
            print(f"[WARNING] Web 服务响应异常: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[INFO] Web 服务未运行")
        print("   如需测试 Web 界面，请运行: python run_web.py")
        return None  # None 表示跳过此测试
        
    except Exception as e:
        print(f"[WARNING] 无法检查 Web 服务: {str(e)}")
        return None


def main():
    """主测试流程"""
    print("\n")
    print("SSL 修复验证测试")
    print("=" * 60)
    print("此脚本将测试 SSL 配置和 API 连接是否正常")
    print("=" * 60)
    
    results = []
    
    # 测试 1: 配置加载
    results.append(("配置加载", test_config()))
    
    # 如果配置加载失败，停止后续测试
    if not results[-1][1]:
        print("\n[ERROR] 配置加载失败，无法继续测试")
        return False
    
    # 测试 2: 客户端创建
    results.append(("客户端创建", test_client_creation()))
    
    # 测试 3: API 连接
    results.append(("API 连接", test_api_connection()))
    
    # 测试 4: Web 服务（可选）
    web_result = test_web_health()
    if web_result is not None:
        results.append(("Web 服务", web_result))
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name:20} {status}")
    
    # 判断总体结果
    critical_tests = [r for name, r in results if name in ["配置加载", "客户端创建", "API 连接"]]
    all_critical_passed = all(critical_tests)
    
    print("\n" + "=" * 60)
    if all_critical_passed:
        print("[SUCCESS] 所有关键测试通过！SSL 问题已解决！")
        print("\n你现在可以:")
        print("1. 运行 'python run_web.py' 启动 Web 服务")
        print("2. 访问 http://localhost:8000 使用 Web 界面")
        print("3. 或者直接使用 Python API 进行开发")
    else:
        print("[WARNING] 部分测试失败，请检查错误信息")
        print("\n请参考:")
        print("1. SSL_FIX_GUIDE.md - 快速修复指南")
        print("2. docs/ssl_troubleshooting.md - 详细故障排除")
    print("=" * 60)
    
    return all_critical_passed


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[INFO] 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] 测试过程中发生未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

