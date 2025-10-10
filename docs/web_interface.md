# Web 界面使用指南

## 概述

ShuYixiao Agent 提供了一个现代化的 Web 界面，让您可以通过浏览器与 Agent 进行交互，无需在控制台运行代码。

## 功能特性

- 🎨 **现代化 UI**：美观的渐变设计，流畅的动画效果
- 💬 **实时对话**：支持与 Agent 进行多轮对话
- 🔧 **Agent 切换**：支持简单对话和工具调用两种模式
- 📝 **历史记录**：自动保存对话历史，刷新页面不丢失
- 🧹 **清除历史**：一键清除所有对话记录
- 📱 **响应式设计**：适配各种屏幕尺寸

## 快速开始

### 1. 安装依赖

```bash
# 使用 Poetry
poetry install

# 或使用 pip
pip install -e .
```

### 2. 配置环境变量

创建 `.env` 文件或配置环境变量：

```bash
GITEE_AI_API_KEY=你的API密钥
GITEE_AI_BASE_URL=https://ai.gitee.com/v1
GITEE_AI_MODEL=DeepSeek-V3
```

### 3. 启动服务

```bash
# 使用启动脚本
python run_web.py

# 或直接运行
python -m uvicorn shuyixiao_agent.web_app:app --reload
```

### 4. 访问界面

打开浏览器访问：http://localhost:8000

## 使用说明

### Agent 类型选择

界面提供两种 Agent 类型：

1. **简单对话 (Simple Agent)**
   - 基础的对话功能
   - 适合一般的问答场景
   - 响应速度快

2. **工具调用 (Tool Agent)**
   - 支持调用工具完成任务
   - 可以执行计算、获取时间等操作
   - 功能更强大

### 发送消息

1. 在输入框中输入您的问题
2. 点击"发送"按钮或按 Enter 键发送（Shift + Enter 换行）
3. 等待 Agent 回复

### 清除历史

点击顶部的"清除历史"按钮可以删除所有对话记录，重新开始对话。

## API 接口

Web 界面基于 FastAPI 构建，提供以下 REST API 接口：

### 1. 发送消息

```http
POST /api/chat
Content-Type: application/json

{
    "message": "你好",
    "agent_type": "simple",
    "session_id": "default"
}
```

**响应：**

```json
{
    "response": "你好！有什么可以帮助你的吗？",
    "agent_type": "simple",
    "session_id": "default"
}
```

### 2. 获取历史记录

```http
GET /api/history/{session_id}
```

**响应：**

```json
{
    "session_id": "default",
    "messages": [
        {
            "role": "user",
            "content": "你好"
        },
        {
            "role": "assistant",
            "content": "你好！有什么可以帮助你的吗？"
        }
    ]
}
```

### 3. 清除历史

```http
DELETE /api/history/{session_id}
```

### 4. 健康检查

```http
GET /api/health
```

**响应：**

```json
{
    "status": "healthy",
    "api_key_configured": true,
    "model": "DeepSeek-V3"
}
```

## 自定义配置

### 修改端口

编辑 `run_web.py` 文件，修改 `port` 参数：

```python
uvicorn.run(
    "shuyixiao_agent.web_app:app",
    host="0.0.0.0",
    port=8000,  # 修改为其他端口
    reload=True
)
```

### 修改系统提示词

在 `src/shuyixiao_agent/web_app.py` 中的 `get_agent` 函数里修改默认的 `system_message`。

### 添加新工具

如果使用 Tool Agent，可以在 `src/shuyixiao_agent/tools/basic_tools.py` 中添加新的工具函数。

## 故障排除

### 1. 无法连接到服务器

- 确保后端服务已启动
- 检查端口 8000 是否被占用
- 查看控制台错误信息

### 2. API 请求失败

- 检查 `.env` 文件中的 API Key 是否正确
- 确认网络连接正常
- 查看 API 返回的错误信息

### 3. 页面无法加载

- 清除浏览器缓存
- 尝试使用其他浏览器
- 检查 static/index.html 文件是否存在

## 开发和调试

### 启用调试模式

FastAPI 提供了自动重载功能，修改代码后会自动重启服务。

### 查看 API 文档

访问 http://localhost:8000/docs 查看自动生成的 API 文档（Swagger UI）。

### 查看日志

控制台会显示所有请求和响应的日志信息，方便调试。

## 生产部署

### 使用 Gunicorn

```bash
pip install gunicorn
gunicorn shuyixiao_agent.web_app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 使用 Docker

创建 `Dockerfile`：

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 8000

CMD ["python", "run_web.py"]
```

构建和运行：

```bash
docker build -t shuyixiao-agent .
docker run -p 8000:8000 --env-file .env shuyixiao-agent
```

## 安全建议

1. **生产环境**：不要在生产环境中使用 `reload=True`
2. **API Key**：不要将 API Key 提交到版本控制系统
3. **HTTPS**：生产环境建议使用 HTTPS
4. **认证**：考虑添加用户认证机制
5. **限流**：添加请求限流保护

## 后续计划

- [ ] 支持流式响应（实时输出）
- [ ] 添加用户认证
- [ ] 支持多会话管理
- [ ] 添加对话导出功能
- [ ] 支持自定义主题
- [ ] 添加语音输入/输出
- [ ] 支持多语言界面

## 反馈与贡献

如有问题或建议，欢迎提交 Issue 或 Pull Request！

