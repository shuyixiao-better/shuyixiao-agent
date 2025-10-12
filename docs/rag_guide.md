# RAG (检索增强生成) 使用指南

## 简介

RAG（Retrieval-Augmented Generation，检索增强生成）是一种结合信息检索和文本生成的 AI 技术。本项目实现了完整的 RAG 系统，包括多模态检索、查询优化、重排序、上下文管理等高级功能。

## 核心功能

### 1. 多模态知识检索

支持三种检索模式：

- **向量检索（Vector Retrieval）**：基于语义相似度的检索
- **关键词检索（Keyword Retrieval）**：基于 BM25 算法的关键词匹配
- **混合检索（Hybrid Retrieval）**：结合向量和关键词检索的优势

### 2. 智能查询优化

- **查询重写（Query Rewriting）**：优化查询以提高检索质量
- **问题修订（Query Revision）**：基于对话历史理解完整意图
- **子问题扩展（Subquery Expansion）**：将复杂问题分解为多个子问题

### 3. 重排序机制

- 使用交叉编码器（Cross-Encoder）模型对检索结果进行重排序
- 提升召回文档的质量和相关性
- 支持降级到简单规则重排序

### 4. 上下文管理

- **智能窗口管理**：自动控制上下文长度，避免超出模型限制
- **临近片段扩展**：自动包含相关文档的前后片段，保持上下文连贯性
- **Token 计数**：精确计算和控制 token 使用

### 5. 多轮对话支持

- 维护对话历史
- 基于历史理解代词和省略
- 上下文感知的问题理解

### 6. 流式响应

- 支持 SSE（Server-Sent Events）流式输出
- 实时返回生成结果
- 提升用户体验

## 快速开始

### 基础使用

```python
from shuyixiao_agent import RAGAgent

# 创建 RAG Agent
agent = RAGAgent(
    collection_name="my_knowledge_base",
    use_reranker=True,
    retrieval_mode="hybrid"
)

# 添加文档
texts = [
    "Python 是一种高级编程语言...",
    "机器学习是人工智能的一个分支...",
]
agent.add_texts(texts)

# 查询
answer = agent.query(
    question="什么是 Python？",
    top_k=3,
    optimize_query=True
)
print(answer)
```

### 从文件加载

```python
# 从单个文件加载
agent.add_documents_from_file("path/to/document.txt")

# 从目录批量加载
agent.add_documents_from_directory(
    "path/to/documents/",
    glob_pattern="**/*.md"  # 只加载 markdown 文件
)
```

### 流式输出

```python
# 使用流式输出
stream = agent.query(
    question="解释一下 RAG 技术",
    stream=True
)

for chunk in stream:
    print(chunk, end="", flush=True)
```

## 配置选项

### 环境变量配置

在 `.env` 文件中配置：

```bash
# 向量数据库配置
VECTOR_DB_PATH=./data/chroma
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
EMBEDDING_DEVICE=cpu

# 文档分片配置
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# 检索配置
RETRIEVAL_TOP_K=10
RERANK_TOP_K=5
HYBRID_SEARCH_WEIGHT=0.5

# 上下文管理
MAX_CONTEXT_TOKENS=4000
ENABLE_CONTEXT_EXPANSION=true

# 查询优化
ENABLE_QUERY_REWRITE=true
ENABLE_SUBQUERY_EXPANSION=false
MAX_SUBQUERIES=3
```

### 代码配置

```python
from shuyixiao_agent import RAGAgent

agent = RAGAgent(
    collection_name="custom_kb",
    system_message="你是一个专业的技术助手",
    use_reranker=True,
    retrieval_mode="hybrid",  # vector, keyword, hybrid
    enable_query_optimization=True,
    enable_context_expansion=True
)
```

## API 接口

### 文档上传接口

#### 上传单个文件

```
POST /api/rag/upload/file
Content-Type: application/json

{
    "file_path": "/path/to/file.txt",
    "collection_name": "default"
}
```

#### 上传目录

```
POST /api/rag/upload/directory
Content-Type: application/json

{
    "directory_path": "/path/to/directory",
    "glob_pattern": "**/*.md",
    "collection_name": "default"
}
```

#### 上传文本

```
POST /api/rag/upload/texts
Content-Type: application/json

{
    "texts": ["文本1", "文本2"],
    "metadatas": [{"source": "doc1"}, {"source": "doc2"}],
    "collection_name": "default"
}
```

### 查询接口

#### 非流式查询

```
POST /api/rag/query
Content-Type: application/json

{
    "question": "什么是 Python？",
    "collection_name": "default",
    "session_id": "session_123",
    "top_k": 5,
    "use_history": true,
    "optimize_query": true
}
```

#### 流式查询

```
POST /api/rag/query/stream
Content-Type: application/json

{
    "question": "解释一下机器学习",
    "collection_name": "default",
    "session_id": "session_123",
    "top_k": 5,
    "use_history": true,
    "optimize_query": true
}
```

响应格式（SSE）：

```
data: {"content": "机器", "done": false}

data: {"content": "学习是", "done": false}

data: {"content": "...", "done": false}

data: {"content": "", "done": true}
```

### 管理接口

#### 获取知识库信息

```
GET /api/rag/info/{collection_name}
```

#### 清空知识库

```
DELETE /api/rag/clear/{collection_name}
```

#### 清空对话历史

```
DELETE /api/rag/history/{collection_name}/{session_id}
```

## 高级用法

### 自定义检索器

```python
from shuyixiao_agent.rag import VectorRetriever, KeywordRetriever

# 使用特定的检索器
agent = RAGAgent(collection_name="kb")

# 只使用向量检索
docs = agent.retrieve(
    query="查询内容",
    mode="vector",
    top_k=5
)

# 只使用关键词检索
docs = agent.retrieve(
    query="查询内容",
    mode="keyword",
    top_k=5
)
```

### 查询优化

```python
from shuyixiao_agent.rag import QueryOptimizer

optimizer = QueryOptimizer()

# 基于历史修订查询
history = [
    {"role": "user", "content": "什么是 Python？"},
    {"role": "assistant", "content": "Python 是..."},
]
revised = optimizer.revise_query_with_history(
    "它有什么特点？",  # 代词 "它" 指代 Python
    history
)
print(revised)  # "Python 有什么特点？"

# 查询重写
rewritten = optimizer.rewrite_query(
    "咋用这玩意儿？"
)
print(rewritten)  # "如何使用这个工具？"

# 子问题扩展
subqueries = optimizer.expand_to_subqueries(
    "对比 Python 和 Java 的优缺点"
)
print(subqueries)
# ["Python 的优点和缺点", "Java 的优点和缺点"]
```

### 上下文管理

```python
from shuyixiao_agent.rag import ContextManager

context_mgr = ContextManager(
    max_tokens=4000,
    enable_expansion=True
)

# 构建上下文
context = context_mgr.build_context(
    documents=docs,
    query="问题",
    separator="\n\n---\n\n"
)

# 扩展上下文（包含临近片段）
expanded_docs = context_mgr.expand_context(
    documents=selected_docs,
    all_documents=all_docs
)
```

### 重排序

```python
from shuyixiao_agent.rag import Reranker

reranker = Reranker(
    model_name="BAAI/bge-reranker-base"
)

# 对检索结果重排序
reranked = reranker.rerank(
    query="查询内容",
    documents=docs,
    top_k=5
)
```

## 性能优化

### 嵌入模型选择

- **小模型**（推荐用于 CPU）：
  - `BAAI/bge-small-zh-v1.5` (中文，维度 512)
  - `sentence-transformers/all-MiniLM-L6-v2` (英文，维度 384)

- **大模型**（推荐用于 GPU）：
  - `BAAI/bge-large-zh-v1.5` (中文，维度 1024)
  - `sentence-transformers/all-mpnet-base-v2` (英文，维度 768)

### 批量处理

```python
from shuyixiao_agent.rag import BatchEmbeddingManager

# 使用批量嵌入管理器
embedding_mgr = BatchEmbeddingManager(
    batch_size=32  # 根据内存调整
)
```

### 缓存 Agent

```python
# 复用 Agent 实例
agents = {}

def get_agent(collection_name):
    if collection_name not in agents:
        agents[collection_name] = RAGAgent(
            collection_name=collection_name
        )
    return agents[collection_name]
```

## 最佳实践

### 1. 文档分片

- 根据文档类型调整分片大小
- 技术文档：500-1000 字符
- 对话内容：200-500 字符
- 长文章：1000-2000 字符

### 2. 检索策略

- 对于精确匹配需求，使用关键词检索
- 对于语义理解需求，使用向量检索
- 对于一般场景，使用混合检索

### 3. 查询优化

- 在多轮对话中启用查询修订
- 对于复杂问题启用子问题扩展
- 在生产环境中关闭不必要的优化以提高速度

### 4. 上下文管理

- 根据模型能力设置合适的 max_context_tokens
- 启用上下文扩展以保持连贯性
- 为不同场景使用不同的分隔符

## 故障排查

### 问题：嵌入模型加载失败

**解决方案**：
- 检查网络连接
- 手动下载模型到本地
- 使用国内镜像源

### 问题：检索结果不准确

**解决方案**：
- 调整检索模式（尝试混合检索）
- 增加 top_k 值
- 启用重排序
- 优化文档分片策略

### 问题：响应速度慢

**解决方案**：
- 使用更小的嵌入模型
- 减少 top_k 值
- 关闭查询优化
- 使用 GPU 加速

### 问题：内存占用过高

**解决方案**：
- 使用更小的嵌入模型
- 减少批处理大小
- 清理不使用的 Agent 实例
- 使用持久化存储

## 示例代码

完整的示例代码请参考：
- `examples/07_rag_basic_usage.py` - 基础使用
- `examples/08_rag_file_upload.py` - 文件上传
- `examples/09_rag_streaming.py` - 流式响应

## 相关文档

- [API 参考](api_reference.md)
- [最佳实践](best_practices.md)
- [LangGraph 架构](langgraph_architecture.md)

