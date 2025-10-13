#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web 服务器问题诊断脚本

用于快速诊断 localhost:8000 无法访问的问题
"""

import sys
import os
import socket
import importlib.util
from pathlib import Path

# 设置 Windows 控制台支持 UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def print_section(title):
    """打印分节标题"""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()

def check_python_version():
    """检查 Python 版本"""
    print_section("1. Python 版本检查")
    
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 版本过低，需要 Python 3.8+")
        return False
    else:
        print("✓ Python 版本符合要求")
        return True

def check_virtual_env():
    """检查是否在虚拟环境中"""
    print_section("2. 虚拟环境检查")
    
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print(f"✓ 已激活虚拟环境: {sys.prefix}")
        return True
    else:
        print("⚠️  未在虚拟环境中")
        print()
        print("建议激活虚拟环境：")
        print("  Windows PowerShell: .venv\\Scripts\\Activate.ps1")
        print("  Windows CMD: .venv\\Scripts\\activate.bat")
        print("  Linux/Mac: source .venv/bin/activate")
        return True  # 不强制要求

def check_dependencies():
    """检查必要的依赖"""
    print_section("3. 依赖包检查")
    
    required_packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pydantic': 'Pydantic',
        'pydantic_settings': 'Pydantic Settings',
        'langchain_core': 'LangChain Core',
        'httpx': 'HTTPX',
        'python_dotenv': 'Python Dotenv'
    }
    
    all_ok = True
    missing = []
    
    for module_name, display_name in required_packages.items():
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"❌ {display_name:25} 未安装")
            missing.append(module_name)
            all_ok = False
        else:
            try:
                module = importlib.import_module(module_name)
                version = getattr(module, '__version__', '未知')
                print(f"✓ {display_name:25} {version}")
            except Exception as e:
                print(f"⚠️  {display_name:25} 导入失败: {e}")
                all_ok = False
    
    if missing:
        print()
        print("缺少的包：", ", ".join(missing))
        print()
        print("安装命令：")
        print(f"  pip install {' '.join(missing)}")
    
    return all_ok

def check_project_structure():
    """检查项目结构"""
    print_section("4. 项目结构检查")
    
    required_paths = [
        'src/shuyixiao_agent/__init__.py',
        'src/shuyixiao_agent/web_app.py',
        'src/shuyixiao_agent/config.py',
        'src/shuyixiao_agent/static/index.html',
    ]
    
    all_ok = True
    
    for path in required_paths:
        file_path = Path(path)
        if file_path.exists():
            print(f"✓ {path}")
        else:
            print(f"❌ {path} 不存在")
            all_ok = False
    
    return all_ok

def check_environment_config():
    """检查环境配置"""
    print_section("5. 环境配置检查")
    
    # 添加 src 到路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from shuyixiao_agent.config import settings
        
        print(f"API Key 已配置: {bool(settings.gitee_ai_api_key)}")
        if settings.gitee_ai_api_key:
            # 只显示前后几个字符
            key = settings.gitee_ai_api_key
            masked_key = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "****"
            print(f"API Key: {masked_key}")
        
        print(f"使用模型: {settings.gitee_ai_model}")
        print(f"数据库路径: {settings.vector_db_path}")
        print(f"使用云端嵌入: {settings.use_cloud_embedding}")
        
        if not settings.gitee_ai_api_key:
            print()
            print("⚠️  API Key 未配置")
            print()
            print("配置方法：")
            print("1. 复制 env.example 为 .env")
            print("2. 编辑 .env 文件，添加：")
            print("   GITEE_AI_API_KEY=你的API密钥")
            print()
            print("获取 API Key: https://ai.gitee.com/dashboard/settings/tokens")
        
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_port(port=8000):
    """检查端口状态"""
    print_section(f"6. 端口 {port} 检查")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                print(f"⚠️  端口 {port} 已被占用")
                print()
                print("查找占用进程的命令：")
                print(f"  netstat -ano | findstr :{port}")
                print()
                print("结束进程的命令：")
                print("  taskkill /PID <PID> /F")
                return False
            else:
                print(f"✓ 端口 {port} 可用")
                return True
    except Exception as e:
        print(f"❌ 检查端口时出错: {e}")
        return False

def test_web_app_import():
    """测试 web_app 导入"""
    print_section("7. Web 应用导入测试")
    
    # 添加 src 到路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from shuyixiao_agent.web_app import app
        print("✓ web_app 模块导入成功")
        print(f"✓ FastAPI app 对象: {app}")
        return True
    except Exception as e:
        print(f"❌ web_app 导入失败: {e}")
        print()
        print("详细错误：")
        import traceback
        traceback.print_exc()
        print()
        
        # 提供具体的解决建议
        error_str = str(e).lower()
        if 'pydantic_settings' in error_str:
            print("💡 解决方案：")
            print("   pip install pydantic-settings")
        elif 'module' in error_str:
            print("💡 解决方案：")
            print("   pip install -r requirements.txt")
        
        return False

def check_firewall():
    """检查防火墙提示"""
    print_section("8. 防火墙检查（手动）")
    
    print("无法自动检查防火墙状态，请手动确认：")
    print()
    print("Windows 防火墙可能会阻止 Python 访问网络")
    print()
    print("检查方法：")
    print("1. 打开 Windows 安全中心")
    print("2. 防火墙和网络保护 > 允许应用通过防火墙")
    print("3. 查找 Python 或 python.exe")
    print("4. 确保已勾选 '专用网络' 和 '公用网络'")
    print()
    print("临时测试方法：")
    print("1. 临时关闭防火墙")
    print("2. 测试是否能访问 localhost:8000")
    print("3. 如果可以，说明是防火墙问题")
    print("4. 重新开启防火墙并添加 Python 到白名单")

def generate_report():
    """生成诊断报告"""
    print()
    print("=" * 70)
    print("  诊断完成")
    print("=" * 70)
    print()
    print("💡 下一步操作建议：")
    print()
    print("1. 如果有缺失的依赖，先安装：")
    print("   pip install -r requirements.txt")
    print()
    print("2. 如果端口被占用，释放端口或使用其他端口")
    print()
    print("3. 如果配置有问题，创建 .env 文件并配置 API Key")
    print()
    print("4. 使用修复版启动脚本：")
    print("   python run_web_fixed.py")
    print()
    print("5. 测试服务器响应：")
    print("   python test_server.py")
    print()
    print("6. 查看详细故障排除文档：")
    print("   WEB_SERVER_TROUBLESHOOTING.md")
    print()

def main():
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "Web 服务器问题诊断工具" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = []
    
    results.append(("Python 版本", check_python_version()))
    results.append(("虚拟环境", check_virtual_env()))
    results.append(("依赖包", check_dependencies()))
    results.append(("项目结构", check_project_structure()))
    results.append(("环境配置", check_environment_config()))
    results.append(("端口检查", check_port(8000)))
    results.append(("应用导入", test_web_app_import()))
    
    check_firewall()
    
    # 显示摘要
    print()
    print("=" * 70)
    print("  诊断摘要")
    print("=" * 70)
    print()
    
    for name, status in results:
        symbol = "✓" if status else "❌"
        print(f"{symbol} {name}")
    
    all_passed = all(status for _, status in results)
    
    if all_passed:
        print()
        print("🎉 所有检查都通过了！")
        print()
        print("如果仍然无法访问，可能的原因：")
        print("1. 浏览器缓存问题 - 尝试清除缓存或使用无痕模式")
        print("2. 防火墙阻止 - 检查 Windows 防火墙设置")
        print("3. 首次启动慢 - 等待 30-60 秒让应用完全启动")
        print()
        print("建议使用修复版启动脚本：")
        print("  python run_web_fixed.py")
    else:
        print()
        print("❌ 发现一些问题需要解决")
    
    generate_report()

if __name__ == "__main__":
    main()

