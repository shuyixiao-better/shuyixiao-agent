"""
RAG 流式响应示例

演示如何使用 RAG Agent 的流式输出功能
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.shuyixiao_agent import RAGAgent


def main():
    """主函数"""
    print("=" * 60)
    print("RAG 流式响应示例")
    print("=" * 60)
    print()
    
    # 创建 RAG Agent
    print("1. 创建 RAG Agent...")
    agent = RAGAgent(
        collection_name="streaming_demo",
        use_reranker=True,
        retrieval_mode="hybrid"
    )
    print()
    
    # 添加知识库文档
    print("2. 添加知识库文档...")
    texts = [
        """
        流式输出（Streaming）是一种实时传输数据的技术。
        在 AI 应用中，流式输出允许模型逐步生成和返回结果，而不是等待完整生成后再返回。
        这大大提升了用户体验，特别是在生成长文本时。
        """,
        """
        Server-Sent Events (SSE) 是一种服务器向浏览器推送信息的技术。
        SSE 基于 HTTP 协议，服务器可以主动向客户端发送消息。
        在 Web 应用中，SSE 常用于实现流式响应和实时更新。
        """,
        """
        在 Python 中，可以使用生成器（Generator）来实现流式输出。
        生成器函数使用 yield 语句返回数据，每次调用 next() 时返回一个值。
        这种惰性计算的方式非常适合处理大量数据或实时数据流。
        """,
        """
        FastAPI 框架提供了 StreamingResponse 类来支持流式响应。
        通过返回 StreamingResponse 对象，可以实现服务器向客户端的流式数据传输。
        这在实现 AI 应用的实时响应时非常有用。
        """
    ]
    
    agent.add_texts(texts)
    print(f"已添加 {len(texts)} 个文档到知识库")
    print()
    
    # 流式查询
    print("3. 流式查询演示...")
    print("-" * 60)
    
    question = "什么是流式输出？它有什么优势？"
    print(f"问题: {question}")
    print("-" * 40)
    print("回答: ", end="", flush=True)
    
    # 使用流式输出
    stream = agent.query(
        question=question,
        top_k=3,
        optimize_query=True,
        stream=True
    )
    
    # 逐个输出片段
    for chunk in stream:
        print(chunk, end="", flush=True)
    
    print("\n")
    print("-" * 60)
    
    # 再来一个流式查询
    question2 = "如何在 Python 中实现流式输出？"
    print(f"\n问题: {question2}")
    print("-" * 40)
    print("回答: ", end="", flush=True)
    
    stream2 = agent.query(
        question=question2,
        top_k=3,
        use_history=True,  # 使用对话历史
        optimize_query=True,
        stream=True
    )
    
    for chunk in stream2:
        print(chunk, end="", flush=True)
    
    print("\n")
    print("=" * 60)
    print("示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

