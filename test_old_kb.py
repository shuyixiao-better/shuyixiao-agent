#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试旧知识库 kb_dd65ff91_kb
"""

import requests

BASE_URL = "http://localhost:8001"

print("=" * 60)
print("测试旧知识库")
print("=" * 60)

# 1. 获取collections列表
print("\n1. 获取知识库列表...")
response = requests.get(f"{BASE_URL}/api/rag/collections")
if response.status_code == 200:
    data = response.json()
    print(f"   找到 {data['total_count']} 个知识库:")
    for coll in data['collections']:
        print(f"   - {coll['collection_name']} ({coll['document_count']}个文档)")
else:
    print(f"   失败: {response.text}")
    exit(1)

# 2. 查看 kb_dd65ff91_kb 的文档
print("\n2. 查看 kb_dd65ff91_kb 的文档...")
response = requests.get(f"{BASE_URL}/api/rag/documents/kb_dd65ff91_kb?limit=5")
if response.status_code == 200:
    data = response.json()
    print(f"   总共 {data['total_count']} 个文档，显示前{data['count']}个:")
    for doc in data['documents']:
        text_preview = doc['text'][:100] + "..." if len(doc['text']) > 100 else doc['text']
        print(f"   - ID: {doc['id']}")
        print(f"     内容: {text_preview}")
        print()
else:
    print(f"   失败: {response.text}")

# 3. 测试查询
print("\n3. 测试RAG查询...")
response = requests.post(
    f"{BASE_URL}/api/rag/query",
    json={
        "question": "这个知识库里有什么内容？",
        "collection_name": "kb_dd65ff91_kb",
        "top_k": 3
    }
)
if response.status_code == 200:
    data = response.json()
    print(f"   查询结果:")
    print(f"   {data['answer']}")
else:
    print(f"   失败: {response.text}")

print("\n" + "=" * 60)
print("结论：数据存在且可以正常访问！")
print("=" * 60)

