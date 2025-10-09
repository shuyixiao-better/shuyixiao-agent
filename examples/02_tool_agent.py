"""
示例 2: 带工具的 Agent

演示如何使用 ToolAgent 以及如何注册和使用工具
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.shuyixiao_agent.agents.tool_agent import ToolAgent
from src.shuyixiao_agent.tools.basic_tools import (
    get_current_time,
    calculate,
    search_wikipedia,
    TOOL_DEFINITIONS
)
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def main():
    """主函数"""
    print("=" * 60)
    print("示例 2: 带工具调用的 Agent")
    print("=" * 60)
    print()
    
    # 创建 Tool Agent
    print("正在初始化 Tool Agent...")
    agent = ToolAgent(
        system_message="你是一个有帮助的AI助手。你可以使用提供的工具来帮助用户完成任务。",
        max_iterations=10
    )
    
    # 注册工具
    print("正在注册工具...")
    agent.register_tool(
        name="get_current_time",
        func=get_current_time,
        description=TOOL_DEFINITIONS["get_current_time"]["description"],
        parameters=TOOL_DEFINITIONS["get_current_time"]["parameters"]
    )
    
    agent.register_tool(
        name="calculate",
        func=calculate,
        description=TOOL_DEFINITIONS["calculate"]["description"],
        parameters=TOOL_DEFINITIONS["calculate"]["parameters"]
    )
    
    agent.register_tool(
        name="search_wikipedia",
        func=search_wikipedia,
        description=TOOL_DEFINITIONS["search_wikipedia"]["description"],
        parameters=TOOL_DEFINITIONS["search_wikipedia"]["parameters"]
    )
    
    print(f"✓ 已注册 {len(agent.tools)} 个工具")
    print("  - get_current_time: 获取当前时间")
    print("  - calculate: 计算数学表达式")
    print("  - search_wikipedia: 搜索维基百科")
    print()
    
    # 测试工具调用
    test_queries = [
        "现在几点了？",
        "帮我计算 123 * 456 + 789",
        "搜索一下人工智能的相关信息",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"查询 {i}: {query}")
        print("-" * 60)
        
        try:
            response = agent.run(query)
            print(f"回答: {response}")
        except Exception as e:
            print(f"错误: {str(e)}")
        
        print()
    
    # 交互式模式
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
            
            response = agent.run(user_input)
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

