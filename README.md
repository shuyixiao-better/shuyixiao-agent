# shuyixiao-agent

基于 LangGraph 和码云 AI 的智能 Agent 框架

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📖 简介

`shuyixiao-agent` 是一个基于 [LangGraph](https://github.com/langchain-ai/langgraph) 和 [码云 AI](https://ai.gitee.com/) 构建的现代化智能 Agent 框架。提供清晰的代码结构、完整的功能模块和详细的文档，适合学习和生产使用。

### ✨ 核心特性

- 🚀 **LangGraph 框架**：基于业界主流的 Agent 框架构建
- 🤖 **码云 AI 集成**：支持 DeepSeek-V3、Qwen、GLM-4 等多种模型
- ⚙️ **灵活配置**：支持为不同任务配置不同模型，云端/本地自由切换
- 📖 **RAG 系统**：完整的检索增强生成系统
  - 多模态检索（向量、关键词、混合）
  - 智能查询优化和重写
  - 重排序机制提升召回质量
  - 流式响应支持
- 🛠️ **工具系统**：
  - 13个基础工具（时间、计算、编码等）
  - 10个AI驱动的智能工具（代码审查、创意生成、决策分析等）
- 🔗 **Prompt Chaining**：提示链设计模式 ⭐ 新功能
  - 5个预定义场景（文档生成、代码审查、研究规划、故事创作、产品分析）
  - 模块化、可控、高质量的输出
  - 支持自定义提示链
  - Web界面和命令行双模式
- 🎨 **Web 界面**：现代化的交互界面，支持 RAG 知识库管理
- 📚 **完整文档**：详细的 API 文档和使用指南
- 💡 **丰富示例**：11个实用示例快速上手

### 🎯 技术栈

- **框架**：LangGraph、LangChain
- **AI 模型**：码云 AI (DeepSeek-V3, Qwen, GLM-4 等)
- **设计模式**：Prompt Chaining（提示链）
- **RAG 组件**：ChromaDB、Sentence Transformers、BM25、Cross-Encoder
- **编程语言**：Python 3.12+
- **Web 框架**：FastAPI、Uvicorn
- **包管理**：Poetry

## 🚀 快速开始

### 1. 环境准备

**系统要求**
- Python >= 3.12
- Poetry 或 pip
- 码云 AI API Key

**获取 API Key**
1. 访问 [码云 AI 平台](https://ai.gitee.com/)
2. 注册/登录账号
3. 前往 **工作台 -> 设置 -> 访问令牌** 创建令牌
4. 购买模型资源包

### 2. 安装

```bash
# 克隆仓库
git clone https://github.com/your-username/shuyixiao-agent.git
cd shuyixiao-agent

# 使用 Poetry 安装（推荐）
poetry install
poetry shell

# 或使用 pip 安装
pip install -e .
```

### 3. 配置

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑 .env 文件，配置你的 API Key
# GITEE_AI_API_KEY=your_api_key_here
```

**核心配置项：**

```bash
# 必填：API 密钥
GITEE_AI_API_KEY=your_api_key_here

# 主对话模型（默认：DeepSeek-V3）
GITEE_AI_MODEL=DeepSeek-V3

# RAG 配置（推荐使用云端服务，启动更快）
USE_CLOUD_EMBEDDING=true
CLOUD_EMBEDDING_MODEL=bge-large-zh-v1.5
USE_CLOUD_RERANKER=true
CLOUD_RERANKER_MODEL=bge-reranker-base
```

💡 查看 [模型配置文档](docs/model_configuration.md) 了解高级配置

### 4. 启动 Web 界面（推荐）

```bash
# 方式 1：自动启动（推荐，自动选择可用端口）
python run_web_auto.py

# 方式 2：标准启动
python run_web.py

# 浏览器访问
http://localhost:8000
```

**Web 界面功能：**
- ✅ 流式对话输出
- ✅ Markdown 渲染（代码高亮、表格等）
- ✅ Agent 类型切换
- ✅ 对话历史管理
- ✅ RAG 知识库管理
- ✅ 文档上传与检索

### 5. 或运行示例代码

```bash
# 基础示例
python examples/01_simple_chat.py          # 简单对话
python examples/02_tool_agent.py           # 工具调用
python examples/03_custom_tool.py          # 自定义工具
python examples/04_api_client.py           # API 客户端
python examples/05_all_tools_demo.py       # 所有工具演示

# AI 智能工具
python examples/06_ai_powered_tools_demo.py

# RAG 示例
python examples/07_rag_basic_usage.py      # RAG 基础
python examples/08_rag_file_upload.py      # 文件上传
python examples/09_rag_streaming.py        # 流式响应

# Prompt Chaining 示例 ⭐ 新功能
python examples/10_prompt_chaining_demo.py    # 完整功能（5个场景）
python examples/11_prompt_chaining_simple.py  # 快速体验（3个示例）
```

## 📂 项目结构

```
shuyixiao-agent/
├── src/shuyixiao_agent/       # 主代码
│   ├── agents/                # Agent 实现
│   │   ├── simple_agent.py   # 简单对话 Agent
│   │   ├── tool_agent.py     # 工具调用 Agent
│   │   └── prompt_chaining_agent.py # 提示链 Agent ⭐
│   ├── tools/                 # 工具集
│   │   ├── basic_tools.py    # 基础工具（13个）
│   │   └── ai_powered_tools.py # AI智能工具（10个）
│   ├── rag/                   # RAG 模块
│   │   ├── embeddings.py      # 嵌入模型
│   │   ├── vector_store.py    # 向量存储
│   │   ├── retrievers.py      # 检索器
│   │   ├── query_optimizer.py # 查询优化
│   │   └── rag_agent.py       # RAG Agent
│   ├── config.py              # 配置管理
│   ├── gitee_ai_client.py    # API 客户端
│   ├── web_app.py             # Web 应用
│   └── static/                # 前端资源
├── examples/                  # 示例代码（11个）
├── docs/                      # 文档
│   ├── prompt_chaining_guide.md # Prompt Chaining 指南 ⭐
│   └── ...                    # 其他文档
├── data/chroma/              # 向量数据库（自动创建）
├── run_web.py                 # Web 启动脚本
├── run_web_auto.py            # 自动化启动脚本
├── PROMPT_CHAINING_README.md  # Prompt Chaining 快速开始 ⭐
├── .env.example               # 环境变量示例
└── README.md                  # 本文件
```

## 💡 使用示例

### 简单对话

```python
from src.shuyixiao_agent import SimpleAgent
from dotenv import load_dotenv

load_dotenv()

# 创建 Agent
agent = SimpleAgent(
    system_message="你是一个友好的AI助手"
)

# 开始对话
response = agent.chat("Python 有什么特点？")
print(response)
```

### 工具调用

```python
from src.shuyixiao_agent.agents.tool_agent import ToolAgent
from src.shuyixiao_agent.tools import get_basic_tools

agent = ToolAgent()

# 批量注册所有基础工具
for tool in get_basic_tools():
    agent.register_tool(**tool)

# 使用工具
response = agent.run("现在几点了？帮我计算 25 * 4 + 10")
print(response)
```

### RAG 检索增强

```python
from src.shuyixiao_agent import RAGAgent

# 创建 RAG Agent
agent = RAGAgent(
    collection_name="my_knowledge",
    use_reranker=True,
    retrieval_mode="hybrid"
)

# 添加文档
texts = [
    "Python 是一种高级编程语言...",
    "LangChain 是一个 LLM 应用框架...",
]
agent.add_texts(texts)

# 查询
answer = agent.query(
    question="什么是 Python？",
    top_k=3,
    optimize_query=True
)
print(answer)

# 流式响应
for chunk in agent.query(question="介绍 LangChain", stream=True):
    print(chunk, end="", flush=True)
```

### Prompt Chaining（提示链）⭐ 新功能

```python
from src.shuyixiao_agent.gitee_ai_client import GiteeAIClient
from src.shuyixiao_agent.agents.prompt_chaining_agent import (
    PromptChainingAgent,
    DocumentGenerationChain
)

# 初始化
llm_client = GiteeAIClient()
agent = PromptChainingAgent(llm_client, verbose=True)

# 使用文档生成链（大纲→内容→示例→润色）
agent.create_chain("doc_gen", DocumentGenerationChain.get_steps())
result = agent.run_chain("doc_gen", "Python 异步编程入门")

if result.success:
    print(result.final_output)  # 生成的完整文档
    print(f"总耗时: {result.execution_time:.2f}秒")
```

**5个预定义场景**：
- 📄 文档生成 - 自动生成技术文档
- 🔍 代码审查 - 系统化代码审查流程
- 🔬 研究规划 - 问题→计划转化
- 📖 故事创作 - 创意写作工作流
- 💡 产品分析 - 需求分析和规划

详见：[Prompt Chaining 快速开始](PROMPT_CHAINING_README.md) | [完整指南](docs/prompt_chaining_guide.md)

---

更多示例请查看 [examples](examples/) 目录

## 🛠️ 工具系统

### 基础工具（13个）

| 工具 | 功能 | 示例 |
|------|------|------|
| `get_current_time` | 获取当前时间 | "现在几点？" |
| `calculate` | 数学计算 | "计算 (25 + 10) * 3" |
| `search_wikipedia` | 搜索维基百科 | "搜索Python" |
| `get_random_number` | 生成随机数 | "1到100的随机数" |
| `convert_temperature` | 温度转换 | "25°C 是多少°F？" |
| `string_reverse` | 反转字符串 | "反转 'hello'" |
| `count_words` | 文本统计 | "统计字数" |
| `get_date_info` | 日期信息 | "2025-10-10 是星期几？" |
| `calculate_age` | 计算年龄 | "1990-01-01 出生多大了？" |
| `generate_uuid` | 生成UUID | "生成唯一ID" |
| `encode_base64` | Base64编码 | "编码 'hello'" |
| `decode_base64` | Base64解码 | "解码字符串" |
| `check_prime` | 质数检查 | "17是质数吗？" |

### AI 智能工具（10个）

真正需要大模型参与的高级智能工具：

| 工具 | 功能 | 需要AI的能力 |
|------|------|-------------|
| `web_content_analyzer` | 网页内容分析 | 内容理解、信息提取 |
| `text_quality_analyzer` | 文本质量分析 | 语言评估、问题发现 |
| `creative_idea_generator` | 创意想法生成 | 发散思维、创新性 |
| `code_review_assistant` | 代码审查 | 代码理解、优化建议 |
| `decision_analyzer` | 决策分析 | 多维度分析、利弊权衡 |
| `data_insight_generator` | 数据洞察 | 数据理解、规律发现 |
| `content_improver` | 内容优化 | 内容理解、表达优化 |
| `problem_solver` | 问题解决 | 问题分解、系统思考 |
| `meeting_summarizer` | 会议总结 | 信息提取、结构化 |
| `learning_path_designer` | 学习路径设计 | 知识体系、路径规划 |

详见：[AI工具设计哲学](docs/ai_tools_philosophy.md) | [工具参考文档](docs/tools_reference.md)

## 🤖 可用模型

### 对话模型
- **DeepSeek-V3** ⭐ - 推荐，强大的通用模型
- **Qwen2.5-72B-Instruct** - 强大的中文理解
- **Qwen2.5-14B-Instruct** - 平衡性能和速度
- **GLM-4-Plus** - 智谱 AI 高性能模型
- **GLM-4-Flash** - 快速响应模型

### 嵌入模型（RAG）
- **bge-large-zh-v1.5** ⭐ - 推荐，1024维
- **bge-small-zh-v1.5** - 512维，速度快
- **text-embedding-ada-002** - OpenAI兼容

### 重排序模型（RAG）
- **bge-reranker-base** ⭐ - 推荐
- **bge-reranker-large** - 更高精度

📖 查看 [模型配置指南](docs/model_configuration.md) 了解如何配置

## 📚 文档

- [快速开始](docs/getting_started.md) - 详细的安装配置指南
- [模型配置](docs/model_configuration.md) - 灵活配置不同模型
- [Prompt Chaining 指南](docs/prompt_chaining_guide.md) ⭐ - 提示链完整教程
- [工具参考](docs/tools_reference.md) - 所有工具的详细文档
- [AI工具哲学](docs/ai_tools_philosophy.md) - AI工具设计理念
- [Web 界面](docs/web_interface.md) - Web界面使用说明
- [RAG 指南](docs/rag_guide.md) - RAG系统使用指南
- [API 参考](docs/api_reference.md) - 完整的API文档
- [LangGraph 架构](docs/langgraph_architecture.md) - 架构设计详解
- [最佳实践](docs/best_practices.md) - 开发建议

## 🔧 配置选项

主要配置项（`.env` 文件）：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `GITEE_AI_API_KEY` | API 密钥 | 必填 |
| `GITEE_AI_MODEL` | 主对话模型 | `DeepSeek-V3` |
| `AGENT_MODEL` | Agent专用模型 | 空（使用主模型） |
| `USE_CLOUD_EMBEDDING` | 使用云端嵌入 | `true` |
| `CLOUD_EMBEDDING_MODEL` | 云端嵌入模型 | `bge-large-zh-v1.5` |
| `USE_CLOUD_RERANKER` | 使用云端重排序 | `true` |
| `CLOUD_RERANKER_MODEL` | 云端重排序模型 | `bge-reranker-base` |
| `AGENT_MAX_ITERATIONS` | 最大迭代次数 | `10` |
| `ENABLE_FAILOVER` | 故障转移 | `true` |
| `SSL_VERIFY` | SSL验证 | `false` |

## 🐛 故障排除

### 端口被占用
```bash
# 使用自动启动脚本
python run_web_auto.py  # 自动查找可用端口
```

### SSL 连接错误
在 `.env` 中设置：
```bash
SSL_VERIFY=false
```

### 启动慢
使用云端嵌入服务：
```bash
USE_CLOUD_EMBEDDING=true
```

更多问题请查看 [docs/ssl_troubleshooting.md](docs/ssl_troubleshooting.md)

## 🤝 贡献

欢迎贡献！请查看 [贡献指南](CONTRIBUTING.md)

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent 框架
- [LangChain](https://github.com/langchain-ai/langchain) - LLM 工具库
- [码云 AI](https://ai.gitee.com/) - 模型 API 服务

## 📧 联系方式

- 作者：ShuYixiao
- 邮箱：chinasjh2022@126.com
- 项目地址：[GitHub](https://github.com/your-username/shuyixiao-agent)

---

**⭐ 如果觉得有帮助，请给个 Star！**

🚀 开始你的 AI Agent 之旅吧！
