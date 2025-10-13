# 🚀 快速开始指南

5分钟快速上手 shuyixiao-agent！

## 📋 前置要求

- Python 3.12+
- 码云 AI API Key（[获取地址](https://ai.gitee.com/)）

## ⚡ 三步启动

### 1️⃣ 安装依赖

```bash
# 克隆项目
git clone https://github.com/your-username/shuyixiao-agent.git
cd shuyixiao-agent

# 安装依赖（选择一种方式）
poetry install && poetry shell  # 使用 Poetry（推荐）
# 或
pip install -e .                # 使用 pip
```

### 2️⃣ 配置 API Key

```bash
# 复制配置文件
cp env.example .env

# 编辑 .env 文件，添加你的 API Key
# GITEE_AI_API_KEY=your_api_key_here
```

### 3️⃣ 启动使用

**方式一：Web 界面（推荐）**

```bash
python run_web_auto.py
# 浏览器访问 http://localhost:8000
```

**方式二：运行示例**

```bash
# 简单对话
python examples/01_simple_chat.py

# 工具调用
python examples/02_tool_agent.py

# RAG 检索
python examples/07_rag_basic_usage.py
```

## 💡 快速体验代码

创建 `test.py`：

```python
from src.shuyixiao_agent import SimpleAgent
from dotenv import load_dotenv

load_dotenv()

agent = SimpleAgent()
response = agent.chat("介绍一下 LangGraph")
print(response)
```

运行：
```bash
python test.py
```

## 📚 下一步

- 📖 [完整文档](README.md)
- 🛠️ [工具系统](docs/tools_reference.md)
- 📖 [RAG 指南](docs/rag_guide.md)
- 🎨 [Web 界面](docs/web_interface.md)

## ❓ 常见问题

**Q: 启动很慢？**
```bash
# 在 .env 中添加：
USE_CLOUD_EMBEDDING=true
```

**Q: SSL 错误？**
```bash
# 在 .env 中添加：
SSL_VERIFY=false
```

**Q: 端口被占用？**
```bash
# 使用自动启动脚本
python run_web_auto.py
```

## 🆘 需要帮助？

- 📖 查看 [详细文档](docs/)
- 💬 提交 [Issue](https://github.com/your-username/shuyixiao-agent/issues)
- 📧 联系：chinasjh2022@126.com

---

**祝你使用愉快！🎉**

