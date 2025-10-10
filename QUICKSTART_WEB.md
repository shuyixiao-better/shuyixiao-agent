# Web 界面快速开始指南

## 🎯 5 分钟快速启动

### 第 1 步：安装依赖

```bash
# 确保已安装 Python 3.12+
python --version

# 安装依赖（使用 pip）
pip install -e .

# 或使用 Poetry
poetry install
```

### 第 2 步：配置 API Key

创建 `.env` 文件（或复制 `.env.example`）：

```bash
GITEE_AI_API_KEY=你的API密钥
GITEE_AI_BASE_URL=https://ai.gitee.com/v1
GITEE_AI_MODEL=DeepSeek-V3
```

**获取 API Key：**
1. 访问 https://ai.gitee.com/
2. 登录后进入 "工作台 -> 设置 -> 访问令牌"
3. 创建新令牌并购买模型资源包

### 第 3 步：启动服务

```bash
python run_web.py
```

看到以下输出表示启动成功：

```
============================================================
🚀 启动 ShuYixiao Agent Web 界面
============================================================

📍 服务地址: http://localhost:8000
📖 API 文档: http://localhost:8000/docs

按 Ctrl+C 停止服务
============================================================
```

### 第 4 步：打开浏览器

在浏览器中访问：**http://localhost:8000**

## 🎨 界面功能

### 1. 选择 Agent 类型

- **简单对话**：适合一般问答
- **工具调用**：支持计算、获取时间等功能

### 2. 开始对话

在底部输入框输入问题，点击"发送"或按 Enter 键。

### 3. 测试示例

#### 简单对话模式：
- "你好！"
- "介绍一下 Python 的特点"
- "帮我写一个快速排序算法"

#### 工具调用模式：
- "现在几点了？"
- "计算 123 * 456"
- "帮我查一下维基百科关于 Python 的信息"

### 4. 清除历史

点击顶部的"清除历史"按钮可以重新开始对话。

## 📱 界面截图说明

```
┌─────────────────────────────────────────────┐
│  🤖 ShuYixiao Agent            在线 ●       │  ← 标题栏
├─────────────────────────────────────────────┤
│ Agent类型: [简单对话 ▼] [清除历史]         │  ← 控制栏
├─────────────────────────────────────────────┤
│                                             │
│  用户: 你好！                                │  ← 对话区
│       助手: 你好！有什么可以帮助你的吗？      │
│                                             │
│                                             │
├─────────────────────────────────────────────┤
│ [输入您的问题...              ] [发送]       │  ← 输入区
└─────────────────────────────────────────────┘
```

## 🔧 常见问题

### Q1: 端口被占用怎么办？

编辑 `run_web.py`，修改端口号：

```python
uvicorn.run(
    "shuyixiao_agent.web_app:app",
    host="0.0.0.0",
    port=8888,  # 改成其他端口
    reload=True
)
```

### Q2: 显示 "API 请求失败"

检查：
1. `.env` 文件中的 API Key 是否正确
2. 是否有网络连接
3. 码云 AI 账户是否有余额

### Q3: 页面无法加载

1. 确认服务已启动（查看控制台）
2. 检查浏览器地址是否正确
3. 清除浏览器缓存后重试

### Q4: 工具调用不工作

确保选择了"工具调用"模式，而不是"简单对话"模式。

## 📚 进阶使用

### 查看 API 文档

访问 http://localhost:8000/docs 查看完整的 API 接口文档。

### 使用 API 接口

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "你好",
        "agent_type": "simple",
        "session_id": "my_session"
    }
)

print(response.json())
```

### 添加自定义工具

编辑 `src/shuyixiao_agent/tools/basic_tools.py`，添加新函数：

```python
def my_custom_tool(param: str) -> str:
    """你的工具描述"""
    return f"处理结果: {param}"
```

然后在 `get_basic_tools()` 函数中注册。

## 🚀 下一步

- 查看 [完整文档](docs/web_interface.md)
- 阅读 [API 参考](docs/api_reference.md)
- 探索 [示例代码](examples/)
- 了解 [LangGraph 架构](docs/langgraph_architecture.md)

## 💡 提示

- 使用 **Shift + Enter** 在输入框中换行
- 对话历史会自动保存，刷新页面不会丢失
- 可以随时切换 Agent 类型
- 支持多轮对话，Agent 会记住上下文

---

**享受与 AI Agent 的对话吧！** 🎉

