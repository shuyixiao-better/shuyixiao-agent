"""
RAG (检索增强生成) 基础使用示例

演示如何使用 RAG Agent 进行知识库问答
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
    print("RAG Agent 基础使用示例")
    print("=" * 60)
    print()
    
    # 创建 RAG Agent
    print("1. 创建 RAG Agent...")
    agent = RAGAgent(
        collection_name="demo",
        use_reranker=True,
        retrieval_mode="hybrid"
    )
    print()
    
    # 添加文档（从文本）
    print("2. 添加知识库文档...")
    texts = [
        """
        Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年首次发布。
        Python 的设计哲学强调代码的可读性和简洁的语法（尤其是使用空格缩进划分代码块）。
        Python 支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。
        """,
        """
        LangChain 是一个用于开发由语言模型驱动的应用程序的框架。
        它提供了标准的、可扩展的接口和外部集成，使开发者能够轻松构建 LLM 应用。
        LangChain 的主要特性包括：链（Chains）、代理（Agents）、记忆（Memory）等。
        """,
        """
        RAG（检索增强生成）是一种结合信息检索和文本生成的技术。
        它首先从知识库中检索相关文档，然后将这些文档作为上下文传递给语言模型。
        RAG 可以显著提高模型回答的准确性和可信度，减少幻觉问题。
        """,
        """
        向量数据库是专门为存储和检索向量嵌入而设计的数据库。
        常见的向量数据库包括 Chroma、Pinecone、Weaviate、Milvus 等。
        向量数据库支持高效的相似度搜索，是 RAG 系统的核心组件。
        """
    ]
    
    metadatas = [
        {"source": "python_intro", "topic": "编程语言"},
        {"source": "langchain_intro", "topic": "AI 框架"},
        {"source": "rag_intro", "topic": "AI 技术"},
        {"source": "vectordb_intro", "topic": "数据库"}
    ]
    
    agent.add_texts(texts, metadatas)
    print(f"已添加 {len(texts)} 个文档到知识库")
    print(f"知识库总文档数: {agent.get_document_count()}")
    print()
    
    # 进行查询
    print("3. 开始查询...")
    print("-" * 60)
    
    questions = [
        "什么是 Python？",
        "RAG 技术有什么优势？",
        "LangChain 有哪些主要特性？",
        "向量数据库的作用是什么？"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n问题 {i}: {question}")
        print("-" * 40)
        
        answer = agent.query(
            question=question,
            top_k=3,
            use_history=True,
            optimize_query=True,
            stream=False
        )
        
        print(f"回答: {answer}")
        print()
    
    print("=" * 60)
    print("示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

