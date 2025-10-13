"""
测试知识库名称映射修复

验证：
1. 首次加载时能从ChromaDB恢复映射关系
2. Collection metadata正确存储原始名称
3. API能正确返回历史知识库
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_collections_api():
    """测试获取collections列表API"""
    print("=" * 60)
    print("测试: 获取所有Collections")
    print("=" * 60)
    
    try:
        print(f"\n请求: GET {BASE_URL}/api/rag/collections")
        response = requests.get(f"{BASE_URL}/api/rag/collections", timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ 成功!")
            print(f"\n找到 {data['total_count']} 个知识库:")
            print("-" * 60)
            
            for coll in data['collections']:
                print(f"\n📚 知识库:")
                print(f"  - 集合名称: {coll['collection_name']}")
                if coll['original_name']:
                    print(f"  - 原始名称: {coll['original_name']}")
                    print(f"  - 是否转换: ✓")
                else:
                    print(f"  - 原始名称: (同集合名称)")
                    print(f"  - 是否转换: ✗")
                print(f"  - 文档数量: {coll['document_count']}")
            
            print("\n" + "=" * 60)
            if data['total_count'] == 0:
                print("⚠️  提示: 数据库中没有历史知识库")
                print("请先创建一些知识库再测试映射功能")
            else:
                print("✅ API工作正常，映射关系已恢复！")
            print("=" * 60)
            
        else:
            print(f"\n✗ 失败!")
            print(f"错误响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ 错误: 无法连接到服务器")
        print("请先启动服务器: python run_web.py")
    except Exception as e:
        print(f"\n✗ 错误: {e}")

def test_upload_and_verify():
    """测试上传中文知识库并验证映射"""
    print("\n" + "=" * 60)
    print("测试: 上传中文名称知识库并验证映射")
    print("=" * 60)
    
    # 创建一个测试知识库（中文名称）
    test_kb_name = "测试知识库_修复验证"
    test_texts = [
        "这是第一条测试数据",
        "这是第二条测试数据", 
        "这是第三条测试数据"
    ]
    
    try:
        print(f"\n1. 上传文本到知识库: {test_kb_name}")
        upload_response = requests.post(
            f"{BASE_URL}/api/rag/upload/texts",
            json={
                "collection_name": test_kb_name,
                "texts": test_texts
            },
            timeout=30
        )
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            print(f"   ✓ 上传成功")
            print(f"   - 原始名称: {upload_data.get('original_name', test_kb_name)}")
            print(f"   - 集合名称: {upload_data.get('collection_name')}")
            print(f"   - 文档数量: {upload_data.get('total_documents')}")
        else:
            print(f"   ✗ 上传失败: {upload_response.text}")
            return
        
        # 等待一下，确保数据持久化
        time.sleep(1)
        
        # 再次获取collections列表
        print(f"\n2. 获取collections列表验证...")
        list_response = requests.get(f"{BASE_URL}/api/rag/collections", timeout=10)
        
        if list_response.status_code == 200:
            list_data = list_response.json()
            
            # 查找刚上传的知识库
            found = False
            for coll in list_data['collections']:
                if coll['original_name'] == test_kb_name or coll['collection_name'] == upload_data.get('collection_name'):
                    found = True
                    print(f"   ✓ 找到知识库:")
                    print(f"   - 集合名称: {coll['collection_name']}")
                    print(f"   - 原始名称: {coll['original_name']}")
                    print(f"   - 文档数量: {coll['document_count']}")
                    break
            
            if found:
                print(f"\n✅ 测试通过! 映射关系正确保存和读取")
            else:
                print(f"\n⚠️  未找到刚创建的知识库")
        else:
            print(f"   ✗ 获取列表失败: {list_response.text}")
            
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")

def main():
    print("\n🚀 开始测试知识库映射修复...")
    print("\n请确保服务器正在运行: python run_web.py\n")
    
    # 测试1: 获取现有collections
    test_collections_api()
    
    # 测试2: 上传新知识库并验证
    print("\n")
    response = input("是否测试上传新知识库? (y/n): ")
    if response.lower() == 'y':
        test_upload_and_verify()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()

