"""
示例 1: 简单对话

演示如何使用 SimpleAgent 进行基础的对话交互
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.shuyixiao_agent import SimpleAgent
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def main():
    """主函数"""
    print("=" * 60)
    print("示例 1: 简单对话 Agent")
    print("=" * 60)
    print()
    
    # 创建 Agent
    print("正在初始化 Agent...")
    agent = SimpleAgent(
        system_message="你是一个友好、专业的AI助手，擅长回答各种问题。"
    )
    print("✓ Agent 初始化完成")
    print()
    
    # 测试对话
    test_questions = [
        "你好！请介绍一下你自己。",
        "什么是人工智能？",
        "Python 语言有哪些特点？",
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"问题 {i}: {question}")
        print("-" * 60)
        
        response = agent.chat(question)
        print(f"回答: {response}")
        print()
    
    # 交互式对话
    print("=" * 60)
    print("进入交互模式（输入 'quit' 或 'exit' 退出）")
    print("=" * 60)
    print()
    
    while True:
        try:
            user_input = input("你: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break
            
            if not user_input:
                continue
            
            response = agent.chat(user_input)
            print(f"Agent: {response}")
            print()
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"错误: {str(e)}")
            print()


if __name__ == "__main__":
    main()

