# 模型配置更新说明

## 更新日期
2025-10-12

## 更新概述

本次更新为 shuyixiao-agent 添加了完整的模型配置灵活性，允许用户通过配置文件控制所有模型的选择，包括是否使用云模型以及使用哪个具体的云模型。

## 主要变更

### 1. 配置文件更新 (`env_config_example.txt`)

新增和优化了以下配置项：

#### 主对话模型配置
```bash
# 新增：是否使用云端对话模型
USE_CLOUD_CHAT_MODEL=true

# 增强：云端对话模型名称（添加了更多可选模型说明）
GITEE_AI_MODEL=DeepSeek-V3

# 新增：本地对话模型配置
LOCAL_CHAT_MODEL=your-local-model-path
LOCAL_CHAT_DEVICE=cpu
```

#### Agent 模型配置
```bash
# 新增：Agent 专用模型配置
AGENT_MODEL=

# 说明：留空则使用 GITEE_AI_MODEL
# 可配置不同的模型用于 Agent 任务
```

#### 查询优化模型配置
```bash
# 新增：查询优化专用模型配置
QUERY_OPTIMIZER_MODEL=

# 说明：留空则使用 GITEE_AI_MODEL
# 可配置不同的模型用于查询优化
```

#### RAG 模型配置优化
```bash
# 优化：嵌入模型配置（添加更多可选模型说明）
USE_CLOUD_EMBEDDING=true
CLOUD_EMBEDDING_MODEL=bge-large-zh-v1.5

# 优化：重排序模型配置（添加更多可选模型说明）
USE_CLOUD_RERANKER=true
CLOUD_RERANKER_MODEL=bge-reranker-base
```

#### 其他配置
```bash
# 新增：故障转移配置
ENABLE_FAILOVER=true

# 重新组织：高级配置
MAX_CONTEXT_TOKENS=4000
ENABLE_CONTEXT_EXPANSION=true
MAX_SUBQUERIES=3
```

### 2. 配置类更新 (`src/shuyixiao_agent/config.py`)

#### 新增配置字段

```python
# 主对话模型配置
use_cloud_chat_model: bool = True
local_chat_model: str = ""
local_chat_device: str = "cpu"

# Agent 模型配置
agent_model: str = ""

# 查询优化模型配置
query_optimizer_model: str = ""
```

### 3. 模块更新

#### Simple Agent (`src/shuyixiao_agent/agents/simple_agent.py`)
- 新增自动使用配置的 `AGENT_MODEL`
- 如果未配置，则使用 `GITEE_AI_MODEL`

```python
# 修改前
self.client = GiteeAIClient(api_key=api_key, model=model)

# 修改后
if model is None:
    model = settings.agent_model or settings.gitee_ai_model
self.client = GiteeAIClient(api_key=api_key, model=model)
```

#### Tool Agent (`src/shuyixiao_agent/agents/tool_agent.py`)
- 同样的逻辑更新
- 支持独立配置 Agent 模型

#### Query Optimizer (`src/shuyixiao_agent/rag/query_optimizer.py`)
- 新增自动使用配置的 `QUERY_OPTIMIZER_MODEL`
- 如果未配置，则使用 `GITEE_AI_MODEL`

```python
# 新增逻辑
if settings.query_optimizer_model:
    self.client = client or GiteeAIClient(model=settings.query_optimizer_model)
else:
    self.client = client or GiteeAIClient()
```

### 4. 新增文档

#### 模型配置指南 (`docs/model_configuration.md`)
- 详细的模型配置说明
- 可用模型列表参考
- 多种配置场景示例
- 故障排查指南
- 最佳实践建议

#### 配置验证脚本 (`test_model_config.py`)
- 验证配置是否正确加载
- 测试模型连接
- 显示所有配置项
- 提供使用提示

## 使用方式

### 1. 更新配置文件

复制新的配置示例：

```bash
cp env_config_example.txt .env
```

编辑 `.env` 文件，配置您的模型选择。

### 2. 验证配置

运行配置验证脚本：

```bash
poetry run python test_model_config.py
```

### 3. 使用不同的模型配置

#### 场景 A：全部使用云端默认模型（推荐）

```bash
GITEE_AI_API_KEY=你的API密钥
USE_CLOUD_CHAT_MODEL=true
GITEE_AI_MODEL=DeepSeek-V3
USE_CLOUD_EMBEDDING=true
CLOUD_EMBEDDING_MODEL=bge-large-zh-v1.5
USE_CLOUD_RERANKER=true
CLOUD_RERANKER_MODEL=bge-reranker-base
```

#### 场景 B：为不同任务使用不同模型

```bash
GITEE_AI_API_KEY=你的API密钥

# 主对话使用强大模型
GITEE_AI_MODEL=DeepSeek-V3

# Agent 使用快速模型
AGENT_MODEL=GLM-4-Flash

# 查询优化使用中等模型
QUERY_OPTIMIZER_MODEL=Qwen2.5-14B-Instruct

# RAG 使用高质量模型
CLOUD_EMBEDDING_MODEL=bge-large-zh-v1.5
CLOUD_RERANKER_MODEL=bge-reranker-large
```

## 功能特性

### 1. 模型独立配置
- ✅ 每个功能模块可以独立配置模型
- ✅ 支持为不同任务使用不同的模型
- ✅ 灵活的后备机制（未配置时使用默认模型）

### 2. 云端/本地切换
- ✅ 通过配置项轻松切换云端和本地模型
- ✅ 无需修改代码
- ✅ 支持混合使用

### 3. 配置验证
- ✅ 提供配置验证工具
- ✅ 详细的配置说明
- ✅ 故障排查指南

### 4. 文档完善
- ✅ 详细的配置指南
- ✅ 多种场景示例
- ✅ 最佳实践建议

## 向后兼容性

✅ **完全向后兼容**

- 所有新增配置项都有默认值
- 现有配置文件无需修改即可继续使用
- 现有代码无需修改

如果您不添加新的配置项，系统将按照原有方式工作。

## 配置优先级

配置的优先级从高到低：

1. **代码中显式指定的模型**
   ```python
   client = GiteeAIClient(model="GLM-4-Flash")
   ```

2. **专用模型配置**
   - `AGENT_MODEL`
   - `QUERY_OPTIMIZER_MODEL`

3. **主对话模型配置**
   - `GITEE_AI_MODEL`

4. **默认值**
   - `DeepSeek-V3`

## 示例代码

### 使用默认配置

```python
from shuyixiao_agent.agents import SimpleAgent

# 自动使用配置文件中的 AGENT_MODEL 或 GITEE_AI_MODEL
agent = SimpleAgent()
response = agent.chat("你好")
```

### 显式指定模型

```python
from shuyixiao_agent.agents import SimpleAgent

# 显式指定模型，优先级最高
agent = SimpleAgent(model="GLM-4-Flash")
response = agent.chat("你好")
```

### 使用 RAG Agent

```python
from shuyixiao_agent.rag import RAGAgent

# 自动使用配置文件中的模型设置
rag_agent = RAGAgent()

# 嵌入模型：根据 USE_CLOUD_EMBEDDING 和 CLOUD_EMBEDDING_MODEL
# 重排序模型：根据 USE_CLOUD_RERANKER 和 CLOUD_RERANKER_MODEL
# 对话模型：使用 GITEE_AI_MODEL
```

## 可用模型参考

完整的模型列表请访问：https://ai.gitee.com/docs/products/apis

### 文本生成模型（对话、Agent、查询优化）
- DeepSeek-V3 ⭐ 推荐
- Qwen2.5-72B-Instruct
- Qwen2.5-14B-Instruct
- GLM-4-Plus
- GLM-4-Flash
- 更多...

### 嵌入模型（文本向量化）
- bge-large-zh-v1.5 ⭐ 推荐
- bge-small-zh-v1.5
- text-embedding-ada-002
- 更多...

### 重排序模型（检索结果重排序）
- bge-reranker-base ⭐ 推荐
- bge-reranker-large
- 更多...

## 测试建议

1. **配置验证**
   ```bash
   poetry run python test_model_config.py
   ```

2. **功能测试**
   ```bash
   # 测试基础对话
   poetry run python examples/01_simple_chat.py
   
   # 测试 Tool Agent
   poetry run python examples/02_tool_agent.py
   
   # 测试 RAG
   poetry run python examples/07_rag_basic_usage.py
   ```

3. **性能测试**
   - 测试不同模型的响应速度
   - 测试不同模型的回答质量
   - 根据需求调整配置

## 故障排查

### 问题 1：配置未生效

**检查清单**：
- [ ] 确认 `.env` 文件在项目根目录
- [ ] 确认配置项名称拼写正确
- [ ] 运行 `test_model_config.py` 验证配置
- [ ] 重启应用程序

### 问题 2：模型调用失败

**检查清单**：
- [ ] 确认 API Key 有效
- [ ] 确认模型名称正确（参考文档）
- [ ] 检查网络连接
- [ ] 尝试设置 `SSL_VERIFY=false`

### 问题 3：模型响应质量不佳

**建议**：
- 尝试更换更强大的模型
- 调整 temperature 参数
- 优化 system_message

## 下一步计划

未来可能的增强：

1. **模型性能监控**
   - 添加模型调用统计
   - 记录响应时间
   - 成本追踪

2. **模型自动选择**
   - 根据任务复杂度自动选择模型
   - 动态负载均衡

3. **更多模型支持**
   - 支持更多云服务提供商
   - 支持更多本地模型框架

4. **配置 UI**
   - 提供 Web 界面配置模型
   - 实时预览配置效果

## 贡献

如果您发现问题或有改进建议，欢迎：

1. 提交 Issue
2. 提交 Pull Request
3. 参与讨论

## 相关链接

- [Gitee AI 模型文档](https://ai.gitee.com/docs/products/apis)
- [模型配置指南](./docs/model_configuration.md)
- [快速开始](./QUICK_START.md)
- [项目文档](./docs/)

## 致谢

感谢 Gitee AI 提供的模型服务和 API 支持。

---

**最后更新**: 2025-10-12  
**版本**: 1.0.0

