"""
简单的对话 Agent

使用 LangGraph 实现一个基础的对话 Agent
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator

from ..gitee_ai_client import GiteeAIClient
from ..config import settings


class AgentState(TypedDict):
    """Agent 状态定义"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_action: str


class SimpleAgent:
    """
    简单对话 Agent
    
    这是一个基础的对话 Agent，使用 LangGraph 构建状态图，
    通过码云 AI 模型进行对话生成。
    """
    
    def __init__(
        self, 
        api_key: str = None,
        model: str = None,
        system_message: str = "你是一个有帮助的AI助手，请友好、专业地回答用户的问题。"
    ):
        """
        初始化 Simple Agent
        
        Args:
            api_key: 码云 AI API Key
            model: 使用的模型名称（留空则使用配置的 AGENT_MODEL 或默认模型）
            system_message: 系统提示词
        """
        # 如果配置了专用的 Agent 模型，使用该模型
        if model is None:
            model = settings.agent_model or settings.gitee_ai_model
        
        self.client = GiteeAIClient(api_key=api_key, model=model)
        self.system_message = system_message
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        构建 LangGraph 状态图
        
        Returns:
            编译后的状态图
        """
        # 创建状态图
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("chat", self._chat_node)
        
        # 设置入口点
        workflow.set_entry_point("chat")
        
        # 添加条件边
        workflow.add_edge("chat", END)
        
        # 编译图
        return workflow.compile()
    
    def _chat_node(self, state: AgentState) -> AgentState:
        """
        对话节点：调用模型生成回复
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        # 构建消息列表
        messages = []
        
        # 添加系统消息
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
        
        # 调用模型
        response = self.client.chat_completion(messages=messages)
        ai_message = response["choices"][0]["message"].get("content") or ""
        
        # 返回更新后的状态
        return {
            "messages": [AIMessage(content=ai_message)],
            "next_action": "end"
        }
    
    def chat(self, user_input: str) -> str:
        """
        单轮对话
        
        Args:
            user_input: 用户输入
            
        Returns:
            Agent 回复
        """
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "next_action": ""
        }
        
        result = self.graph.invoke(initial_state)
        return result["messages"][-1].content
    
    def chat_stream(self, user_input: str):
        """
        流式对话（未来可扩展）
        
        Args:
            user_input: 用户输入
            
        Yields:
            回复的每个部分
        """
        # 目前简单实现，未来可以添加流式支持
        response = self.chat(user_input)
        yield response

