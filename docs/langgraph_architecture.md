# LangGraph 架构详解

本文档详细介绍 shuyixiao-agent 项目中 LangGraph 的架构设计。

## 什么是 LangGraph？

LangGraph 是一个用于构建有状态、多参与者应用的框架，基于图（Graph）的概念，特别适合构建 Agent 和工作流。

### 核心概念

1. **状态（State）**：图中流动的数据结构
2. **节点（Node）**：执行具体操作的函数
3. **边（Edge）**：连接节点的路径
4. **条件边（Conditional Edge）**：根据状态决定下一步的路径

## 项目中的 LangGraph 实现

### SimpleAgent 架构

SimpleAgent 是最简单的实现，只有一个节点。

#### 状态定义

```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_action: str
```

**字段说明：**
- `messages`: 消息历史，使用 `operator.add` 实现累加
- `next_action`: 下一步动作标识

#### 图结构

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       v
┌─────────────┐
│   chat      │  调用模型生成回复
└──────┬──────┘
       │
       v
┌─────────────┐
│    END      │
└─────────────┘
```

#### 代码实现

```python
def _build_graph(self) -> StateGraph:
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("chat", self._chat_node)
    
    # 设置入口
    workflow.set_entry_point("chat")
    
    # 添加边
    workflow.add_edge("chat", END)
    
    return workflow.compile()
```

#### chat 节点

```python
def _chat_node(self, state: AgentState) -> AgentState:
    """对话节点：调用模型生成回复"""
    
    # 1. 构建消息列表
    messages = []
    if self.system_message:
        messages.append({"role": "system", "content": self.system_message})
    
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})
    
    # 2. 调用模型
    response = self.client.chat_completion(messages=messages)
    ai_message = response["choices"][0]["message"]["content"]
    
    # 3. 返回更新后的状态
    return {
        "messages": [AIMessage(content=ai_message)],
        "next_action": "end"
    }
```

---

### ToolAgent 架构

ToolAgent 更复杂，支持工具调用和迭代。

#### 状态定义

```python
class ToolAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_action: str
    iterations: int
```

**字段说明：**
- `messages`: 消息历史
- `next_action`: 下一步动作（"tool" 或 "end"）
- `iterations`: 当前迭代次数

#### 图结构

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       v
┌─────────────┐
│   agent     │  调用模型决定动作
└──────┬──────┘
       │
       v
┌─────────────┐
│  判断条件   │  是否需要调用工具？
└──┬────────┬─┘
   │        │
   │ tool   │ end
   v        v
┌──────┐  ┌────┐
│tools │  │END │
└──┬───┘  └────┘
   │
   │ (循环)
   └──────┐
          │
          v
   ┌─────────────┐
   │   agent     │
   └─────────────┘
```

#### 代码实现

```python
def _build_graph(self) -> StateGraph:
    workflow = StateGraph(ToolAgentState)
    
    # 添加节点
    workflow.add_node("agent", self._agent_node)
    workflow.add_node("tools", self._tools_node)
    
    # 设置入口
    workflow.set_entry_point("agent")
    
    # 添加条件边
    workflow.add_conditional_edges(
        "agent",
        self._should_continue,
        {
            "continue": "tools",
            "end": END
        }
    )
    
    # 工具节点回到 agent
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()
```

#### agent 节点

```python
def _agent_node(self, state: ToolAgentState) -> ToolAgentState:
    """Agent 节点：调用模型决定下一步动作"""
    
    # 1. 构建消息
    messages = [...]
    
    # 2. 调用模型（传入工具定义）
    kwargs = {}
    if self.tools:
        kwargs["tools"] = self.tools
        kwargs["tool_choice"] = "auto"
    
    response = self.client.chat_completion(messages=messages, **kwargs)
    ai_msg = response["choices"][0]["message"]
    
    # 3. 检查是否需要调用工具
    if "tool_calls" in ai_msg and ai_msg["tool_calls"]:
        return {
            "messages": [AIMessage(
                content=ai_msg.get("content", ""),
                additional_kwargs={"tool_calls": ai_msg["tool_calls"]}
            )],
            "next_action": "tool",
            "iterations": state.get("iterations", 0) + 1
        }
    else:
        return {
            "messages": [AIMessage(content=ai_msg["content"])],
            "next_action": "end",
            "iterations": state.get("iterations", 0) + 1
        }
```

#### tools 节点

```python
def _tools_node(self, state: ToolAgentState) -> ToolAgentState:
    """工具节点：执行工具调用"""
    
    # 1. 获取工具调用信息
    last_message = state["messages"][-1]
    tool_calls = last_message.additional_kwargs.get("tool_calls", [])
    
    tool_messages = []
    
    # 2. 执行每个工具
    for tool_call in tool_calls:
        tool_name = tool_call["function"]["name"]
        tool_args = json.loads(tool_call["function"]["arguments"])
        tool_id = tool_call["id"]
        
        if tool_name in self.tool_functions:
            try:
                result = self.tool_functions[tool_name](**tool_args)
                tool_messages.append(ToolMessage(
                    content=str(result),
                    tool_call_id=tool_id
                ))
            except Exception as e:
                tool_messages.append(ToolMessage(
                    content=f"工具执行错误: {str(e)}",
                    tool_call_id=tool_id
                ))
    
    # 3. 返回工具结果
    return {
        "messages": tool_messages,
        "next_action": "agent",
        "iterations": state["iterations"]
    }
```

#### 条件判断

```python
def _should_continue(self, state: ToolAgentState) -> str:
    """判断是否继续"""
    
    # 检查迭代次数
    if state["iterations"] >= self.max_iterations:
        return "end"
    
    # 检查是否需要调用工具
    if state["next_action"] == "tool":
        return "continue"
    
    return "end"
```

---

## 执行流程示例

### SimpleAgent 执行流程

```
用户输入: "你好"

1. 初始状态:
   {
     "messages": [HumanMessage("你好")],
     "next_action": ""
   }

2. chat 节点:
   - 构建请求消息
   - 调用码云 AI API
   - 生成 AI 回复
   
3. 输出状态:
   {
     "messages": [
       HumanMessage("你好"),
       AIMessage("你好！我是...")
     ],
     "next_action": "end"
   }

4. 返回最后的 AI 消息
```

### ToolAgent 执行流程

```
用户输入: "现在几点了？"

1. 初始状态:
   {
     "messages": [HumanMessage("现在几点了？")],
     "next_action": "",
     "iterations": 0
   }

2. agent 节点 (第1次):
   - 调用模型
   - 模型决定使用 get_current_time 工具
   - 返回 tool_calls
   
   状态:
   {
     "messages": [
       HumanMessage("现在几点了？"),
       AIMessage(tool_calls=[...])
     ],
     "next_action": "tool",
     "iterations": 1
   }

3. 条件判断:
   - next_action == "tool" → 继续到 tools 节点

4. tools 节点:
   - 执行 get_current_time()
   - 返回结果 "2024-01-01 12:00:00"
   
   状态:
   {
     "messages": [
       ...,
       ToolMessage("2024-01-01 12:00:00")
     ],
     "next_action": "agent",
     "iterations": 1
   }

5. agent 节点 (第2次):
   - 接收工具结果
   - 生成最终回复 "现在是 2024-01-01 12:00:00"
   
   状态:
   {
     "messages": [
       ...,
       AIMessage("现在是 2024-01-01 12:00:00")
     ],
     "next_action": "end",
     "iterations": 2
   }

6. 条件判断:
   - next_action == "end" → 结束

7. 返回最后的 AI 消息
```

---

## 状态管理

### 状态更新机制

LangGraph 使用 `Annotated` 和 `operator.add` 实现状态的增量更新：

```python
messages: Annotated[Sequence[BaseMessage], operator.add]
```

这意味着：
- 每个节点返回的 `messages` 会**追加**到现有的 messages 列表中
- 而不是替换整个列表

**示例：**

```python
# 初始状态
state = {"messages": [HumanMessage("你好")]}

# 节点返回
return {"messages": [AIMessage("你好！")]}

# 实际状态变为
state = {"messages": [HumanMessage("你好"), AIMessage("你好！")]}
```

### 其他字段

对于没有使用 `operator.add` 的字段，会直接替换：

```python
# 初始
state = {"next_action": ""}

# 节点返回
return {"next_action": "tool"}

# 结果
state = {"next_action": "tool"}
```

---

## 扩展 Agent

### 添加新节点

```python
def _build_graph(self):
    workflow = StateGraph(AgentState)
    
    # 添加多个节点
    workflow.add_node("preprocess", self._preprocess_node)
    workflow.add_node("chat", self._chat_node)
    workflow.add_node("postprocess", self._postprocess_node)
    
    # 设置流程
    workflow.set_entry_point("preprocess")
    workflow.add_edge("preprocess", "chat")
    workflow.add_edge("chat", "postprocess")
    workflow.add_edge("postprocess", END)
    
    return workflow.compile()
```

### 添加复杂条件

```python
def _route_message(self, state: AgentState) -> str:
    """根据消息内容路由到不同节点"""
    last_message = state["messages"][-1].content
    
    if "翻译" in last_message:
        return "translate"
    elif "搜索" in last_message:
        return "search"
    else:
        return "chat"

workflow.add_conditional_edges(
    "router",
    self._route_message,
    {
        "translate": "translate_node",
        "search": "search_node",
        "chat": "chat_node"
    }
)
```

### 添加记忆功能

```python
class MemoryAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    memory: Dict[str, Any]  # 持久化记忆
    session_id: str

def _memory_node(self, state: MemoryAgentState):
    """加载历史记忆"""
    session_id = state["session_id"]
    memory = load_memory(session_id)
    
    return {"memory": memory}
```

---

## 调试技巧

### 打印状态

```python
def _debug_node(self, state: AgentState) -> AgentState:
    print(f"当前状态: {state}")
    return {}  # 不修改状态

workflow.add_node("debug", self._debug_node)
```

### 可视化图结构

```python
# 获取 Mermaid 格式的图
graph_def = agent.graph.get_graph()
print(graph_def.draw_mermaid())
```

### 步进执行

```python
# 使用 stream 逐步查看状态变化
for step in agent.graph.stream(initial_state):
    print(f"步骤: {step}")
```

---

## 最佳实践

1. **保持节点简单**：每个节点只做一件事
2. **使用类型提示**：确保状态定义清晰
3. **处理异常**：在节点中捕获并处理错误
4. **限制迭代次数**：防止无限循环
5. **记录日志**：在关键节点记录状态

---

## 进阶主题

### 并行执行

```python
# 多个节点并行执行
workflow.add_node("task1", task1_node)
workflow.add_node("task2", task2_node)
workflow.add_node("merge", merge_node)

workflow.set_entry_point("task1")
workflow.set_entry_point("task2")

workflow.add_edge("task1", "merge")
workflow.add_edge("task2", "merge")
```

### 子图

```python
# 创建子图
subgraph = StateGraph(SubState)
# ... 配置子图

# 在主图中使用
workflow.add_node("sub", subgraph.compile())
```

### 人工介入

```python
from langgraph.checkpoint import MemorySaver

# 使用检查点实现人工介入
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# 暂停并等待人工输入
result = graph.invoke(state, {"configurable": {"thread_id": "1"}})
```

---

## 参考资源

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)
- [LangChain 文档](https://python.langchain.com/)

---

## 下一步

- 查看 [API 参考](./api_reference.md)
- 阅读 [最佳实践](./best_practices.md)
- 尝试修改示例实现自己的 Agent

