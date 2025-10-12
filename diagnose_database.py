#!/usr/bin/env python3
"""
ChromaDB 数据库诊断工具

检查数据库配置、路径、权限等信息
"""

import os
import sys
from pathlib import Path

print("🔍 ChromaDB 数据库诊断工具")
print("=" * 60)

# 1. 检查当前工作目录
print(f"\n📁 当前工作目录: {os.getcwd()}")

# 2. 检查项目根目录
project_root = Path(__file__).parent
print(f"📁 项目根目录: {project_root}")

# 3. 加载配置
try:
    sys.path.insert(0, str(project_root / "src"))
    from shuyixiao_agent.config import settings
    
    print(f"\n⚙️  配置信息:")
    print(f"   向量数据库路径: {settings.vector_db_path}")
    print(f"   使用云端嵌入: {settings.use_cloud_embedding}")
    print(f"   嵌入模型: {settings.cloud_embedding_model if settings.use_cloud_embedding else settings.embedding_model}")
    
    # 4. 检查数据库目录
    db_path = Path(settings.vector_db_path)
    if not db_path.is_absolute():
        db_path = project_root / db_path
    
    print(f"\n📂 数据库路径信息:")
    print(f"   绝对路径: {db_path.absolute()}")
    print(f"   目录存在: {'✓' if db_path.exists() else '✗'}")
    
    if db_path.exists():
        print(f"   目录权限: {oct(os.stat(db_path).st_mode)[-3:]}")
        print(f"   可读: {'✓' if os.access(db_path, os.R_OK) else '✗'}")
        print(f"   可写: {'✓' if os.access(db_path, os.W_OK) else '✗'}")
        print(f"   可执行: {'✓' if os.access(db_path, os.X_OK) else '✗'}")
        
        # 5. 列出目录内容
        print(f"\n📄 目录内容:")
        files = list(db_path.iterdir())
        if files:
            for f in files:
                size = f.stat().st_size if f.is_file() else '-'
                ftype = 'D' if f.is_dir() else 'F'
                perms = oct(os.stat(f).st_mode)[-3:]
                print(f"   [{ftype}] {f.name:30} {perms:4} {size:>10}")
        else:
            print("   (空目录)")
        
        # 6. 检查 SQLite 数据库文件
        sqlite_file = db_path / "chroma.sqlite3"
        print(f"\n💾 SQLite 数据库文件:")
        print(f"   文件存在: {'✓' if sqlite_file.exists() else '✗'}")
        if sqlite_file.exists():
            print(f"   文件大小: {sqlite_file.stat().st_size} 字节")
            print(f"   文件权限: {oct(os.stat(sqlite_file).st_mode)[-3:]}")
            print(f"   可读: {'✓' if os.access(sqlite_file, os.R_OK) else '✗'}")
            print(f"   可写: {'✓' if os.access(sqlite_file, os.W_OK) else '✗'}")
    else:
        print(f"   ⚠️  目录不存在，将在首次使用时自动创建")
    
    # 7. 尝试创建测试数据库
    print(f"\n🧪 测试数据库创建:")
    try:
        from shuyixiao_agent.rag.vector_store import VectorStoreManager
        from shuyixiao_agent.rag.cloud_embeddings import BatchCloudEmbeddingManager
        
        print("   正在创建测试集合...")
        embedding_manager = BatchCloudEmbeddingManager(model=settings.cloud_embedding_model)
        test_store = VectorStoreManager(
            collection_name="test_diagnostics",
            embedding_manager=embedding_manager
        )
        
        # 尝试添加一个测试文档
        from langchain_core.documents import Document
        test_doc = Document(page_content="测试文档", metadata={"test": True})
        test_store.add_documents([test_doc])
        
        print("   ✓ 成功创建测试集合")
        print("   ✓ 成功添加测试文档")
        
        # 清理测试数据
        test_store.clear()
        print("   ✓ 成功清理测试数据")
        
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        import traceback
        print("\n详细错误信息:")
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ 诊断完成")
    
except Exception as e:
    print(f"\n❌ 诊断失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

