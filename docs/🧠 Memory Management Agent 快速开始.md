# 🧠 Memory Management Agent 快速开始

## ✅ 已完成

Memory Management Agent 的前端界面已经完全集成到Web应用中！

## 🚀 如何使用

### 1. 启动Web服务器

```bash
python run_web.py
```

或

```bash
python run_web_auto.py
```

### 2. 访问Web界面

打开浏览器访问：`http://localhost:8001`

### 3. 查看Memory Management标签页

在页面顶部的标签栏中，点击 **"🧠 Memory Management"** 标签页。

## 📋 功能说明

### 左侧面板

#### 📝 存储新记忆
- 输入记忆内容
- 选择记忆类型（语义、情景、长期、短期、工作、程序性）
- 设置重要性级别（1-5星）
- 添加标签（用逗号分隔）
- 点击"💾 存储记忆"按钮

#### 🔍 检索记忆
- 输入查询内容
- 勾选要搜索的记忆类型
- 点击"🔍 搜索记忆"按钮
- 结果会显示在右侧的"📋 检索结果"区域

#### 📊 记忆统计
- 查看总记忆数
- 按类型分布
- 存储大小
- 点击"🔄 刷新统计"更新数据

### 右侧面板

#### 💬 基于记忆的对话
- 在输入框中输入消息
- AI会基于存储的记忆回答问题
- 重要对话会自动存储为记忆

#### 📋 检索结果
- 显示搜索到的相关记忆
- 显示相关性分数
- 显示记忆类型和标签

## 💡 使用示例

### 示例1：存储用户偏好

1. 在"存储新记忆"区域输入：`用户喜欢Python编程，偏好函数式编程风格`
2. 选择类型：`💾 长期记忆 (用户偏好)`
3. 重要性：`⭐⭐⭐⭐ 高`
4. 标签：`用户偏好, Python, 编程风格`
5. 点击"💾 存储记忆"

### 示例2：基于记忆对话

在对话框中输入：`你知道我喜欢什么编程语言吗？`

AI会基于之前存储的记忆回答：`根据我的记忆，您喜欢Python编程，并且偏好函数式编程风格。`

### 示例3：检索记忆

1. 在"检索记忆"输入框输入：`编程偏好`
2. 勾选相关类型（语义、长期等）
3. 点击"🔍 搜索记忆"
4. 在右侧查看检索结果和相关性分数

## 🎯 记忆类型说明

| 类型 | 图标 | 说明 | 适用场景 |
|------|------|------|----------|
| 语义记忆 | 📚 | 事实和概念性知识 | 定义、规则、通用信息 |
| 情景记忆 | 📖 | 具体的事件和经历 | 对话历史、具体事件 |
| 长期记忆 | 💾 | 重要的知识和经验 | 用户偏好、历史经验 |
| 短期记忆 | ⚡ | 最近的对话和交互 | 临时信息、最近对话 |
| 工作记忆 | 🔧 | 当前任务相关信息 | 任务状态、临时变量 |
| 程序性记忆 | ⚙️ | 技能和操作步骤 | 流程、步骤、方法 |

## 🌟 高级功能

### API访问

也可以通过API直接访问Memory Management功能：

```bash
# 存储记忆
curl -X POST http://localhost:8001/api/memory/store \
  -H "Content-Type: application/json" \
  -d '{"content":"测试记忆","memory_type":"semantic","importance":3,"session_id":"default"}'

# 检索记忆
curl -X POST http://localhost:8001/api/memory/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query":"测试","session_id":"default"}'

# 获取统计
curl http://localhost:8001/api/memory/statistics/default
```

### Python代码

```python
from src.shuyixiao_agent.gitee_ai_client import GiteeAIClient
from src.shuyixiao_agent.agents.memory_agent import (
    MemoryAgent, MemoryType, MemoryImportance
)

llm_client = GiteeAIClient()
agent = MemoryAgent(llm_client=llm_client)

# 存储记忆
agent.store_memory(
    content="用户喜欢Python",
    memory_type=MemoryType.SEMANTIC,
    importance=MemoryImportance.HIGH
)

# 基于记忆对话
response = agent.chat_with_memory("我喜欢什么？")
print(response)
```

### 命令行演示

```bash
python examples/18_memory_agent_demo.py
```

## 📚 更多信息

- **完整文档**: `MEMORY_MANAGEMENT_FEATURES.md`
- **集成指南**: `MEMORY_AGENT_WEB_INTEGRATION_GUIDE.md`
- **使用示例**: `examples/18_memory_agent_demo.py`

## 🎉 开始使用吧！

现在您可以启动Web服务器，点击"🧠 Memory Management"标签页，开始体验智能记忆管理功能了！

