#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
显示所有知识库信息
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import chromadb
from chromadb.config import Settings as ChromaSettings

DB_PATH = "./data/chroma"

def main():
    print("=" * 60)
    print("知识库列表")
    print("=" * 60)
    
    client = chromadb.PersistentClient(
        path=DB_PATH,
        settings=ChromaSettings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    
    collections = client.list_collections()
    
    print(f"\n找到 {len(collections)} 个知识库:\n")
    
    for idx, collection in enumerate(collections, 1):
        metadata = collection.metadata or {}
        original_name = metadata.get('original_name')
        
        print(f"{idx}. 集合名称: {collection.name}")
        print(f"   文档数量: {collection.count()}")
        
        if original_name:
            print(f"   原始名称: {original_name}")
            print(f"   状态: [已修复] 包含原始名称")
        else:
            print(f"   原始名称: (未保存)")
            print(f"   状态: [需迁移] 旧数据，没有原始名称映射")
        
        print(f"   Metadata: {metadata}")
        print()
    
    print("=" * 60)
    print("说明:")
    print("=" * 60)
    print()
    print("1. [已修复] 的知识库：包含原始名称，可以正常显示中文名")
    print("2. [需迁移] 的知识库：旧数据，只能显示编码名称")
    print()
    print("解决方案:")
    print("- 对于旧知识库，建议重新创建（上传数据到新的中文名称知识库）")
    print("- 或者继续使用编码名称访问")
    print()

if __name__ == "__main__":
    main()

