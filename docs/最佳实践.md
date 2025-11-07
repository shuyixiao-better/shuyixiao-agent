# 最佳实践

本文档介绍使用 shuyixiao-agent 的最佳实践和建议。

## 目录

- [Agent 设计](#agent-设计)
- [工具开发](#工具开发)
- [错误处理](#错误处理)
- [性能优化](#性能优化)
- [安全性](#安全性)
- [测试](#测试)
- [部署](#部署)

---

## Agent 设计

### 1. 选择合适的 Agent 类型

**SimpleAgent 适用于：**
- 简单的问答场景
- 不需要工具调用的对话
- 快速原型验证

**ToolAgent 适用于：**
- 需要查询外部数据
- 需要执行计算或操作
- 复杂的多步骤任务

### 2. 编写清晰的 System Message

好的 system message 能显著提升 Agent 表现：

```python
# ❌ 不好的例子
system_message = "你是助手"

# ✅ 好的例子
system_message = """你是一个专业的Python编程助手。
你的职责是：
1. 回答Python相关的技术问题
2. 提供清晰的代码示例
3. 解释编程概念
4. 推荐最佳实践

请保持回答简洁、准确、友好。"""
```

### 3. 限制迭代次数

防止无限循环：

```python
agent = ToolAgent(
    max_iterations=10  # 根据实际需求调整
)
```

### 4. 状态管理

对于复杂应用，考虑添加自定义状态字段：

```python
class CustomAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_context: Dict[str, Any]  # 用户上下文
    session_id: str  # 会话 ID
    step_count: int  # 步骤计数
```

---

## 工具开发

### 1. 工具设计原则

**单一职责：** 每个工具只做一件事

```python
# ✅ 好的设计
def get_current_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_date() -> str:
    """获取当前日期"""
    return datetime.now().strftime("%Y-%m-%d")

# ❌ 不好的设计
def get_time_and_weather(city: str) -> Dict:
    """同时获取时间和天气（职责太多）"""
    return {
        "time": "...",
        "weather": "..."
    }
```

### 2. 提供详细的描述

AI 需要清晰的描述来决定何时使用工具：

```python
agent.register_tool(
    name="calculate",
    func=calculate,
    description="""计算数学表达式的值。
    
    支持的运算：
    - 加法 (+)
    - 减法 (-)
    - 乘法 (*)
    - 除法 (/)
    - 括号 ()
    
    示例：
    - "2 + 3" → 5
    - "10 * (5 + 3)" → 80
    
    注意：只接受数学表达式，不支持变量。""",
    parameters={...}
)
```

### 3. 参数验证

在工具函数中验证输入：

```python
def search_database(query: str, limit: int = 10) -> str:
    """搜索数据库"""
    
    # 验证参数
    if not query or not query.strip():
        raise ValueError("查询字符串不能为空")
    
    if limit < 1 or limit > 100:
        raise ValueError("limit 必须在 1-100 之间")
    
    # 执行搜索
    results = do_search(query, limit)
    return format_results(results)
```

### 4. 错误处理

工具应该优雅地处理错误：

```python
def call_external_api(endpoint: str) -> str:
    """调用外部 API"""
    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return "API 请求超时，请稍后重试"
    except requests.exceptions.RequestException as e:
        return f"API 调用失败: {str(e)}"
    except Exception as e:
        return f"未知错误: {str(e)}"
```

### 5. 返回格式化的结果

返回人类可读的字符串：

```python
# ✅ 好的例子
def get_user_info(user_id: int) -> str:
    user = fetch_user(user_id)
    return f"""用户信息：
姓名：{user.name}
邮箱：{user.email}
注册时间：{user.created_at}"""

# ❌ 不好的例子
def get_user_info(user_id: int) -> dict:
    return fetch_user(user_id)  # 返回原始字典
```

---

## 错误处理

### 1. 捕获 API 错误

```python
from src.shuyixiao_agent import SimpleAgent

def safe_chat(agent: SimpleAgent, message: str) -> str:
    try:
        return agent.chat(message)
    except ValueError as e:
        # 配置错误
        return f"配置错误：{e}"
    except Exception as e:
        # API 或网络错误
        return f"请求失败：{e}"
```

### 2. 实现重试机制

```python
import time
from typing import Callable, TypeVar

T = TypeVar('T')

def retry_with_backoff(
    func: Callable[..., T],
    max_retries: int = 3,
    initial_delay: float = 1.0
) -> T:
    """带指数退避的重试"""
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            delay = initial_delay * (2 ** attempt)
            print(f"重试 {attempt + 1}/{max_retries}，等待 {delay}秒...")
            time.sleep(delay)

# 使用
result = retry_with_backoff(
    lambda: agent.chat("你好"),
    max_retries=3
)
```

### 3. 记录日志

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def chat_with_logging(agent, message):
    logger.info(f"用户输入: {message}")
    
    try:
        response = agent.chat(message)
        logger.info(f"Agent 回复: {response}")
        return response
    except Exception as e:
        logger.error(f"错误: {e}", exc_info=True)
        raise
```

---

## 性能优化

### 1. 控制 Token 使用

```python
client = GiteeAIClient()

# 限制生成长度
response = client.chat_completion(
    messages=[...],
    max_tokens=500  # 限制输出长度
)
```

### 2. 调整温度参数

```python
# 低温度 = 更确定性（适合事实性任务）
response = client.chat_completion(
    messages=[...],
    temperature=0.3
)

# 高温度 = 更有创造性（适合创意任务）
response = client.chat_completion(
    messages=[...],
    temperature=1.2
)
```

### 3. 批量处理

```python
def process_batch(agent: SimpleAgent, messages: List[str]):
    """批量处理消息"""
    results = []
    for msg in messages:
        try:
            result = agent.chat(msg)
            results.append(result)
        except Exception as e:
            results.append(f"错误: {e}")
    return results
```

### 4. 缓存响应

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_chat(message: str) -> str:
    """缓存常见问题的回复"""
    agent = SimpleAgent()
    return agent.chat(message)
```

---

## 安全性

### 1. 保护 API Key

```python
# ✅ 使用环境变量
from dotenv import load_dotenv
load_dotenv()
agent = SimpleAgent()  # 自动从环境变量读取

# ❌ 硬编码在代码中
agent = SimpleAgent(api_key="sk-xxxxx")  # 不要这样做！
```

### 2. 输入验证

```python
def sanitize_input(user_input: str) -> str:
    """清理用户输入"""
    
    # 限制长度
    if len(user_input) > 1000:
        user_input = user_input[:1000]
    
    # 移除危险字符
    user_input = user_input.strip()
    
    return user_input

# 使用
safe_input = sanitize_input(user_input)
response = agent.chat(safe_input)
```

### 3. 工具权限控制

```python
class SecureToolAgent(ToolAgent):
    """带权限控制的 Agent"""
    
    def __init__(self, allowed_tools: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_tools = set(allowed_tools)
    
    def register_tool(self, name: str, *args, **kwargs):
        if name not in self.allowed_tools:
            raise PermissionError(f"工具 {name} 未授权")
        super().register_tool(name, *args, **kwargs)
```

### 4. 限流

```python
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    """简单的限流器"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = timedelta(seconds=time_window)
        self.requests = defaultdict(list)
    
    def allow_request(self, user_id: str) -> bool:
        now = datetime.now()
        
        # 清理过期记录
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.time_window
        ]
        
        # 检查是否超限
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        self.requests[user_id].append(now)
        return True

# 使用
limiter = RateLimiter(max_requests=10, time_window=60)

if limiter.allow_request(user_id):
    response = agent.chat(message)
else:
    response = "请求过于频繁，请稍后再试"
```

---

## 测试

### 1. 单元测试

```python
import pytest
from src.shuyixiao_agent.tools.basic_tools import calculate

def test_calculate():
    """测试计算工具"""
    assert calculate("2 + 2") == 4.0
    assert calculate("10 * 5") == 50.0
    assert calculate("(2 + 3) * 4") == 20.0
    
    with pytest.raises(ValueError):
        calculate("invalid expression")
```

### 2. Mock API 调用

```python
from unittest.mock import Mock, patch

def test_agent_with_mock():
    """使用 Mock 测试 Agent"""
    
    with patch('src.shuyixiao_agent.gitee_ai_client.requests.post') as mock_post:
        # 设置 Mock 响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "测试回复"
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # 测试
        agent = SimpleAgent(api_key="test_key")
        response = agent.chat("测试")
        
        assert response == "测试回复"
        mock_post.assert_called_once()
```

### 3. 集成测试

```python
def test_tool_agent_integration():
    """集成测试"""
    
    agent = ToolAgent(api_key="test_key")
    
    # 注册测试工具
    def mock_tool(param: str) -> str:
        return f"处理: {param}"
    
    agent.register_tool(
        name="mock_tool",
        func=mock_tool,
        description="测试工具",
        parameters={"type": "object", "properties": {}}
    )
    
    # 测试完整流程
    response = agent.run("使用 mock_tool")
    assert "处理" in response
```

---

## 部署

### 1. 环境变量管理

生产环境使用专门的配置：

```python
# config/production.py
from pydantic_settings import BaseSettings

class ProductionSettings(BaseSettings):
    gitee_ai_api_key: str
    request_timeout: int = 30
    max_retries: int = 5
    enable_failover: bool = True
    
    class Config:
        env_file = ".env.production"
```

### 2. Docker 部署

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装 Poetry
RUN pip install poetry

# 复制依赖文件
COPY pyproject.toml poetry.lock ./

# 安装依赖
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# 复制代码
COPY . .

# 运行
CMD ["python", "your_app.py"]
```

### 3. 健康检查

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    """健康检查端点"""
    try:
        # 测试 Agent 是否正常
        agent = SimpleAgent()
        agent.chat("测试")
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### 4. 监控

```python
import time
from prometheus_client import Counter, Histogram

# 定义指标
request_count = Counter('agent_requests_total', 'Total requests')
request_duration = Histogram('agent_request_duration_seconds', 'Request duration')

def monitored_chat(agent, message):
    """带监控的对话"""
    request_count.inc()
    
    start_time = time.time()
    try:
        response = agent.chat(message)
        return response
    finally:
        duration = time.time() - start_time
        request_duration.observe(duration)
```

---

## 常见陷阱

### 1. 避免在循环中创建 Agent

```python
# ❌ 不好的做法
for message in messages:
    agent = SimpleAgent()  # 每次都创建新实例
    response = agent.chat(message)

# ✅ 好的做法
agent = SimpleAgent()  # 复用实例
for message in messages:
    response = agent.chat(message)
```

### 2. 注意消息历史的长度

```python
# 对于长对话，定期清理历史
if len(state["messages"]) > 20:
    # 只保留最近的消息
    state["messages"] = state["messages"][-10:]
```

### 3. 合理设置超时

```python
# 根据任务复杂度设置合理的超时
settings.request_timeout = 120  # 复杂任务
settings.request_timeout = 30   # 简单任务
```

---

## 总结

遵循这些最佳实践可以帮助你：
- 构建更稳定的 Agent
- 提高性能和效率
- 确保安全性
- 便于维护和扩展

记住：**从简单开始，逐步优化。**

---

## 参考资源

- [LangGraph 最佳实践](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
- [LangChain 安全指南](https://python.langchain.com/docs/security)
- [码云 AI 文档](https://ai.gitee.com/docs/products/apis)

