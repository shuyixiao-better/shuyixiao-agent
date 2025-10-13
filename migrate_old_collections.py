"""
迁移旧Collection，添加original_name到metadata

用于修复在bug修复前创建的collection，为它们添加原始名称
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from pathlib import Path
import hashlib
import re

# 数据库路径
DB_PATH = "./data/chroma"

def reverse_hash_guess(collection_name: str) -> str:
    """
    尝试从collection名称猜测原始名称
    
    如果无法猜测，返回collection_name本身
    """
    # 检查是否符合我们的命名模式：prefix_hash 或 prefix_hash_kb
    pattern = r'^(.+?)_([a-f0-9]{8})(_kb)?$'
    match = re.match(pattern, collection_name)
    
    if not match:
        return collection_name
    
    prefix = match.group(1)
    name_hash = match.group(2)
    
    # 如果prefix是"kb"，说明原始名称完全没有合法字符
    if prefix == "kb":
        print(f"   ⚠️  无法自动恢复原始名称（前缀为'kb'）")
        return None
    
    # 返回前缀作为可能的原始名称提示
    return prefix

def list_collections_needing_migration():
    """列出需要迁移的collections"""
    print("=" * 60)
    print("🔍 扫描需要迁移的旧知识库...")
    print("=" * 60)
    
    client = chromadb.PersistentClient(
        path=DB_PATH,
        settings=ChromaSettings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    
    collections = client.list_collections()
    need_migration = []
    
    for collection in collections:
        metadata = collection.metadata or {}
        
        # 如果没有original_name，需要迁移
        if 'original_name' not in metadata:
            guess = reverse_hash_guess(collection.name)
            need_migration.append({
                'collection': collection,
                'name': collection.name,
                'count': collection.count(),
                'guess': guess
            })
    
    return need_migration, client

def migrate_collection(client, coll_info, original_name):
    """为collection添加original_name到metadata"""
    try:
        collection = coll_info['collection']
        
        # 获取现有metadata
        metadata = collection.metadata or {}
        metadata['original_name'] = original_name
        
        # ChromaDB不支持直接修改collection metadata
        # 需要删除并重建collection
        print(f"   ⚠️  警告：ChromaDB不支持直接修改metadata")
        print(f"   建议：手动记录映射关系，或重新创建知识库")
        
        return False
    except Exception as e:
        print(f"   ✗ 迁移失败: {e}")
        return False

def main():
    print("\n🔧 旧知识库迁移工具\n")
    
    need_migration, client = list_collections_needing_migration()
    
    if not need_migration:
        print("\n✅ 所有知识库都已包含原始名称，无需迁移！")
        return
    
    print(f"\n找到 {len(need_migration)} 个需要迁移的知识库:\n")
    
    for idx, coll_info in enumerate(need_migration, 1):
        print(f"{idx}. 📚 {coll_info['name']}")
        print(f"   - 文档数: {coll_info['count']}")
        if coll_info['guess']:
            print(f"   - 可能的原始名称: {coll_info['guess']}")
        else:
            print(f"   - 无法猜测原始名称")
        print()
    
    print("=" * 60)
    print("⚠️  重要说明")
    print("=" * 60)
    print()
    print("ChromaDB不支持直接修改collection的metadata。")
    print("要为旧知识库添加原始名称，有以下方案：")
    print()
    print("方案1：手动记录映射关系")
    print("  - 在web界面中记住：编码名称 -> 原始名称")
    print("  - 继续使用编码名称访问")
    print()
    print("方案2：重新创建知识库（推荐）")
    print("  - 使用web界面重新上传数据到新的中文名称知识库")
    print("  - 新知识库会自动保存原始名称")
    print("  - 删除旧的编码名称知识库")
    print()
    print("方案3：直接使用编码名称")
    print("  - 不进行迁移，直接使用编码名称")
    print("  - 在'所有知识库'列表中显示的就是编码名称")
    print()
    
    # 为每个collection生成建议
    print("=" * 60)
    print("📝 迁移建议")
    print("=" * 60)
    print()
    
    for idx, coll_info in enumerate(need_migration, 1):
        print(f"{idx}. {coll_info['name']} ({coll_info['count']}个文档)")
        
        if coll_info['guess'] and coll_info['guess'] != coll_info['name']:
            print(f"   建议原始名称: {coll_info['guess']}")
            print(f"   → 在web界面创建新知识库: '{coll_info['guess']}'")
        else:
            original = input(f"   请输入原始名称（回车跳过）: ").strip()
            if original:
                print(f"   → 在web界面创建新知识库: '{original}'")
        print()

if __name__ == "__main__":
    main()

