# 知识库首次加载映射丢失问题修复

## 问题描述

用户报告：项目首次加载时，历史知识库数据加载不出来。

## 问题根源

1. **映射关系丢失**: `collection_name_mapping` 是一个内存字典，只在程序运行时存在
2. **重启后映射丢失**: 每次应用重启后，这个映射关系就会丢失
3. **数据存在但无法识别**: 虽然历史知识库的数据在ChromaDB中持久保存了，但是原始名称到编码名称的映射关系没有持久化
4. **首次加载失败**: 在首次加载页面时调用 `/api/rag/collections` 时，由于映射关系丢失，无法恢复原始名称

## 解决方案

### 1. Collection Metadata 持久化存储原始名称

**修改文件**: `src/shuyixiao_agent/rag/vector_store.py`

在创建Collection时，将原始名称保存到Collection的metadata中：

```python
# 创建集合时保存原始名称到metadata
collection_metadata = {"hnsw:space": "cosine"}

if original_name and original_name != collection_name:
    collection_metadata["original_name"] = original_name

self.collection = self.client.create_collection(
    name=collection_name,
    metadata=collection_metadata
)
```

### 2. 启动时从ChromaDB恢复映射关系

**修改文件**: `src/shuyixiao_agent/web_app.py`

在应用启动时，扫描所有Collection并从metadata恢复映射关系：

```python
@app.on_event("startup")
async def startup_event():
    # ... 其他初始化代码 ...
    
    # 从数据库恢复知识库名称映射关系
    print("🔄 正在恢复知识库名称映射关系...")
    try:
        client = chromadb.PersistentClient(...)
        collections = client.list_collections()
        
        for collection in collections:
            metadata = collection.metadata or {}
            original_name = metadata.get('original_name')
            
            if original_name and original_name != collection.name:
                collection_name_mapping[original_name] = collection.name
                print(f"  ✓ 恢复映射: '{original_name}' -> '{collection.name}'")
        
        print(f"✅ 已恢复 {len(collection_name_mapping)} 个名称映射关系")
    except Exception as e:
        print(f"⚠️  恢复名称映射失败: {e}")
```

### 3. API端点直接从Metadata读取

**修改文件**: `src/shuyixiao_agent/web_app.py`

修改 `/api/rag/collections` 端点，优先从Collection metadata读取原始名称：

```python
@app.get("/api/rag/collections")
async def list_collections():
    # ...
    
    for collection in collections:
        # 优先从collection metadata中读取原始名称
        metadata = collection.metadata or {}
        original_name = metadata.get('original_name')
        
        # 如果metadata中没有，再尝试从内存映射表中查找（向后兼容）
        if not original_name:
            for orig, norm in collection_name_mapping.items():
                if norm == collection_name:
                    original_name = orig
                    break
        
        # 如果还是没有原始名称，说明该collection名称本身就是合法的
        if not original_name:
            original_name = collection_name
```

### 4. 传递原始名称链路完整

**修改文件**: 
- `src/shuyixiao_agent/rag/rag_agent.py` - 添加 `original_name` 参数
- `src/shuyixiao_agent/web_app.py` - `get_rag_agent` 函数传递原始名称

确保从用户输入 → RAGAgent → VectorStoreManager → ChromaDB Collection metadata 的完整链路。

## 修复效果

### ✅ 修复前的问题

1. 首次加载页面时，历史知识库列表为空
2. 虽然数据在数据库中，但前端无法显示
3. 重启应用后，之前的中文名称知识库无法识别

### ✅ 修复后的效果

1. **启动时自动恢复**: 应用启动时自动从ChromaDB恢复所有映射关系
2. **持久化存储**: 原始名称保存在Collection metadata中，永久保存
3. **首次加载正常**: 页面首次加载能正确显示所有历史知识库
4. **向后兼容**: 支持从内存映射表读取（兼容旧数据）

## 测试验证

### 方式1: 自动测试脚本

运行测试脚本验证修复：

```bash
python test_collection_mapping_fix.py
```

### 方式2: 手动测试

1. **启动服务器**:
   ```bash
   python run_web.py
   ```

2. **观察启动日志**:
   ```
   🔄 正在恢复知识库名称映射关系...
     ✓ 恢复映射: '测试知识库' -> 'kb_12345678'
     ✓ 恢复映射: '我的文档' -> 'kb_abcdef12'
   ✅ 已恢复 2 个名称映射关系
   ```

3. **访问Web界面**: http://localhost:8000

4. **切换到"知识库管理"标签页**

5. **点击"刷新列表"按钮** (在"所有知识库"卡片中)

6. **验证**: 
   - 应该能看到所有历史知识库
   - 中文名称应该正确显示
   - 文档数量应该正确

### 方式3: API测试

```bash
curl http://localhost:8000/api/rag/collections
```

应该返回所有知识库，包括原始名称映射。

## 技术细节

### ChromaDB Collection Metadata

ChromaDB支持在Collection级别存储metadata：

```python
collection = client.create_collection(
    name="kb_12345678",
    metadata={
        "hnsw:space": "cosine",      # 向量空间配置
        "original_name": "我的知识库"  # 自定义元数据
    }
)
```

这些metadata会随Collection一起持久化保存。

### 启动恢复流程

```
启动应用
  ↓
初始化数据库
  ↓
扫描所有Collections
  ↓
读取每个Collection的metadata
  ↓
提取original_name
  ↓
重建collection_name_mapping字典
  ↓
应用就绪
```

### API读取优先级

```
1. 尝试从Collection metadata读取original_name
   ↓ (如果没有)
2. 尝试从内存映射表collection_name_mapping读取
   ↓ (如果还没有)
3. 使用collection_name本身作为原始名称
```

## 影响范围

### ✅ 已修改的文件

- `src/shuyixiao_agent/web_app.py` - 启动恢复逻辑、API端点优化、get_rag_agent传参
- `src/shuyixiao_agent/rag/vector_store.py` - Collection创建时保存原始名称
- `src/shuyixiao_agent/rag/rag_agent.py` - 添加original_name参数

### ✅ 新增的文件

- `test_collection_mapping_fix.py` - 测试脚本
- `COLLECTION_MAPPING_FIX.md` - 本文档

### ⚠️ 向后兼容性

- 完全向后兼容
- 旧的Collection（没有original_name metadata）仍然可以通过内存映射表读取
- 新创建的Collection会自动保存原始名称到metadata

## 注意事项

1. **首次启动时间**: 如果有大量Collection，启动时扫描恢复映射关系可能需要几秒钟
2. **日志输出**: 启动时会输出详细的映射恢复日志，便于调试
3. **数据迁移**: 旧的Collection不会自动添加original_name到metadata，但不影响使用
4. **元数据大小**: ChromaDB metadata有大小限制，原始名称不应过长（通常不超过512字符）

## 相关文档

- [KNOWLEDGE_BASE_FIXES_SUMMARY.md](KNOWLEDGE_BASE_FIXES_SUMMARY.md) - 知识库功能修复总结
- [DATABASE_PERSISTENCE_FIX.md](DATABASE_PERSISTENCE_FIX.md) - 数据持久化修复
- [KNOWLEDGE_BASE_MAPPING_DISPLAY.md](KNOWLEDGE_BASE_MAPPING_DISPLAY.md) - 名称映射显示

## 问题反馈

如果修复后仍有问题，请检查：

1. 服务器启动日志是否显示映射恢复成功
2. 数据库路径是否正确 (`data/chroma/`)
3. 数据库文件是否有读写权限
4. ChromaDB版本是否兼容（建议使用0.4.0+）

