"""
完整工具集演示

展示如何使用所有13个内置工具
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.shuyixiao_agent.agents.tool_agent import ToolAgent
from src.shuyixiao_agent.tools import get_basic_tools


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()
    
    print("=" * 60)
    print("完整工具集演示")
    print("=" * 60)
    
    # 创建工具 Agent
    agent = ToolAgent(
        system_message="你是一个有帮助的AI助手。你可以使用多种工具来完成任务，包括时间查询、数学计算、编码解码、质数检查等。"
    )
    
    # 批量注册所有基础工具
    print("\n📦 正在注册工具...")
    tools = get_basic_tools()
    for tool in tools:
        agent.register_tool(
            name=tool["name"],
            func=tool["func"],
            description=tool["description"],
            parameters=tool["parameters"]
        )
    print(f"✅ 已注册 {len(tools)} 个工具\n")
    
    # 测试用例列表
    test_cases = [
        "现在几点了？",
        "帮我计算 (15 + 25) * 3",
        "生成一个1到100之间的随机数",
        "25摄氏度等于多少华氏度？",
        "反转字符串 'Python'",
        "统计这段文本的字数：Hello World! This is a test.",
        "2025-12-25是星期几？",
        "1995-06-15出生的人现在多大了？",
        "生成一个UUID",
        "对文本 'Hello World' 进行base64编码",
        "97是质数吗？"
    ]
    
    # 运行测试用例
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}/{len(test_cases)}")
        print(f"{'='*60}")
        print(f"❓ 问题: {test}")
        print(f"\n💭 AI正在思考...\n")
        
        try:
            response = agent.run(test)
            print(f"✅ 回答: {response}")
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
    
    print(f"\n{'='*60}")
    print("演示完成！")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

