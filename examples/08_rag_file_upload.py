"""
RAG 文件上传示例

演示如何从文件和目录加载文档到 RAG 知识库
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
    print("RAG 文件上传示例")
    print("=" * 60)
    print()
    
    # 创建 RAG Agent
    print("1. 创建 RAG Agent...")
    agent = RAGAgent(
        collection_name="docs_demo",
        use_reranker=True,
        retrieval_mode="hybrid"
    )
    print()
    
    # 从目录加载文档
    print("2. 从目录加载文档...")
    docs_dir = project_root / "docs"
    
    if docs_dir.exists():
        try:
            count = agent.add_documents_from_directory(
                str(docs_dir),
                glob_pattern="**/*.md",  # 只加载 markdown 文件
                show_progress=True
            )
            print(f"\n成功加载文档，共 {count} 个片段")
            print(f"知识库总文档数: {agent.get_document_count()}")
        except Exception as e:
            print(f"加载文档失败: {e}")
    else:
        print(f"目录不存在: {docs_dir}")
        print("\n创建示例文档...")
        
        # 创建示例文本
        sample_texts = [
            """
            # 项目概述
            
            本项目是一个基于 LangGraph 和码云 AI 的智能 Agent 系统。
            支持多种功能，包括简单对话、工具调用和检索增强生成（RAG）。
            """,
            """
            # 快速开始
            
            ## 安装依赖
            
            ```bash
            pip install -r requirements.txt
            ```
            
            ## 运行示例
            
            ```bash
            python examples/01_simple_chat.py
            ```
            """,
            """
            # RAG 功能
            
            RAG（检索增强生成）是本项目的核心功能之一。
            支持向量检索、关键词检索和混合检索。
            还提供了查询优化、重排序和上下文管理等高级功能。
            """
        ]
        
        agent.add_texts(sample_texts)
        print(f"已添加 {len(sample_texts)} 个示例文档")
        print(f"知识库总文档数: {agent.get_document_count()}")
    
    print()
    
    # 进行查询测试
    print("3. 查询测试...")
    print("-" * 60)
    
    questions = [
        "这个项目有什么功能？",
        "如何快速开始使用？",
        "RAG 功能包括哪些特性？"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n问题 {i}: {question}")
        print("-" * 40)
        
        answer = agent.query(
            question=question,
            top_k=3,
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

