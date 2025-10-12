# RAG 存储位置和工作原理说明

## 📁 存储位置

### 向量数据库存储路径
```
./data/chroma/
```

**配置位置：** `src/shuyixiao_agent/config.py` 第 98-101 行

```python
vector_db_path: str = Field(
    default="./data/chroma",
    description="向量数据库存储路径"
)
```

### 完整目录结构
```
/Users/shuyixiao/PycharmProjects/shuyixiao-agent/
└── data/
    └── chroma/              # ChromaDB 向量数据库目录
        ├── chroma.sqlite3   # 数据库文件
        └── [集合目录]/      # 每个知识库一个集合
```

## 📝 文档分割原理

### 为什么显示"已添加 6 个文档"？

你上传的文本内容是：
```
你好，我是舒一笑不秃头，一名资深Java开发工程师和技术博主。
IDEA插件-PandaCoder（熊猫编码器）作者
生成式AI应用工程师(高级)认证
阿里云博客专家
Java应用开发职业技能等级认证
HarmonyOS应用开发者基础认证
```

这段文本被自动分割成了 **6 个文档片段（chunks）**。

### 分割配置

**配置位置：** `src/shuyixiao_agent/config.py` 第 113-121 行

```python
# 文档分片配置
chunk_size: int = Field(
    default=500,
    description="文档分片大小（字符数）"
)
chunk_overlap: int = Field(
    default=50,
    description="文档分片重叠大小（字符数）"
)
```

### 为什么要分割文档？

1. **向量检索效率**：小片段更容易精确匹配用户问题
2. **语义完整性**：每个片段包含完整的语义信息
3. **上下文控制**：避免单个文档过长超出模型限制

## 🔍 知识库名称转换

### 转换规则

| 原始名称 | 转换后名称 | 说明 |
|---------|-----------|------|
| `舒一笑不秃头个人信息` | `kb_dd65ff91` | 中文转为前缀+哈希 |
| `default` | `default` | 合法名称保持不变 |
| `my-knowledge` | `my-knowledge` | 合法名称保持不变 |
| `我的知识库123` | `123_a1b2c3d4` | 提取数字+哈希 |

### 命名约束（ChromaDB 要求）

✅ **允许的字符：** 
- 英文字母：`a-z`, `A-Z`
- 数字：`0-9`
- 特殊符号：`.`, `_`, `-`

❌ **不允许的字符：**
- 中文字符
- 空格
- 其他特殊符号

📏 **长度要求：** 3-512 个字符

🎯 **开头和结尾：** 必须是字母或数字

## 📊 查看存储信息

### 方法1：通过 Web 界面查看

访问 "知识库信息" 标签，输入知识库名称（如 `舒一笑不秃头个人信息`），点击"刷新信息"。

### 方法2：通过代码查看

```python
from shuyixiao_agent.rag.rag_agent import RAGAgent

# 创建 RAG Agent
agent = RAGAgent(collection_name="kb_dd65ff91")

# 查看文档数量
count = agent.get_document_count()
print(f"知识库中有 {count} 个文档片段")
```

### 方法3：直接查看数据库文件

```bash
# 进入数据目录
cd data/chroma/

# 查看 SQLite 数据库
sqlite3 chroma.sqlite3

# 查询所有集合
SELECT * FROM collections;

# 退出
.quit
```

## 🔄 数据流程

```
用户上传文本
    ↓
文本分割（chunk_size=500, overlap=50）
    ↓
生成向量嵌入（使用 bge-large-zh-v1.5）
    ↓
存储到 ChromaDB（./data/chroma/）
    ↓
建立索引（支持相似度搜索）
```

## 🛠️ 修改存储路径

如果要修改存储位置，有两种方式：

### 方式1：修改配置文件

编辑 `src/shuyixiao_agent/config.py`：
```python
vector_db_path: str = Field(
    default="/你的自定义路径/chroma",  # 修改这里
    description="向量数据库存储路径"
)
```

### 方式2：设置环境变量

```bash
export VECTOR_DB_PATH="/你的自定义路径/chroma"
```

或在 PyCharm 的运行配置中添加环境变量：
```
VECTOR_DB_PATH=/你的自定义路径/chroma
```

## 📈 存储空间估算

- 每个文档片段（chunk）：约 1-2 KB
- 向量维度：1024（bge-large-zh-v1.5）
- 每个向量：约 4 KB
- **总计**：每个 chunk 约 5-6 KB

**示例：**
- 10,000 个文档片段 ≈ 50-60 MB
- 100,000 个文档片段 ≈ 500-600 MB

## 🔧 常见问题

### Q1：如何清空知识库？

**Web 界面：**
"知识库管理" → 输入知识库名称 → 点击"清空知识库"

**代码：**
```python
agent.clear_knowledge_base()
```

### Q2：如何删除整个数据库？

```bash
# 谨慎！这会删除所有知识库
rm -rf data/chroma/
```

### Q3：数据库文件可以迁移吗？

可以！直接复制 `data/chroma/` 整个目录到新位置即可。

### Q4：支持多用户吗？

当前版本是单用户设计。如需多用户支持，建议：
- 为每个用户创建独立的集合（知识库）
- 使用用户ID作为集合名称前缀

## 📚 相关文档

- ChromaDB 官方文档：https://docs.trychroma.com/
- 配置文件详解：`src/shuyixiao_agent/config.py`
- RAG Agent 实现：`src/shuyixiao_agent/rag/rag_agent.py`
- 向量存储管理：`src/shuyixiao_agent/rag/vector_store.py`

