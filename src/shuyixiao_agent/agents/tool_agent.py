"""
带工具调用的 Agent

使用 LangGraph 实现一个支持工具调用的 Agent
"""

from typing import TypedDict, Annotated, Sequence, List, Dict, Any, Callable
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
import operator
import json

from ..gitee_ai_client import GiteeAIClient


class ToolAgentState(TypedDict):
    """Tool Agent 状态定义"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_action: str
    iterations: int


class ToolAgent:
    """
    带工具调用的 Agent
    
    支持工具调用的 Agent，可以让模型调用预定义的工具来完成任务。
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        tools: List[Dict[str, Any]] = None,
        system_message: str = "你是一个有帮助的AI助手。你可以使用提供的工具来完成任务。",
        max_iterations: int = 10
    ):
        """
        初始化 Tool Agent
        
        Args:
            api_key: 码云 AI API Key
            model: 使用的模型名称
            tools: 工具列表
            system_message: 系统提示词
            max_iterations: 最大迭代次数
        """
        self.client = GiteeAIClient(api_key=api_key, model=model)
        self.system_message = system_message
        self.max_iterations = max_iterations
        self.tools = tools or []
        self.tool_functions = {}
        self.graph = self._build_graph()
    
    def register_tool(self, name: str, func: Callable, description: str, parameters: Dict):
        """
        注册工具
        
        Args:
            name: 工具名称
            func: 工具函数
            description: 工具描述
            parameters: 工具参数定义（JSON Schema 格式）
        """
        tool_def = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        self.tools.append(tool_def)
        self.tool_functions[name] = func
    
    def _build_graph(self) -> StateGraph:
        """
        构建 LangGraph 状态图
        
        Returns:
            编译后的状态图
        """
        workflow = StateGraph(ToolAgentState)
        
        # 添加节点
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", self._tools_node)
        
        # 设置入口点
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
        
        # 工具节点之后回到 agent
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def _agent_node(self, state: ToolAgentState) -> ToolAgentState:
        """
        Agent 节点：调用模型决定下一步动作
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        # 构建消息列表
        messages = []
        
        if self.system_message:
            messages.append({
                "role": "system",
                "content": self.system_message
            })
        
        # 添加历史消息
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                messages.append({
                    "role": "user",
                    "content": msg.content
                })
            elif isinstance(msg, AIMessage):
                messages.append({
                    "role": "assistant",
                    "content": msg.content
                })
            elif isinstance(msg, ToolMessage):
                messages.append({
                    "role": "tool",
                    "content": msg.content,
                    "tool_call_id": msg.tool_call_id
                })
        
        # 调用模型（如果有工具，传入工具定义）
        kwargs = {}
        if self.tools:
            kwargs["tools"] = self.tools
            kwargs["tool_choice"] = "auto"
        
        response = self.client.chat_completion(messages=messages, **kwargs)
        
        ai_msg = response["choices"][0]["message"]
        
        # 检查是否需要调用工具
        if "tool_calls" in ai_msg and ai_msg["tool_calls"]:
            return {
                "messages": [AIMessage(
                    content=ai_msg.get("content") or "",
                    additional_kwargs={"tool_calls": ai_msg["tool_calls"]}
                )],
                "next_action": "tool",
                "iterations": state.get("iterations", 0) + 1
            }
        else:
            return {
                "messages": [AIMessage(content=ai_msg.get("content") or "")],
                "next_action": "end",
                "iterations": state.get("iterations", 0) + 1
            }
    
    def _tools_node(self, state: ToolAgentState) -> ToolAgentState:
        """
        工具节点：执行工具调用
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        last_message = state["messages"][-1]
        tool_calls = last_message.additional_kwargs.get("tool_calls", [])
        
        tool_messages = []
        
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])
            tool_id = tool_call["id"]
            
            # 执行工具
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
            else:
                tool_messages.append(ToolMessage(
                    content=f"未找到工具: {tool_name}",
                    tool_call_id=tool_id
                ))
        
        return {
            "messages": tool_messages,
            "next_action": "agent",
            "iterations": state["iterations"]
        }
    
    def _should_continue(self, state: ToolAgentState) -> str:
        """
        判断是否继续
        
        Args:
            state: 当前状态
            
        Returns:
            "continue" 或 "end"
        """
        if state["iterations"] >= self.max_iterations:
            return "end"
        
        if state["next_action"] == "tool":
            return "continue"
        
        return "end"
    
    def run(self, user_input: str) -> str:
        """
        运行 Agent
        
        Args:
            user_input: 用户输入
            
        Returns:
            Agent 回复
        """
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "next_action": "",
            "iterations": 0
        }
        
        result = self.graph.invoke(initial_state)
        
        # 找到最后一个 AI 消息
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage):
                return msg.content
        
        return "未能生成回复"

