"""
示例 4: 直接使用 API 客户端

演示如何直接使用码云 AI API 客户端进行调用
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.shuyixiao_agent import GiteeAIClient
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def example_simple_chat():
    """示例：简单对话"""
    print("=" * 60)
    print("示例 4.1: 简单对话")
    print("=" * 60)
    print()
    
    client = GiteeAIClient()
    
    response = client.simple_chat(
        user_message="什么是 LangGraph？",
        system_message="你是一个AI技术专家。"
    )
    
    print(f"问题: 什么是 LangGraph？")
    print(f"回答: {response}")
    print()


def example_multi_turn_chat():
    """示例：多轮对话"""
    print("=" * 60)
    print("示例 4.2: 多轮对话")
    print("=" * 60)
    print()
    
    client = GiteeAIClient()
    
    messages = [
        {"role": "system", "content": "你是一个有帮助的编程助手。"},
        {"role": "user", "content": "Python 中如何创建一个列表？"},
    ]
    
    # 第一轮
    response = client.chat_completion(messages=messages)
    ai_response = response["choices"][0]["message"]["content"]
    
    print("用户: Python 中如何创建一个列表？")
    print(f"AI: {ai_response}")
    print()
    
    # 第二轮
    messages.append({"role": "assistant", "content": ai_response})
    messages.append({"role": "user", "content": "那列表推导式呢？"})
    
    response = client.chat_completion(messages=messages)
    ai_response = response["choices"][0]["message"]["content"]
    
    print("用户: 那列表推导式呢？")
    print(f"AI: {ai_response}")
    print()


def example_with_parameters():
    """示例：使用不同的参数"""
    print("=" * 60)
    print("示例 4.3: 调整参数")
    print("=" * 60)
    print()
    
    client = GiteeAIClient()
    
    messages = [
        {"role": "user", "content": "写一个简短的科幻故事开头"}
    ]
    
    # 低温度（更确定性）
    print("低温度 (temperature=0.3) - 更确定性的输出:")
    response = client.chat_completion(
        messages=messages,
        temperature=0.3,
        max_tokens=100
    )
    print(response["choices"][0]["message"]["content"])
    print()
    
    # 高温度（更随机）
    print("高温度 (temperature=1.5) - 更有创造性的输出:")
    response = client.chat_completion(
        messages=messages,
        temperature=1.5,
        max_tokens=100
    )
    print(response["choices"][0]["message"]["content"])
    print()


def example_response_details():
    """示例：查看响应详情"""
    print("=" * 60)
    print("示例 4.4: API 响应详情")
    print("=" * 60)
    print()
    
    client = GiteeAIClient()
    
    response = client.chat_completion(
        messages=[{"role": "user", "content": "你好"}]
    )
    
    print("完整的 API 响应:")
    print("-" * 60)
    
    # 打印响应的关键信息
    print(f"ID: {response.get('id', 'N/A')}")
    print(f"模型: {response.get('model', 'N/A')}")
    print(f"创建时间: {response.get('created', 'N/A')}")
    
    if 'usage' in response:
        usage = response['usage']
        print(f"\nToken 使用情况:")
        print(f"  - 提示词 tokens: {usage.get('prompt_tokens', 0)}")
        print(f"  - 生成 tokens: {usage.get('completion_tokens', 0)}")
        print(f"  - 总计 tokens: {usage.get('total_tokens', 0)}")
    
    choice = response['choices'][0]
    print(f"\n回复内容: {choice['message']['content']}")
    print(f"完成原因: {choice.get('finish_reason', 'N/A')}")
    print()


def main():
    """主函数"""
    print("=" * 60)
    print("码云 AI API 客户端使用示例")
    print("=" * 60)
    print()
    
    try:
        # 运行各个示例
        example_simple_chat()
        example_multi_turn_chat()
        example_with_parameters()
        example_response_details()
        
        print("=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"错误: {str(e)}")
        print("\n请确保：")
        print("1. 已在 .env 文件中设置 GITEE_AI_API_KEY")
        print("2. API Key 是有效的")
        print("3. 已购买相应的模型资源包")


if __name__ == "__main__":
    main()

