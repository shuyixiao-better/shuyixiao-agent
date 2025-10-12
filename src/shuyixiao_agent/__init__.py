"""
shuyixiao-agent: 基于 LangGraph 和码云 AI 的智能 Agent 项目
"""

__version__ = "0.1.0"
__author__ = "ShuYixiao"

from .gitee_ai_client import GiteeAIClient
from .agents.simple_agent import SimpleAgent
from .config import settings

# RAG Agent 使用延迟导入，避免阻塞启动
# from .rag.rag_agent import RAGAgent

__all__ = [
    "GiteeAIClient",
    "SimpleAgent",
    # "RAGAgent",  # 延迟导入
    "settings",
]


def lazy_import_rag_agent():
    """延迟导入 RAG Agent"""
    from .rag.rag_agent import RAGAgent
    return RAGAgent

