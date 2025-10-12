# 模型配置指南

本文档详细说明如何在 shuyixiao-agent 中配置和使用不同的云端模型。

## 概述

shuyixiao-agent 支持通过配置文件灵活选择不同的模型用于不同的任务：

1. **主对话模型** - 用于基础对话和 Agent 交互
2. **嵌入模型** - 用于文本向量化（RAG）
3. **重排序模型** - 用于检索结果重排序（RAG）
4. **查询优化模型** - 用于查询重写和优化（RAG）
5. **Agent 模型** - Agent 专用模型（可选）

所有模型都支持通过配置文件选择是否使用云端服务以及使用哪个具体的云端模型。

## 配置文件位置

配置文件位于项目根目录的 `.env` 文件中。如果没有该文件，请复制 `env_config_example.txt` 并重命名为 `.env`。

```bash
cp env_config_example.txt .env
```

## 可用模型列表

完整的模型列表请访问：https://ai.gitee.com/docs/products/apis

### 主要对话模型

适用于对话、Agent、查询优化等任务：

- `DeepSeek-V3` - **推荐**，强大的通用模型
- `Qwen2.5-72B-Instruct` - 强大的中文理解能力
- `Qwen2.5-14B-Instruct` - 平衡性能和速度
- `GLM-4-Plus` - 智谱 AI 的高性能模型
- `GLM-4-Flash` - 快速响应模型
- 更多模型请查看文档

### 嵌入模型

适用于文本向量化：

- `bge-large-zh-v1.5` - **推荐**，1024 维，高质量中文嵌入
- `bge-small-zh-v1.5` - 512 维，速度更快
- `text-embedding-ada-002` - OpenAI 兼容，1536 维
- 更多模型请查看文档

### 重排序模型

适用于检索结果重排序：

- `bge-reranker-base` - **推荐**，基础版本
- `bge-reranker-large` - 更高精度
- 更多模型请查看文档

## 配置示例

### 基础配置

```bash
# API 密钥（必需）
GITEE_AI_API_KEY=你的API密钥

# API 基础 URL
GITEE_AI_BASE_URL=https://ai.gitee.com/v1

# SSL 验证
SSL_VERIFY=false
```

### 主对话模型配置

```bash
# 是否使用云端对话模型
USE_CLOUD_CHAT_MODEL=true

# 云端对话模型名称
GITEE_AI_MODEL=DeepSeek-V3
```

### RAG 嵌入模型配置

```bash
# 使用云端嵌入服务（推荐）
USE_CLOUD_EMBEDDING=true

# 云端嵌入模型
CLOUD_EMBEDDING_MODEL=bge-large-zh-v1.5

# 如果不使用云端，可以配置本地模型
# USE_CLOUD_EMBEDDING=false
# EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
# EMBEDDING_DEVICE=cpu
```

### RAG 重排序模型配置

```bash
# 使用云端重排序服务（推荐）
USE_CLOUD_RERANKER=true

# 云端重排序模型
CLOUD_RERANKER_MODEL=bge-reranker-base

# 如果不使用云端，可以配置本地模型
# USE_CLOUD_RERANKER=false
# RERANKER_MODEL=BAAI/bge-reranker-base
# RERANKER_DEVICE=cpu
```

### 查询优化模型配置

```bash
# 查询优化使用的模型
# 留空则使用 GITEE_AI_MODEL 配置的模型
# 如果需要为查询优化使用不同的模型，可以单独配置
QUERY_OPTIMIZER_MODEL=

# 是否启用查询优化功能
ENABLE_QUERY_REWRITE=true
ENABLE_SUBQUERY_EXPANSION=false
```

### Agent 模型配置

```bash
# Agent 使用的模型
# 留空则使用 GITEE_AI_MODEL 配置的模型
# 如果需要为 Agent 使用不同的模型，可以单独配置
AGENT_MODEL=

# Agent 最大迭代次数
AGENT_MAX_ITERATIONS=10
```

## 高级配置场景

### 场景 1：全部使用云端服务（推荐）

这是最简单且推荐的配置方式，无需下载任何本地模型：

```bash
GITEE_AI_API_KEY=你的API密钥

# 主对话模型
USE_CLOUD_CHAT_MODEL=true
GITEE_AI_MODEL=DeepSeek-V3

# RAG 嵌入模型
USE_CLOUD_EMBEDDING=true
CLOUD_EMBEDDING_MODEL=bge-large-zh-v1.5

# RAG 重排序模型
USE_CLOUD_RERANKER=true
CLOUD_RERANKER_MODEL=bge-reranker-base
```

**优点**：
- 无需下载大型模型文件
- 启动速度快
- 始终使用最新版本
- 自动享受云端 GPU 加速

### 场景 2：为不同任务使用不同模型

如果您想为不同的任务使用不同的优化模型：

```bash
GITEE_AI_API_KEY=你的API密钥

# 主对话使用强大模型
GITEE_AI_MODEL=DeepSeek-V3

# Agent 使用快速响应模型
AGENT_MODEL=GLM-4-Flash

# 查询优化使用中等模型
QUERY_OPTIMIZER_MODEL=Qwen2.5-14B-Instruct

# RAG 模型
USE_CLOUD_EMBEDDING=true
CLOUD_EMBEDDING_MODEL=bge-large-zh-v1.5
USE_CLOUD_RERANKER=true
CLOUD_RERANKER_MODEL=bge-reranker-large
```

**适用场景**：
- Agent 需要快速响应，使用轻量级模型
- 复杂推理任务使用强大模型
- 精细控制成本和性能

### 场景 3：混合使用云端和本地模型

如果您有部分本地模型资源：

```bash
GITEE_AI_API_KEY=你的API密钥

# 主对话使用云端
USE_CLOUD_CHAT_MODEL=true
GITEE_AI_MODEL=DeepSeek-V3

# 嵌入使用本地模型（节省 API 调用）
USE_CLOUD_EMBEDDING=false
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
EMBEDDING_DEVICE=cuda

# 重排序使用云端（避免下载大模型）
USE_CLOUD_RERANKER=true
CLOUD_RERANKER_MODEL=bge-reranker-base
```

**适用场景**：
- 有本地 GPU 资源
- 需要频繁的向量化操作
- 希望减少 API 调用成本

## 配置验证

### 验证配置是否生效

创建一个简单的测试脚本 `test_config.py`：

```python
from shuyixiao_agent.config import settings

print("配置加载成功！")
print(f"API Key: {settings.gitee_ai_api_key[:10]}...")
print(f"主对话模型: {settings.gitee_ai_model}")
print(f"Agent 模型: {settings.agent_model or '使用主模型'}")
print(f"查询优化模型: {settings.query_optimizer_model or '使用主模型'}")
print(f"嵌入模型: {'云端 - ' + settings.cloud_embedding_model if settings.use_cloud_embedding else '本地 - ' + settings.embedding_model}")
print(f"重排序模型: {'云端 - ' + settings.cloud_reranker_model if settings.use_cloud_reranker else '本地 - ' + settings.reranker_model}")
```

运行测试：

```bash
poetry run python test_config.py
```

### 测试模型调用

```python
from shuyixiao_agent.gitee_ai_client import GiteeAIClient

# 测试主对话模型
client = GiteeAIClient()
response = client.simple_chat("你好，请介绍一下你自己")
print(f"模型回复: {response}")
```

## 成本优化建议

1. **根据任务选择模型大小**
   - 简单任务使用小模型（如 GLM-4-Flash）
   - 复杂推理使用大模型（如 DeepSeek-V3）

2. **合理使用缓存**
   - 嵌入向量会自动缓存
   - 避免重复处理相同文档

3. **调整批处理大小**
   - 嵌入和重排序支持批处理
   - 适当增加批处理大小可以减少 API 调用次数

4. **启用故障转移**
   ```bash
   ENABLE_FAILOVER=true
   ```
   这样即使某个模型暂时不可用，系统也能自动切换到其他可用模型

## 故障排查

### 问题 1：API Key 无效

**错误信息**：`未提供 API Key` 或 `401 Unauthorized`

**解决方案**：
1. 检查 `.env` 文件中的 `GITEE_AI_API_KEY` 配置
2. 确认 API Key 在 https://ai.gitee.com/dashboard/settings/tokens 是有效的

### 问题 2：模型不存在

**错误信息**：`404 Not Found` 或类似错误

**解决方案**：
1. 访问 https://ai.gitee.com/docs/products/apis 确认模型名称
2. 确保模型名称拼写正确
3. 检查您的账号是否有权限访问该模型

### 问题 3：SSL 连接错误

**错误信息**：`SSL connection error`

**解决方案**：
```bash
SSL_VERIFY=false
```

### 问题 4：云端服务初始化失败

**错误信息**：`云端嵌入服务初始化失败`

**解决方案**：
1. 检查 API Key 配置
2. 检查网络连接
3. 临时切换到本地模型：
   ```bash
   USE_CLOUD_EMBEDDING=false
   ```

## 最佳实践

1. **开发环境**：使用小模型快速迭代
   ```bash
   GITEE_AI_MODEL=GLM-4-Flash
   AGENT_MODEL=GLM-4-Flash
   ```

2. **生产环境**：使用高质量模型
   ```bash
   GITEE_AI_MODEL=DeepSeek-V3
   CLOUD_EMBEDDING_MODEL=bge-large-zh-v1.5
   CLOUD_RERANKER_MODEL=bge-reranker-large
   ```

3. **定期更新**：关注模型文档，尝试新发布的模型
   - 新模型通常有更好的性能
   - 或者更优的性价比

4. **监控使用情况**：在 https://ai.gitee.com 查看使用日志
   - 了解模型调用频率
   - 优化成本和性能

## 相关文档

- [Gitee AI 模型广场文档](https://ai.gitee.com/docs/products/apis)
- [快速开始指南](../QUICK_START.md)
- [RAG 使用指南](./rag_guide.md)
- [API 参考](./api_reference.md)

## 常见问题

**Q: 如何知道哪个模型最适合我的任务？**

A: 建议从推荐的默认配置开始，然后根据实际效果调整。通常：
- 对话任务：DeepSeek-V3 或 Qwen2.5-72B-Instruct
- 快速响应：GLM-4-Flash
- 中文理解：Qwen 系列

**Q: 可以同时使用多个不同的 API Key 吗？**

A: 目前每个 Agent 实例使用一个 API Key。如果需要使用多个 Key，可以创建多个 Agent 实例。

**Q: 如何在代码中动态切换模型？**

A: 在创建客户端时指定模型：
```python
from shuyixiao_agent.gitee_ai_client import GiteeAIClient

# 使用特定模型
client = GiteeAIClient(model="GLM-4-Flash")
```

**Q: 本地模型和云端模型可以无缝切换吗？**

A: 是的，只需修改配置文件中的 `USE_CLOUD_*` 选项，无需修改代码。

