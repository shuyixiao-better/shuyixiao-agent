"""
测试Collections API

快速检查API是否正常工作
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_collections_api():
    """测试获取collections列表"""
    print("="*60)
    print("测试: 获取所有Collections")
    print("="*60)
    
    try:
        print(f"\n请求: GET {BASE_URL}/api/rag/collections")
        response = requests.get(f"{BASE_URL}/api/rag/collections", timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ 成功!")
            print(f"响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"\n✗ 失败!")
            print(f"错误响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ 错误: 无法连接到服务器")
        print("请确保服务器正在运行: python run_web.py")
    except Exception as e:
        print(f"\n✗ 错误: {e}")

def test_health():
    """测试健康检查"""
    print("\n" + "="*60)
    print("测试: 健康检查")
    print("="*60)
    
    try:
        print(f"\n请求: GET {BASE_URL}/api/health")
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 服务器正常")
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"✗ 服务器响应异常: {response.text}")
            
    except Exception as e:
        print(f"✗ 错误: {e}")

def check_database():
    """检查数据库目录"""
    import os
    from pathlib import Path
    
    print("\n" + "="*60)
    print("检查: 数据库目录")
    print("="*60)
    
    db_path = Path("data/chroma")
    
    print(f"\n数据库路径: {db_path.absolute()}")
    print(f"目录存在: {db_path.exists()}")
    
    if db_path.exists():
        print(f"目录可读: {os.access(db_path, os.R_OK)}")
        print(f"目录可写: {os.access(db_path, os.W_OK)}")
        
        # 列出目录内容
        print(f"\n目录内容:")
        for item in db_path.iterdir():
            size = item.stat().st_size if item.is_file() else "DIR"
            print(f"  - {item.name} ({size})")
    else:
        print("⚠ 数据库目录不存在!")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Collections API 诊断工具")
    print("="*60)
    
    # 1. 检查数据库
    check_database()
    
    # 2. 测试健康检查
    test_health()
    
    # 3. 测试collections API
    test_collections_api()
    
    print("\n" + "="*60)
    print("诊断完成")
    print("="*60)
    print("\n提示:")
    print("1. 如果显示'无法连接到服务器'，请先运行: python run_web.py")
    print("2. 如果数据库目录不存在，说明还没有上传过任何文档")
    print("3. 查看服务器终端的日志输出以获取详细错误信息")
    print()

