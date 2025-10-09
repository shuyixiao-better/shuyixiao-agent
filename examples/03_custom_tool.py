"""
示例 3: 自定义工具

演示如何创建和注册自定义工具
"""

import sys
import os
import random

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.shuyixiao_agent.agents.tool_agent import ToolAgent
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


# 自定义工具函数
def get_weather(city: str) -> str:
    """
    获取天气信息（模拟）
    
    Args:
        city: 城市名称
        
    Returns:
        天气信息
    """
    weather_conditions = ["晴天", "多云", "阴天", "小雨", "大雨"]
    temp = random.randint(15, 35)
    condition = random.choice(weather_conditions)
    
    return f"{city}的天气: {condition}, 温度 {temp}°C"


def translate_text(text: str, target_language: str = "英文") -> str:
    """
    翻译文本（模拟）
    
    Args:
        text: 要翻译的文本
        target_language: 目标语言
        
    Returns:
        翻译结果
    """
    # 这是一个模拟实现
    # 实际使用时可以调用真实的翻译 API
    translations = {
        "你好": {"英文": "Hello", "日文": "こんにちは", "法文": "Bonjour"},
        "谢谢": {"英文": "Thank you", "日文": "ありがとう", "法文": "Merci"},
    }
    
    if text in translations and target_language in translations[text]:
        return f"'{text}' 翻译为{target_language}: {translations[text][target_language]}"
    else:
        return f"这是一个模拟翻译。实际应用中会调用真实的翻译 API 将 '{text}' 翻译为{target_language}。"


def generate_random_number(min_value: int = 1, max_value: int = 100) -> int:
    """
    生成随机数
    
    Args:
        min_value: 最小值
        max_value: 最大值
        
    Returns:
        随机数
    """
    return random.randint(min_value, max_value)


def main():
    """主函数"""
    print("=" * 60)
    print("示例 3: 自定义工具")
    print("=" * 60)
    print()
    
    # 创建 Tool Agent
    print("正在初始化 Tool Agent...")
    agent = ToolAgent(
        system_message="你是一个有帮助的AI助手，可以使用各种工具来帮助用户。",
        max_iterations=10
    )
    
    # 注册自定义工具
    print("正在注册自定义工具...")
    
    # 1. 天气查询工具
    agent.register_tool(
        name="get_weather",
        func=get_weather,
        description="查询指定城市的天气信息",
        parameters={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，例如 '北京'、'上海'"
                }
            },
            "required": ["city"]
        }
    )
    
    # 2. 翻译工具
    agent.register_tool(
        name="translate_text",
        func=translate_text,
        description="将文本翻译成指定语言",
        parameters={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要翻译的文本"
                },
                "target_language": {
                    "type": "string",
                    "description": "目标语言，例如 '英文'、'日文'、'法文'",
                    "default": "英文"
                }
            },
            "required": ["text"]
        }
    )
    
    # 3. 随机数生成工具
    agent.register_tool(
        name="generate_random_number",
        func=generate_random_number,
        description="生成指定范围内的随机数",
        parameters={
            "type": "object",
            "properties": {
                "min_value": {
                    "type": "integer",
                    "description": "最小值",
                    "default": 1
                },
                "max_value": {
                    "type": "integer",
                    "description": "最大值",
                    "default": 100
                }
            },
            "required": []
        }
    )
    
    print(f"✓ 已注册 {len(agent.tools)} 个自定义工具")
    print("  - get_weather: 查询天气")
    print("  - translate_text: 翻译文本")
    print("  - generate_random_number: 生成随机数")
    print()
    
    # 测试自定义工具
    test_queries = [
        "北京今天天气怎么样？",
        "帮我把'你好'翻译成英文",
        "生成一个 1 到 10 之间的随机数",
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
    print("提示: 你可以尝试以下命令:")
    print("  - '上海的天气如何？'")
    print("  - '翻译：谢谢'")
    print("  - '给我一个随机数'")
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

