# shuyixiao-agent

基于 LangGraph 和码云 AI 的智能 Agent 项目

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📖 简介

`shuyixiao-agent` 是一个基于现代 AI Agent 框架 [LangGraph](https://github.com/langchain-ai/langgraph) 和[码云 AI](https://ai.gitee.com/) 的智能 Agent 项目。本项目提供清晰的代码结构、详细的文档和丰富的示例，适合学习和参考。

### ✨ 特性

- 🚀 **基于 LangGraph**：使用业界主流的 Agent 框架
- 🤖 **码云 AI 集成**：接入码云 AI Serverless API，支持多种模型
- 🛠️ **工具调用**：支持 Agent 调用自定义工具完成复杂任务
- 🎨 **Web 界面**：提供现代化的 Web 交互界面，无需在控制台调试
- 📚 **详细文档**：完整的 API 文档和使用指南
- 💡 **丰富示例**：多个实用示例帮助快速上手
- ⚡ **故障转移**：支持自动故障转移，确保服务稳定性
- 🎯 **类型安全**：使用 Pydantic 进行配置管理

### 🎯 技术栈

- **Agent 框架**：LangGraph、LangChain
- **AI 模型**：码云 AI（DeepSeek-V3 等）
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
cp .env.example .env

# 编辑 .env 文件，填入你的码云 AI API Key
# GITEE_AI_API_KEY=your_api_key_here
```

**获取 API Key：**
1. 访问 [码云 AI 平台](https://ai.gitee.com/)
2. 前往 **工作台 -> 设置 -> 访问令牌**
3. 创建新的访问令牌
4. 购买模型资源包

### 3. 启动 Web 界面（推荐）

```bash
# 启动 Web 服务
python run_web.py

# 在浏览器中打开
# http://localhost:8000
```

Web 界面提供了友好的聊天界面，支持：
- ✅ **流式输出**：AI 回复实时逐字显示，无需等待
- ✅ **Markdown 渲染**：支持代码高亮、表格、列表等完整 Markdown 语法
- ✅ **Agent 类型切换**：简单对话/工具调用模式
- ✅ **对话历史**：自动保存，刷新不丢失
- ✅ **一键清除**：清空所有对话历史
- ✅ **现代化 UI**：美观的渐变设计，流畅动画
- ✅ **打字指示器**：显示 AI 正在思考的状态

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
│       └── tools/                 # 工具集合
│           ├── __init__.py
│           └── basic_tools.py    # 基础工具
├── examples/                      # 示例代码
│   ├── 01_simple_chat.py
│   ├── 02_tool_agent.py
│   ├── 03_custom_tool.py
│   ├── 04_api_client.py
│   └── README.md
├── docs/                          # 文档
│   ├── getting_started.md        # 快速开始
│   ├── api_reference.md          # API 参考
│   ├── langgraph_architecture.md # LangGraph 架构
│   ├── best_practices.md         # 最佳实践
│   └── web_interface.md          # Web 界面使用指南
├── run_web.py                     # Web 服务启动脚本
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
from src.shuyixiao_agent.tools import get_current_time, calculate

agent = ToolAgent()

# 注册工具
agent.register_tool(
    name="get_current_time",
    func=get_current_time,
    description="获取当前时间",
    parameters={"type": "object", "properties": {}}
)

# 使用工具
response = agent.run("现在几点了？")
print(response)
```

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

**问题：流式输出不工作**
- 确保已重启服务
- 清除浏览器缓存（Ctrl+F5）
- 检查控制台错误（F12）

**问题：工具调用失败**
- 确保选择了"工具调用"模式
- 查看后端日志
- 验证工具函数是否正确注册

**问题：Markdown 不渲染**
- 强制刷新浏览器（Ctrl+F5）
- 检查 marked.js 和 DOMPurify 库是否加载
- 在控制台输入 `typeof marked` 检查

## 📚 文档

- [快速开始](docs/getting_started.md) - 详细的安装和配置指南
- [Web 界面使用指南](docs/web_interface.md) - Web 界面使用说明
- [API 参考](docs/api_reference.md) - 完整的 API 文档
- [LangGraph 架构](docs/langgraph_architecture.md) - 深入了解架构设计
- [示例代码](examples/README.md) - 查看所有示例

## 🔧 配置选项

主要配置项（在 `.env` 文件中设置）：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `GITEE_AI_API_KEY` | 码云 AI API Key | 必填 |
| `GITEE_AI_MODEL` | 使用的模型 | `Qwen/Qwen2.5-7B-Instruct` |
| `AGENT_MAX_ITERATIONS` | Agent 最大迭代次数 | `10` |
| `ENABLE_FAILOVER` | 是否启用故障转移 | `true` |
| `REQUEST_TIMEOUT` | 请求超时时间（秒） | `60` |

## 🤝 可用模型

码云 AI 支持多种模型，包括：

- **Qwen/Qwen2.5-7B-Instruct** - 通用对话（推荐入门）
- **Qwen/Qwen2.5-14B-Instruct** - 更强性能
- **Qwen/Qwen2.5-72B-Instruct** - 最强性能
- 更多模型见 [码云 AI 模型广场](https://ai.gitee.com/serverless)

## 📋 TODO

- [x] Web 交互界面
- [x] 流式输出支持
- [x] Markdown 渲染
- [x] 对话历史管理
- [ ] 实现会话记忆功能
- [ ] 添加更多内置工具
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