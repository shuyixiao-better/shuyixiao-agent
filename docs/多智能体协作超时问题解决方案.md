# 多智能体协作超时问题解决方案

## 问题分析

### 原因
多智能体协作系统在执行时会遇到超时问题，主要原因是：

1. **多次 API 调用累积**
   - 研究团队有 5 个 Agents（研究负责人、理论研究者、数据科学家、实验研究者、评审专家）
   - 软件开发团队有 5 个 Agents（产品经理、架构师、后端/前端工程师、QA）
   - 每个 Agent 都需要调用一次 LLM API
   - 在层级协作模式下，这些调用是**顺序执行**的

2. **单个请求超时限制**
   - 原始配置：`REQUEST_TIMEOUT = 60秒`
   - 如果每个 Agent 调用需要 15-20 秒
   - 5 个 Agents：5 × 15 = 75秒 > 60秒（超时！）

3. **网络不稳定**
   - Gitee AI API 可能响应较慢
   - 网络延迟会进一步增加总时间

### 错误信息
```
ReadTimeoutError("HTTPSConnectionPool(host='ai.gitee.com', port=443): 
Read timed out. (read timeout=60)")
```

## 解决方案

### ✅ 已实施的修复

#### 1. 新增专用超时配置
**文件**: `src/shuyixiao_agent/config.py`

```python
# 多智能体协作超时时间（秒）
multi_agent_timeout: int = Field(
    default=180,  # 3分钟
    description="多智能体协作超时时间（秒），因为需要多次API调用"
)
```

#### 2. 支持自定义超时时间
**文件**: `src/shuyixiao_agent/gitee_ai_client.py`

```python
def simple_chat(
    self, 
    user_message: str, 
    system_message: Optional[str] = None, 
    timeout: Optional[int] = None  # 新增参数
) -> str:
    # 使用自定义超时或默认超时
    response = self.chat_completion(messages=messages, timeout=timeout)
```

#### 3. 应用到多智能体协作
**文件**: `src/shuyixiao_agent/agents/multi_agent_collaboration.py`

```python
# 每个 Agent 调用时使用更长的超时
response = self.llm_client.simple_chat(
    prompt, 
    timeout=settings.multi_agent_timeout  # 使用 180秒 而不是 60秒
)
```

#### 4. 更新配置示例
**文件**: `env.example`

```bash
# 多智能体协作超时时间（秒）
# 因为多智能体协作需要顺序调用多个 Agent，每个 Agent 都需要调用 API
# 所以需要更长的超时时间。默认 180 秒（3分钟）
# 如果团队规模大或任务复杂，可以适当增加此值
MULTI_AGENT_TIMEOUT=180
```

## 配置建议

### 基本配置（推荐）
对于大多数场景，默认配置即可：

```bash
REQUEST_TIMEOUT=60          # 普通请求：60秒
MULTI_AGENT_TIMEOUT=180     # 多智能体：180秒（3分钟）
```

### 复杂任务配置
如果任务特别复杂或网络较慢：

```bash
REQUEST_TIMEOUT=60
MULTI_AGENT_TIMEOUT=300     # 增加到 5 分钟
```

### 团队规模调整

| 团队规模 | Agent 数量 | 预计时间 | 推荐超时 |
|---------|-----------|---------|---------|
| 小型 | 2-3 个 | 30-60秒 | 120秒 |
| 中型（默认） | 4-5 个 | 60-120秒 | 180秒 |
| 大型 | 6-8 个 | 120-240秒 | 300秒 |
| 超大型 | 9+ 个 | 240秒+ | 600秒 |

## 优化建议

### 1. 选择合适的协作模式

不同协作模式的时间开销：

| 模式 | 特点 | 时间开销 | 推荐场景 |
|-----|------|---------|---------|
| **并行** | Agents 同时工作 | ⚡ 最快（≈单个 Agent 时间） | 多角度分析 |
| **顺序** | 依次执行 | 🐌 慢（累加所有 Agent） | 有明确流程 |
| **层级** | 按阶段执行 | 🚶 中等 | 专业分工（推荐） |
| **对等** | 多轮讨论 | 🐌 很慢（轮数 × Agent数） | 需要深度讨论 |

**建议**：
- 首次使用：选择**并行模式**（最快）
- 复杂任务：选择**层级模式**（质量好）
- 避免使用：**对等模式**（太慢，除非必要）

### 2. 减少 Agent 数量

不是 Agent 越多越好！合理配置：

```python
# ❌ 太多 Agents（可能超时）
team = [
    coordinator,
    specialist1, specialist2, specialist3,
    executor1, executor2, executor3,
    reviewer1, reviewer2,
    advisor1, advisor2
]  # 11 个 Agents，可能需要 3-5 分钟

# ✅ 精简团队（推荐）
team = [
    coordinator,      # 1个协调者
    specialist1,      # 1-2个关键专家
    executor,         # 1个执行者
    reviewer          # 1个审核者
]  # 4-5 个 Agents，约 1-2 分钟
```

### 3. 优化提示词长度

更短的提示词 = 更快的响应：

```python
# ❌ 过长的提示词
system_prompt = """
你是一位资深专家，拥有20年经验......
（500字的详细描述）
请仔细分析以下问题的各个方面......
（又是200字的指导）
"""

# ✅ 精简的提示词
system_prompt = """
你是XX专家，负责：
1. 分析问题
2. 提出方案
3. 给出建议
"""
```

### 4. 使用更快的模型

如果对质量要求不是特别高：

```bash
# 在 .env 中配置
GITEE_AI_MODEL=GLM-4-Flash      # 更快，适合简单任务
# GITEE_AI_MODEL=DeepSeek-V3    # 更慢但质量更高
```

### 5. 本地缓存结果

对于重复的任务，可以缓存结果：

```python
# 在实际使用中，可以添加缓存逻辑
import hashlib
import json

def get_cached_result(task_hash):
    # 检查缓存
    cache_file = f"cache/{task_hash}.json"
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return None

def save_cached_result(task_hash, result):
    os.makedirs("cache", exist_ok=True)
    with open(f"cache/{task_hash}.json", 'w') as f:
        json.dump(result, f)
```

## 监控和调试

### 查看详细日志

```python
collaboration = MultiAgentCollaboration(
    llm_client=llm_client,
    verbose=True  # 开启详细日志
)
```

输出示例：
```
🤖 product_manager 正在思考...
✓ product_manager 完成 (15.2秒)

🤖 system_architect 正在思考...
✓ system_architect 完成 (18.5秒)

...
```

### 测量执行时间

```python
import time

start_time = time.time()
result = collaboration.collaborate(task)
execution_time = time.time() - start_time

print(f"总执行时间: {execution_time:.2f}秒")
print(f"Agent 数量: {len(result.agent_contributions)}")
print(f"平均每个 Agent: {execution_time / len(result.agent_contributions):.2f}秒")
```

## 网络优化

### 1. 检查网络连接

```bash
# 测试连接
ping ai.gitee.com

# 测试 API 可用性
curl https://ai.gitee.com/v1/models
```

### 2. 使用代理（如果需要）

在代码中设置代理：

```python
import os

# 设置代理
os.environ['http_proxy'] = 'http://your-proxy:port'
os.environ['https_proxy'] = 'http://your-proxy:port'
```

### 3. 启用重试机制

已经内置在 `GiteeAIClient` 中：

```python
# 在 config.py 中配置
MAX_RETRIES=3  # 失败后最多重试3次
```

## 常见问题 FAQ

### Q1: 为什么还是超时？

**A**: 检查以下几点：
1. 是否重启了应用？（配置需要重启生效）
2. 是否设置了环境变量 `MULTI_AGENT_TIMEOUT=180`？
3. 是否选择了合适的协作模式？（避免对等模式）
4. 网络是否稳定？（测试 `ping ai.gitee.com`）

### Q2: 可以设置更短的超时时间吗？

**A**: 不建议。建议值：
- 最小：120秒（2分钟）- 仅适用于 2-3 个 Agents
- 推荐：180秒（3分钟）- 适用于 4-5 个 Agents
- 复杂：300秒（5分钟）- 适用于 6+ 个 Agents

### Q3: 能让协作更快吗？

**A**: 可以！方法：
1. 使用**并行模式**（最快）
2. 减少 Agent 数量（4-5个最佳）
3. 使用更快的模型（GLM-4-Flash）
4. 优化提示词（更短更精确）

### Q4: 某个 Agent 超时了怎么办？

**A**: 系统已经有容错机制：
- 单个 Agent 失败不会影响其他 Agents
- 错误信息会被记录
- 可以查看部分结果

## 验证修复

测试新配置是否生效：

```bash
# 1. 重启 Web 应用
python run_web.py

# 2. 访问 http://localhost:8001
# 3. 点击 "👥 Multi-Agent Collaboration"
# 4. 选择一个团队和任务
# 5. 点击"开始协作"

# 应该不再出现超时错误！
```

## 总结

✅ **已修复的问题**：
- 多智能体协作超时问题
- 增加了专用的超时配置（180秒）
- 支持自定义超时时间
- 提供了详细的配置说明

✅ **改进的方面**：
- 更灵活的超时控制
- 更好的错误处理
- 更清晰的配置文档
- 更多的优化建议

🎯 **建议配置**：
```bash
REQUEST_TIMEOUT=60
MULTI_AGENT_TIMEOUT=180
MAX_RETRIES=3
```

📝 **最佳实践**：
1. 使用并行或层级模式
2. 控制 Agent 数量（4-5个）
3. 优化提示词长度
4. 开启详细日志监控
5. 根据需要调整超时时间

---

**现在您可以愉快地使用多智能体协作功能了！** 🚀

