"""
测试知识库修复功能

验证以下功能：
1. 列出所有collection
2. 批量删除文档
3. 物理删除验证
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"

def test_list_collections():
    """测试列出所有collection"""
    print("\n" + "="*60)
    print("测试1: 列出所有collection")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/rag/collections")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 成功获取collection列表")
        print(f"  总数: {data['total_count']}")
        
        for coll in data['collections']:
            print(f"\n  📚 {coll['collection_name']}")
            if coll['original_name']:
                print(f"     原始名称: {coll['original_name']}")
            print(f"     文档数量: {coll['document_count']}")
            print(f"     是否规范化: {coll['is_normalized']}")
    else:
        print(f"✗ 失败: {response.status_code}")
        print(f"  {response.text}")


def test_upload_and_batch_delete():
    """测试上传和批量删除"""
    print("\n" + "="*60)
    print("测试2: 上传测试文档并批量删除")
    print("="*60)
    
    collection_name = "test_batch_delete"
    
    # 1. 上传测试文档
    print("\n步骤1: 上传测试文档...")
    texts = [
        "这是测试文档1",
        "这是测试文档2", 
        "这是测试文档3",
        "这是测试文档4",
        "这是测试文档5"
    ]
    
    upload_response = requests.post(
        f"{BASE_URL}/api/rag/upload/texts",
        json={
            "texts": texts,
            "collection_name": collection_name
        }
    )
    
    if upload_response.status_code == 200:
        upload_data = upload_response.json()
        print(f"✓ 上传成功: {upload_data['chunks_added']} 个片段")
    else:
        print(f"✗ 上传失败: {upload_response.status_code}")
        return
    
    # 2. 获取文档列表
    print("\n步骤2: 获取文档列表...")
    docs_response = requests.get(
        f"{BASE_URL}/api/rag/documents/{collection_name}?limit=10"
    )
    
    if docs_response.status_code == 200:
        docs_data = docs_response.json()
        print(f"✓ 获取到 {docs_data['count']} 个文档")
        
        # 获取前3个文档ID用于批量删除
        doc_ids = [doc['id'] for doc in docs_data['documents'][:3]]
        print(f"  选择删除的文档ID: {doc_ids}")
    else:
        print(f"✗ 获取文档失败: {docs_response.status_code}")
        return
    
    # 3. 批量删除
    print("\n步骤3: 批量删除文档...")
    delete_response = requests.delete(
        f"{BASE_URL}/api/rag/documents/batch",
        json={
            "collection_name": collection_name,
            "doc_ids": doc_ids
        }
    )
    
    if delete_response.status_code == 200:
        delete_data = delete_response.json()
        print(f"✓ 批量删除完成")
        print(f"  成功: {delete_data['success_count']}")
        print(f"  失败: {delete_data['failed_count']}")
        print(f"  剩余文档: {delete_data['remaining_count']}")
    else:
        print(f"✗ 批量删除失败: {delete_response.status_code}")
        print(f"  {delete_response.text}")
    
    # 4. 验证删除结果
    print("\n步骤4: 验证删除结果...")
    verify_response = requests.get(
        f"{BASE_URL}/api/rag/documents/{collection_name}"
    )
    
    if verify_response.status_code == 200:
        verify_data = verify_response.json()
        print(f"✓ 当前文档数: {verify_data['total_count']}")
        
        # 检查被删除的文档是否还存在
        remaining_ids = [doc['id'] for doc in verify_data['documents']]
        deleted_successfully = all(doc_id not in remaining_ids for doc_id in doc_ids)
        
        if deleted_successfully:
            print(f"✓ 所有选中的文档已成功删除（物理删除）")
        else:
            print(f"✗ 警告: 部分文档可能未被删除")
    
    # 5. 清理测试collection
    print("\n步骤5: 清理测试collection...")
    clear_response = requests.delete(
        f"{BASE_URL}/api/rag/clear/{collection_name}"
    )
    
    if clear_response.status_code == 200:
        print(f"✓ 测试collection已清理")
    else:
        print(f"⚠ 清理失败（请手动删除）: {clear_response.status_code}")


def test_knowledge_info():
    """测试知识库信息刷新"""
    print("\n" + "="*60)
    print("测试3: 知识库信息刷新")
    print("="*60)
    
    # 获取所有collections
    collections_response = requests.get(f"{BASE_URL}/api/rag/collections")
    
    if collections_response.status_code == 200:
        collections_data = collections_response.json()
        
        if collections_data['collections']:
            # 测试第一个collection的信息
            first_coll = collections_data['collections'][0]
            coll_name = first_coll['collection_name']
            
            print(f"\n获取 '{coll_name}' 的信息...")
            info_response = requests.get(f"{BASE_URL}/api/rag/info/{coll_name}")
            
            if info_response.status_code == 200:
                info_data = info_response.json()
                print(f"✓ 成功获取知识库信息")
                print(f"  集合名称: {info_data['collection_name']}")
                if info_data.get('original_name'):
                    print(f"  原始名称: {info_data['original_name']}")
                print(f"  文档数量: {info_data['document_count']}")
                print(f"  检索模式: {info_data['retrieval_mode']}")
            else:
                print(f"✗ 获取信息失败: {info_response.status_code}")
        else:
            print("⚠ 没有可用的collection进行测试")
    else:
        print(f"✗ 获取collections失败: {collections_response.status_code}")


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("知识库修复功能测试")
    print("="*60)
    print("请确保Web服务器正在运行: python run_web.py")
    print("="*60)
    
    try:
        # 健康检查
        health_response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✓ 服务器连接成功")
        else:
            print("✗ 服务器响应异常")
            return
    except requests.exceptions.RequestException as e:
        print(f"✗ 无法连接到服务器: {e}")
        print("  请先启动服务器: python run_web.py")
        return
    
    # 运行测试
    test_list_collections()
    test_upload_and_batch_delete()
    test_knowledge_info()
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


if __name__ == "__main__":
    main()

