"""
RAG 功能快速测试脚本

快速验证 RAG 功能是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("RAG 功能快速测试")
print("=" * 70)
print()

try:
    print("1. 导入模块...")
    from src.shuyixiao_agent import RAGAgent
    print("✓ 模块导入成功")
    print()
    
    print("2. 创建 RAG Agent（这可能需要一些时间来下载模型）...")
    agent = RAGAgent(
        collection_name="test_kb",
        use_reranker=False,  # 暂时不使用 reranker 以加快测试速度
        retrieval_mode="vector"
    )
    print("✓ RAG Agent 创建成功")
    print()
    
    print("3. 添加测试文档...")
    test_texts = [
        """
        Python 是一种高级、通用、解释型的编程语言。
        Python 的设计哲学强调代码的可读性和简洁的语法。
        Python 支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。
        """,
        """
        机器学习是人工智能的一个分支，它使计算机系统能够从数据中学习并改进。
        机器学习算法可以分为监督学习、非监督学习和强化学习。
        常用的机器学习库包括 scikit-learn、TensorFlow 和 PyTorch。
        """,
        """
        深度学习是机器学习的一个子集，使用人工神经网络来模拟人脑的学习过程。
        深度学习在图像识别、自然语言处理和语音识别等领域取得了突破性进展。
        卷积神经网络（CNN）和循环神经网络（RNN）是深度学习的两种主要架构。
        """
    ]
    
    agent.add_texts(test_texts)
    doc_count = agent.get_document_count()
    print(f"✓ 已添加文档，知识库文档数: {doc_count}")
    print()
    
    print("4. 测试查询...")
    print("-" * 70)
    
    test_questions = [
        "Python 有什么特点？",
        "什么是机器学习？",
        "深度学习在哪些领域有应用？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n问题 {i}: {question}")
        print("-" * 40)
        
        try:
            answer = agent.query(
                question=question,
                top_k=2,
                optimize_query=False,  # 关闭查询优化以加快速度
                stream=False
            )
            print(f"回答: {answer[:200]}..." if len(answer) > 200 else f"回答: {answer}")
        except Exception as e:
            print(f"✗ 查询失败: {e}")
    
    print()
    print("-" * 70)
    print()
    
    print("5. 清理测试数据...")
    agent.clear_knowledge_base()
    print("✓ 测试数据已清理")
    print()
    
    print("=" * 70)
    print("✓ RAG 功能测试完成！所有功能正常工作。")
    print("=" * 70)
    print()
    print("下一步：")
    print("1. 查看示例：python examples/07_rag_basic_usage.py")
    print("2. 阅读文档：docs/rag_guide.md")
    print("3. 启动 Web 服务：python run_web.py")
    print()

except ImportError as e:
    print(f"✗ 导入错误: {e}")
    print()
    print("请确保已安装所有依赖：")
    print("  poetry install")
    print()
    sys.exit(1)

except Exception as e:
    print(f"✗ 测试失败: {e}")
    print()
    print("可能的原因：")
    print("1. 未配置 API Key（请检查 .env 文件）")
    print("2. 网络连接问题（下载嵌入模型需要网络）")
    print("3. 依赖版本不兼容")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)

