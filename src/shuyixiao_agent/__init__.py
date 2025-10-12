"""
shuyixiao-agent: 基于 LangGraph 和码云 AI 的智能 Agent 项目
"""

__version__ = "0.1.0"
__author__ = "ShuYixiao"

from .gitee_ai_client import GiteeAIClient
from .agents.simple_agent import SimpleAgent
from .config import settings
from .rag.rag_agent import RAGAgent

__all__ = [
    "GiteeAIClient",
    "SimpleAgent",
    "RAGAgent",
    "settings",
]

