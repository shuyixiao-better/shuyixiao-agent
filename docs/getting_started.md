# 快速开始

本指南将帮助你快速上手 shuyixiao-agent 项目。

## 目录

- [环境准备](#环境准备)
- [安装](#安装)
- [配置](#配置)
- [第一个 Agent](#第一个-agent)
- [下一步](#下一步)

## 环境准备

### 系统要求

- Python >= 3.12
- Poetry（推荐）或 pip
- 稳定的网络连接

### 获取 API Key

1. 访问 [码云 AI 平台](https://ai.gitee.com/)
2. 注册/登录账号
3. 前往 **工作台 -> 设置 -> 访问令牌**
4. 创建一个新的访问令牌
5. 购买全模型资源包或特定模型的资源包

详细步骤请参考 [码云 AI 文档](https://ai.gitee.com/docs/products/apis)。

## 安装

### 使用 Poetry（推荐）

```bash
# 克隆仓库
git clone https://github.com/your-username/shuyixiao-agent.git
cd shuyixiao-agent

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

### 使用 pip

```bash
# 克隆仓库
git clone https://github.com/your-username/shuyixiao-agent.git
cd shuyixiao-agent

# 安装依赖
pip install -e .
```

### 验证安装

```bash
python -c "from src.shuyixiao_agent import SimpleAgent; print('安装成功！')"
```

## 配置

### 1. 创建环境变量文件

```bash
# 复制示例文件
cp .env.example .env
```

### 2. 编辑 .env 文件

打开 `.env` 文件，填入你的配置：

```env
# 必填：你的码云 AI API Key
GITEE_AI_API_KEY=your_actual_api_key_here

# 可选：选择要使用的模型（默认 Qwen2.5-7B-Instruct）
GITEE_AI_MODEL=Qwen/Qwen2.5-7B-Instruct

# 其他配置保持默认即可
```

### 3. 可用的模型

码云 AI 支持多种模型，包括：

- **Qwen/Qwen2.5-7B-Instruct** - 通用对话模型（推荐）
- **Qwen/Qwen2.5-14B-Instruct** - 更强大的对话模型
- **Qwen/Qwen2.5-72B-Instruct** - 最强大的对话模型
- 更多模型请访问 [模型广场](https://ai.gitee.com/serverless)

## 第一个 Agent

### 最简单的例子

创建一个文件 `my_first_agent.py`：

```python
from src.shuyixiao_agent import SimpleAgent
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建 Agent
agent = SimpleAgent()

# 开始对话
response = agent.chat("你好！请介绍一下你自己。")
print(response)
```

运行：

```bash
python my_first_agent.py
```

### 运行示例代码

项目提供了多个示例，你可以直接运行：

```bash
# 示例 1: 简单对话
python examples/01_simple_chat.py

# 示例 2: 带工具的 Agent
python examples/02_tool_agent.py

# 示例 3: 自定义工具
python examples/03_custom_tool.py

# 示例 4: API 客户端
python examples/04_api_client.py
```

## 核心概念

### SimpleAgent

最基础的对话 Agent，适合简单的问答场景。

```python
from src.shuyixiao_agent import SimpleAgent

agent = SimpleAgent(
    system_message="你是一个友好的助手"
)

response = agent.chat("Python 有什么特点？")
```

### ToolAgent

支持工具调用的 Agent，可以让 AI 使用工具完成复杂任务。

```python
from src.shuyixiao_agent.agents.tool_agent import ToolAgent

agent = ToolAgent()

# 注册工具
agent.register_tool(
    name="get_time",
    func=lambda: "2024-01-01 12:00:00",
    description="获取当前时间",
    parameters={"type": "object", "properties": {}}
)

response = agent.run("现在几点了？")
```

### GiteeAIClient

直接使用 API 客户端，提供更多控制。

```python
from src.shuyixiao_agent import GiteeAIClient

client = GiteeAIClient()

# 简单对话
response = client.simple_chat("你好")

# 高级用法
response = client.chat_completion(
    messages=[
        {"role": "system", "content": "你是助手"},
        {"role": "user", "content": "你好"}
    ],
    temperature=0.7,
    max_tokens=1000
)
```

## 常见问题

### Q: 如何更换模型？

A: 在 `.env` 文件中设置 `GITEE_AI_MODEL`，或在创建 Agent 时指定：

```python
agent = SimpleAgent(model="Qwen/Qwen2.5-14B-Instruct")
```

### Q: 如何启用故障转移？

A: 在 `.env` 中设置 `ENABLE_FAILOVER=true`（默认已启用）。启用后，如果当前算力出现故障，系统会自动切换到其他可用算力。

### Q: 遇到 API 错误怎么办？

A: 检查以下几点：
1. API Key 是否正确
2. 是否购买了资源包
3. 网络连接是否正常
4. 查看错误信息的具体内容

### Q: 如何查看 API 使用情况？

A: 登录码云 AI 平台，前往 **工作台 -> 使用日志** 查看详细的使用记录和费用。

## 下一步

- 📚 查看 [示例代码](../examples/) 学习更多用法
- 📖 阅读 [API 参考文档](./api_reference.md) 了解详细 API
- 🛠️ 学习 [如何创建自定义工具](./custom_tools.md)
- 🏗️ 了解 [LangGraph 架构](./langgraph_architecture.md)
- 💡 查看 [最佳实践](./best_practices.md)

## 获取帮助

如果遇到问题：

1. 查看 [常见问题](./faq.md)
2. 阅读 [码云 AI 官方文档](https://ai.gitee.com/docs/products/apis)
3. 提交 [GitHub Issue](https://github.com/your-username/shuyixiao-agent/issues)

