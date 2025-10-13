# shuyixiao-agent

基于 LangGraph 和码云 AI 的智能 Agent 项目

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📖 简介

`shuyixiao-agent` 是一个基于现代 AI Agent 框架 [LangGraph](https://github.com/langchain-ai/langgraph) 和[码云 AI](https://ai.gitee.com/) 的智能 Agent 项目。本项目提供清晰的代码结构、详细的文档和丰富的示例，适合学习和参考。

### ✨ 特性

- 🚀 **基于 LangGraph**：使用业界主流的 Agent 框架
- 🤖 **码云 AI 集成**：接入码云 AI Serverless API，支持多种模型
- ⚙️ **灵活模型配置**：支持为不同任务配置不同模型，云端/本地自由切换
- 📖 **RAG 系统**：完整的检索增强生成系统，支持知识库问答
  - 多模态检索（向量、关键词、混合）
  - 智能查询优化（重写、修订、子问题扩展）
  - 重排序机制提升召回质量
  - 智能上下文管理和片段扩展
  - 多轮对话支持
  - SSE 流式响应
- 🛠️ **工具调用**：支持 Agent 调用自定义工具完成复杂任务
- 🧠 **AI驱动工具**：10个真正需要大模型参与的智能工具（代码审查、创意生成、决策分析等）
- 🔧 **基础工具集**：13个演示用基础工具（时间、计算、编码等）
- 🎨 **Web 界面**：提供现代化的 Web 交互界面，支持 RAG 知识库管理
- 📚 **详细文档**：完整的 API 文档和使用指南，包含 RAG 使用指南
- 💡 **丰富示例**：多个实用示例帮助快速上手
- ⚡ **故障转移**：支持自动故障转移，确保服务稳定性
- 🎯 **类型安全**：使用 Pydantic 进行配置管理

### 🎯 技术栈

- **Agent 框架**：LangGraph、LangChain
- **AI 模型**：码云 AI（DeepSeek-V3 等）
- **RAG 组件**：
  - 向量数据库：ChromaDB
  - 嵌入模型：Sentence Transformers (BGE)
  - 文本分割：LangChain Text Splitters
  - 关键词检索：BM25、Jieba 分词
  - 重排序：Cross-Encoder
  - Token 计数：tiktoken
- **编程语言**：Python 3.12+
- **Web 框架**：FastAPI、Uvicorn
- **包管理**：Poetry
- **配置管理**：Pydantic Settings
- **HTTP 客户端**：Requests

## 🚀 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/your-username/shuyixiao-agent.git
cd shuyixiao-agent

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

### 2. 配置

```bash
# 复制环境变量示例文件
cp env_config_example.txt .env

# 编辑 .env 文件，填入你的码云 AI API Key
# GITEE_AI_API_KEY=your_api_key_here
```

**获取 API Key：**
1. 访问 [码云 AI 平台](https://ai.gitee.com/)
2. 前往 **工作台 -> 设置 -> 访问令牌**
3. 创建新的访问令牌
4. 购买模型资源包

**配置模型（可选）：**

所有模型都可以通过 `.env` 文件灵活配置。查看 [模型配置文档](docs/model_configuration.md) 了解详情。

```bash
# 主对话模型（默认：DeepSeek-V3）
GITEE_AI_MODEL=DeepSeek-V3

# Agent 专用模型（留空则使用主对话模型）
AGENT_MODEL=GLM-4-Flash

# 查询优化模型（留空则使用主对话模型）
QUERY_OPTIMIZER_MODEL=Qwen2.5-14B-Instruct

# RAG 嵌入模型（推荐使用云端）
USE_CLOUD_EMBEDDING=true
CLOUD_EMBEDDING_MODEL=bge-large-zh-v1.5

# RAG 重排序模型（推荐使用云端）
USE_CLOUD_RERANKER=true
CLOUD_RERANKER_MODEL=bge-reranker-base
```

💡 **提示**：运行 `python test_model_config.py` 验证配置是否正确

### 3. 启动 Web 界面（推荐）

#### 方式 1：自动启动（推荐）⭐

使用自动化启动脚本，会自动检测并使用可用端口：

```bash
# 激活虚拟环境（如果使用）
.venv\Scripts\Activate.ps1  # Windows PowerShell
# 或 source .venv/bin/activate  # Linux/Mac

# 启动 Web 服务（自动查找可用端口）
python run_web_auto.py

# 服务启动后，浏览器访问显示的地址
# 例如：http://localhost:8001
```

#### 方式 2：标准启动

```bash
# 启动 Web 服务
python run_web.py

# 在浏览器中打开
# http://localhost:8000
```

#### 方式 3：修复版启动（遇到问题时使用）

```bash
# 带诊断功能的启动脚本
python run_web_fixed.py

# 会自动检查：
# - 依赖包是否完整
# - 端口是否被占用
# - 配置是否正确
```

Web 界面提供了友好的聊天界面，支持：
- ✅ **流式输出**：AI 回复实时逐字显示，无需等待
- ✅ **Markdown 渲染**：支持代码高亮、表格、列表等完整 Markdown 语法
- ✅ **Agent 类型切换**：简单对话/工具调用模式
- ✅ **对话历史**：自动保存，刷新不丢失
- ✅ **一键清除**：清空所有对话历史
- ✅ **现代化 UI**：美观的渐变设计，流畅动画
- ✅ **打字指示器**：显示 AI 正在思考的状态

#### 🔧 诊断工具

如果启动遇到问题，可以使用诊断脚本：

```bash
# 运行完整诊断
python diagnose_web_issue.py

# 检查内容：
# ✓ Python 版本
# ✓ 虚拟环境状态
# ✓ 依赖包完整性
# ✓ 项目结构
# ✓ 环境配置
# ✓ 端口占用情况
# ✓ 应用导入测试
```

### 4. 或运行命令行示例

```bash
# 简单对话示例
python examples/01_simple_chat.py

# 带工具的 Agent
python examples/02_tool_agent.py

# 自定义工具
python examples/03_custom_tool.py

# API 客户端
python examples/04_api_client.py

# 完整工具集演示（推荐）
python examples/05_all_tools_demo.py

# RAG 示例
python examples/07_rag_basic_usage.py      # RAG 基础使用
python examples/08_rag_file_upload.py      # 文件上传到知识库
python examples/09_rag_streaming.py        # 流式响应
```

### 5. 快速体验（代码）

```python
from src.shuyixiao_agent import SimpleAgent
from dotenv import load_dotenv

load_dotenv()

# 创建 Agent
agent = SimpleAgent()

# 开始对话
response = agent.chat("你好！请介绍一下 LangGraph。")
print(response)
```

## 📂 项目结构

```
shuyixiao-agent/
├── src/
│   └── shuyixiao_agent/          # 主要代码
│       ├── __init__.py
│       ├── config.py              # 配置管理
│       ├── gitee_ai_client.py    # 码云 AI 客户端
│       ├── web_app.py             # Web 应用服务
│       ├── static/                # 前端静态文件
│       │   └── index.html        # Web 界面
│       ├── agents/                # Agent 实现
│       │   ├── simple_agent.py   # 简单对话 Agent
│       │   └── tool_agent.py     # 工具调用 Agent
│       ├── tools/                 # 工具集合
│       │   ├── __init__.py
│       │   └── basic_tools.py    # 基础工具
│       └── rag/                   # RAG 模块
│           ├── __init__.py
│           ├── embeddings.py      # 嵌入模型管理
│           ├── vector_store.py    # 向量存储
│           ├── document_loader.py # 文档加载
│           ├── retrievers.py      # 检索器
│           ├── query_optimizer.py # 查询优化
│           ├── reranker.py        # 重排序
│           ├── context_manager.py # 上下文管理
│           └── rag_agent.py       # RAG Agent
├── examples/                      # 示例代码
│   ├── 01_simple_chat.py
│   ├── 02_tool_agent.py
│   ├── 03_custom_tool.py
│   ├── 04_api_client.py
│   ├── 07_rag_basic_usage.py      # RAG 基础使用
│   ├── 08_rag_file_upload.py      # RAG 文件上传
│   ├── 09_rag_streaming.py        # RAG 流式响应
│   └── README.md
├── docs/                          # 文档
│   ├── getting_started.md        # 快速开始
│   ├── api_reference.md          # API 参考
│   ├── langgraph_architecture.md # LangGraph 架构
│   ├── best_practices.md         # 最佳实践
│   ├── model_configuration.md    # 模型配置指南 ⭐ 新增
│   ├── web_interface.md          # Web 界面使用指南
│   └── rag_guide.md              # RAG 使用指南
├── data/                          # 数据目录（自动创建）
│   └── chroma/                    # 向量数据库
├── run_web.py                     # Web 服务启动脚本（标准版）
├── run_web_auto.py                # Web 服务启动脚本（自动化版）⭐
├── run_web_fixed.py               # Web 服务启动脚本（修复版）
├── run_web_optimized.py           # Web 服务启动脚本（优化版）
├── diagnose_web_issue.py          # Web 服务器诊断工具
├── test_server.py                 # 服务器连接测试脚本
├── .env.example                   # 环境变量示例
├── pyproject.toml                 # 项目配置
└── README.md                      # 本文件
```

## 🎓 使用示例

### 简单对话

```python
from src.shuyixiao_agent import SimpleAgent

agent = SimpleAgent(
    system_message="你是一个友好的AI助手"
)

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
    agent.register_tool(
        name=tool["name"],
        func=tool["func"],
        description=tool["description"],
        parameters=tool["parameters"]
    )

# 使用工具
response = agent.run("现在几点了？帮我计算一下 25 * 4 + 10")
print(response)
```

### RAG (检索增强生成)

```python
from src.shuyixiao_agent import RAGAgent

# 创建 RAG Agent
agent = RAGAgent(
    collection_name="my_knowledge_base",
    use_reranker=True,
    retrieval_mode="hybrid"
)

# 添加知识库文档
texts = [
    "Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年首次发布。",
    "LangChain 是一个用于开发由语言模型驱动的应用程序的框架。",
    "RAG（检索增强生成）结合了信息检索和文本生成的技术。"
]
agent.add_texts(texts)

# 查询知识库
answer = agent.query(
    question="什么是 RAG？",
    top_k=3,
    optimize_query=True
)
print(answer)

# 流式响应
stream = agent.query(question="Python 的特点是什么？", stream=True)
for chunk in stream:
    print(chunk, end="", flush=True)
```

更多 RAG 功能：
- 📄 从文件/目录批量加载文档
- 🔍 多模态检索（向量、关键词、混合）
- 🎯 智能查询优化和重写
- 🔄 重排序提升质量
- 💬 多轮对话支持
- ⚡ 流式实时响应

详见：[RAG 使用指南](docs/rag_guide.md)

#### 🤖 AI驱动的智能工具（推荐）

**真正需要大模型参与的高级工具，而不是简单的硬编码逻辑！**

项目内置了10个AI驱动的智能工具：

| 工具名称 | 功能描述 | 需要AI的能力 | 使用示例 |
|---------|---------|------------|---------|
| `web_content_analyzer` | 智能网页内容分析 | 内容理解、信息提取、摘要生成 | "分析这篇文章的要点" |
| `text_quality_analyzer` | 文本质量分析 | 语言评估、问题发现、改进建议 | "分析这段文案的质量" |
| `creative_idea_generator` | 创意想法生成 | 发散思维、创新性、可行性评估 | "为咖啡店想3个创意" |
| `code_review_assistant` | 代码智能审查 | 代码理解、问题发现、优化建议 | "审查这段代码" |
| `decision_analyzer` | 决策智能分析 | 多维度分析、利弊权衡、理性建议 | "帮我分析职业选择" |
| `data_insight_generator` | 数据洞察生成 | 数据理解、规律发现、价值洞察 | "分析这份销售数据" |
| `content_improver` | 内容智能优化 | 内容理解、表达优化、风格转换 | "改成专业商务风格" |
| `problem_solver` | 智能问题解决 | 问题分解、系统性思考、方案设计 | "如何提升团队效率" |
| `meeting_summarizer` | 会议智能总结 | 信息提取、结构化呈现、任务识别 | "总结这次会议" |
| `learning_path_designer` | 学习路径设计 | 知识体系、路径规划、资源推荐 | "设计机器学习路径" |

**使用示例：**
```python
from src.shuyixiao_agent.tools import get_ai_powered_tools

# 注册所有AI智能工具
for tool in get_ai_powered_tools():
    agent.register_tool(**tool)

# 使用示例
agent.run("帮我审查这段代码的质量和安全性")
agent.run("为在线教育平台生成5个创新功能创意")
agent.run("分析这个技术决策的优劣")
```

📖 **详细了解：** [AI工具设计哲学](docs/ai_tools_philosophy.md)

---

#### 🔧 基础工具（简单逻辑）

项目也包含13个基础工具用于演示（但这些工具不需要AI参与）：

| 工具名称 | 功能描述 | 使用示例 |
|---------|---------|---------|
| `get_current_time` | 获取当前日期和时间 | "现在几点了？" |
| `calculate` | 计算数学表达式 | "计算 (25 + 10) * 3" |
| `search_wikipedia` | 搜索维基百科 | "搜索Python编程语言" |
| `get_random_number` | 生成随机数 | "生成1到100之间的随机数" |
| `convert_temperature` | 温度单位转换 | "25摄氏度等于多少华氏度？" |
| `string_reverse` | 反转字符串 | "反转字符串 'hello'" |
| `count_words` | 统计文本信息 | "统计这段文本的字数" |
| `get_date_info` | 获取日期详细信息 | "2025-10-10是星期几？" |
| `calculate_age` | 计算年龄 | "1990-01-01出生的人多大了？" |
| `generate_uuid` | 生成UUID | "生成一个唯一ID" |
| `encode_base64` | Base64编码 | "对'hello'进行base64编码" |
| `decode_base64` | Base64解码 | "解码这个base64字符串" |
| `check_prime` | 检查质数 | "17是质数吗？" |

### 自定义工具

```python
from src.shuyixiao_agent.agents.tool_agent import ToolAgent

# 定义工具函数
def get_weather(city: str) -> str:
    return f"{city}的天气：晴天，25°C"

agent = ToolAgent()

# 注册自定义工具
agent.register_tool(
    name="get_weather",
    func=get_weather,
    description="查询城市天气",
    parameters={
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名称"}
        },
        "required": ["city"]
    }
)

response = agent.run("北京今天天气怎么样？")
print(response)
```

## 🌐 Web 界面详细说明

### 核心功能

#### 1. 流式输出
- AI 回复实时逐字显示，无需等待完整生成
- 显示打字指示器动画
- 大幅提升用户体验

#### 2. Markdown 渲染
支持完整的 Markdown 语法：
- **代码块**：深色主题，语法高亮
- **行内代码**：`代码` 样式
- **表格**：清晰的边框和表头
- **列表**：有序/无序列表
- **标题**：H1-H6 层级
- **引用**：左侧紫色边框
- **链接和图片**：完整支持

#### 3. Agent 类型
- **简单对话**：基础问答，支持流式输出
- **工具调用**：可调用时间、计算、搜索等工具

#### 4. 对话历史
- 自动保存到服务器
- 刷新页面不丢失
- 一键清空所有历史

### 使用示例

**测试流式输出：**
```
问：用 Python 写一个冒泡排序算法
答：[实时逐字显示，带代码高亮]
```

**测试工具调用：**
```
切换到"工具调用"模式

问：现在几点了？
答：当前时间是 2025-10-10 10:30:00

问：帮我计算 123 * 456
答：56,088

问：生成一个1到1000之间的随机数
答：生成的随机数是 742

问：25摄氏度等于多少华氏度？
答：25°C = 77°F

问：反转字符串 "hello world"
答：dlrow olleh

问：2025-10-10是星期几？
答：2025-10-10是周五

问：1990-01-01出生的人现在多大了？
答：35岁

问：生成一个UUID
答：生成的UUID是 550e8400-e29b-41d4-a716-446655440000

问：对"Hello"进行base64编码
答：SGVsbG8=

问：97是质数吗？
答：97是质数，没有找到除1和自身外的因数
```

**测试 Markdown：**
```
问：用表格对比 Python 和 Java 的特点
答：[显示格式化的表格]
```

### API 接口

Web 服务提供以下 API：

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat/stream` | POST | 流式聊天接口 |
| `/api/chat` | POST | 普通聊天接口 |
| `/api/history/{session_id}` | GET | 获取历史记录 |
| `/api/history/{session_id}` | DELETE | 清除历史记录 |
| `/api/health` | GET | 健康检查 |

完整 API 文档：http://localhost:8000/docs

### 故障排除

#### 常见启动问题

**问题 1：浏览器无法访问 localhost:8000** ❌

**原因：** 端口被占用或依赖缺失

**解决方案：**
```bash
# 方案 A：使用自动化启动脚本（推荐）
python run_web_auto.py
# 会自动查找可用端口（8001, 8002...）

# 方案 B：运行诊断工具
python diagnose_web_issue.py
# 会检查所有问题并给出建议

# 方案 C：手动清理端口
netstat -ano | findstr :8000  # 查找占用进程
taskkill /PID <PID> /F         # 结束进程
```

**问题 2：缺少依赖包** ❌

**症状：** `ModuleNotFoundError: No module named 'xxx'`

**解决方案：**
```bash
# 激活虚拟环境
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/Mac

# 安装依赖
pip install -r requirements.txt
# 或使用 Poetry
poetry install
```

**问题 3：API Key 未配置** ⚠️

**症状：** 启动日志显示 `API Key 已配置: False`

**解决方案：**
```bash
# 1. 复制环境变量示例文件
cp env.example .env

# 2. 编辑 .env 文件，添加：
# GITEE_AI_API_KEY=你的API密钥

# 3. 获取 API Key
# https://ai.gitee.com/dashboard/settings/tokens
```

**问题 4：流式输出不工作**
- 确保已重启服务
- 清除浏览器缓存（Ctrl+F5）
- 检查控制台错误（F12）

**问题 5：工具调用失败**
- 确保选择了"工具调用"模式
- 查看后端日志
- 验证工具函数是否正确注册

**问题 6：Markdown 不渲染**
- 强制刷新浏览器（Ctrl+F5）
- 检查 marked.js 和 DOMPurify 库是否加载
- 在控制台输入 `typeof marked` 检查

#### 🛠️ 诊断工具说明

项目提供了三个诊断和启动工具：

| 工具 | 用途 | 特点 |
|------|------|------|
| `run_web_auto.py` | 自动化启动 | ⭐ **推荐**，自动查找可用端口，无需交互 |
| `run_web_fixed.py` | 修复版启动 | 带完整诊断，交互式选择端口 |
| `diagnose_web_issue.py` | 诊断工具 | 全面检查系统状态，给出修复建议 |

**使用场景：**
- **首次启动**：使用 `run_web_auto.py`
- **遇到问题**：先运行 `diagnose_web_issue.py`，再用 `run_web_fixed.py`
- **日常使用**：使用 `run_web_auto.py` 或 `run_web.py`

## 📚 文档

- [快速开始](docs/getting_started.md) - 详细的安装和配置指南
- [模型配置指南](docs/model_configuration.md) - ⭐ **灵活配置不同任务使用不同模型**
- [工具参考](docs/tools_reference.md) - 所有13个内置工具的详细文档
- [Web 界面使用指南](docs/web_interface.md) - Web 界面使用说明
- [RAG 使用指南](docs/rag_guide.md) - 检索增强生成系统使用指南
- [API 参考](docs/api_reference.md) - 完整的 API 文档
- [LangGraph 架构](docs/langgraph_architecture.md) - 深入了解架构设计
- [示例代码](examples/README.md) - 查看所有示例

## 🔧 配置选项

主要配置项（在 `.env` 文件中设置）：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `GITEE_AI_API_KEY` | 码云 AI API Key | 必填 |
| `GITEE_AI_MODEL` | 主对话模型 | `DeepSeek-V3` |
| `AGENT_MODEL` | Agent 专用模型（可选） | 空（使用主模型） |
| `QUERY_OPTIMIZER_MODEL` | 查询优化模型（可选） | 空（使用主模型） |
| `USE_CLOUD_EMBEDDING` | 使用云端嵌入服务 | `true` |
| `CLOUD_EMBEDDING_MODEL` | 云端嵌入模型 | `bge-large-zh-v1.5` |
| `USE_CLOUD_RERANKER` | 使用云端重排序服务 | `true` |
| `CLOUD_RERANKER_MODEL` | 云端重排序模型 | `bge-reranker-base` |
| `AGENT_MAX_ITERATIONS` | Agent 最大迭代次数 | `10` |
| `ENABLE_FAILOVER` | 是否启用故障转移 | `true` |
| `REQUEST_TIMEOUT` | 请求超时时间（秒） | `60` |

💡 **更多配置选项**：查看 [模型配置指南](docs/model_configuration.md) 了解如何为不同任务配置不同模型

## 🤝 可用模型

码云 AI 支持多种模型，包括：

### 对话模型（用于 Agent、对话、查询优化）
- **DeepSeek-V3** - ⭐ 推荐，强大的通用模型
- **Qwen2.5-72B-Instruct** - 强大的中文理解
- **Qwen2.5-14B-Instruct** - 平衡性能和速度
- **GLM-4-Plus** - 智谱 AI 高性能模型
- **GLM-4-Flash** - 快速响应模型

### 向量化模型（用于 RAG 嵌入）
- **bge-large-zh-v1.5** - ⭐ 推荐，1024 维
- **bge-small-zh-v1.5** - 512 维，速度快
- **text-embedding-ada-002** - OpenAI 兼容

### 重排序模型（用于 RAG 重排序）
- **bge-reranker-base** - ⭐ 推荐
- **bge-reranker-large** - 更高精度

📖 **完整模型列表和配置方法**：
- [Gitee AI 模型文档](https://ai.gitee.com/docs/products/apis)
- [本项目模型配置指南](docs/model_configuration.md)

## 📋 TODO

- [x] Web 交互界面
- [x] 流式输出支持
- [x] Markdown 渲染
- [x] 对话历史管理
- [x] 添加更多内置工具（13个工具）
- [ ] 实现会话记忆功能
- [ ] 支持多模态（图像、语音）
- [ ] 添加测试用例
- [ ] 性能优化
- [ ] 用户认证功能
- [ ] 代码复制功能
- [ ] 对话导出功能

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) - 优秀的 Agent 框架
- [LangChain](https://github.com/langchain-ai/langchain) - 强大的 LLM 工具库
- [码云 AI](https://ai.gitee.com/) - 提供模型 API 服务

## 📧 联系方式

- 作者：ShuYixiao
- 邮箱：chinasjh2022@126.com
- 项目地址：[GitHub](https://github.com/your-username/shuyixiao-agent)

## ⭐ 如果觉得有帮助，请给个 Star！

---

**开始你的 AI Agent 之旅吧！** 🚀