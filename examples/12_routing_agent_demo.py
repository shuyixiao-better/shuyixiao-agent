"""
Routing Agent 演示脚本

展示如何使用 Routing Agent 实现智能任务路由和分发。

运行方式：
    python examples/12_routing_agent_demo.py
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.shuyixiao_agent.gitee_ai_client import GiteeAIClient
from src.shuyixiao_agent.agents.routing_agent import (
    RoutingAgent,
    RoutingStrategy,
    RouteConfig,
    SmartAssistantRoutes,
    DeveloperAssistantRoutes
)


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60 + "\n")


def demo_smart_assistant():
    """演示智能助手场景"""
    print_section("演示1: 智能助手路由")
    
    # 初始化
    llm_client = GiteeAIClient()
    agent = RoutingAgent(
        llm_client=llm_client,
        strategy=RoutingStrategy.HYBRID,
        verbose=True
    )
    
    # 注册智能助手路由
    routes = SmartAssistantRoutes.get_routes(llm_client)
    agent.register_routes(routes)
    
    # 测试不同类型的输入
    test_inputs = [
        "帮我写一个Python快速排序函数",
        "翻译：Hello, how are you today?",
        "总结一下这段话的要点：人工智能是...",
        "分析一下当前AI市场的发展趋势",
        "写一篇关于机器学习的博客文章",
        "什么是深度学习？"
    ]
    
    for i, input_text in enumerate(test_inputs, 1):
        print(f"\n【测试 {i}】")
        result = agent.route(input_text)
        
        if result.success:
            print(f"\n✅ 成功路由到: {result.route_name}")
            print(f"📊 置信度: {result.confidence:.2%}")
            print(f"⏱️  执行时间: {result.execution_time:.2f}秒")
            print(f"\n📝 结果预览:\n{result.handler_output[:200]}...\n")
        else:
            print(f"❌ 路由失败: {result.error_message}")
        
        # 暂停一下，避免请求过快
        import time
        time.sleep(1)


def demo_developer_assistant():
    """演示开发者助手场景"""
    print_section("演示2: 开发者助手路由")
    
    # 初始化
    llm_client = GiteeAIClient()
    agent = RoutingAgent(
        llm_client=llm_client,
        strategy=RoutingStrategy.HYBRID,
        verbose=True
    )
    
    # 注册开发者助手路由
    routes = DeveloperAssistantRoutes.get_routes(llm_client)
    agent.register_routes(routes)
    
    # 测试不同类型的开发任务
    test_inputs = [
        "审查这段代码：def add(a, b): return a + b",
        "为什么会报错 NullPointerException？",
        "如何优化这个数据库查询的性能？",
        "设计一个微服务架构的电商系统"
    ]
    
    for i, input_text in enumerate(test_inputs, 1):
        print(f"\n【测试 {i}】")
        result = agent.route(input_text)
        
        if result.success:
            print(f"\n✅ 成功路由到: {result.route_name}")
            print(f"📊 置信度: {result.confidence:.2%}")
            print(f"⏱️  执行时间: {result.execution_time:.2f}秒")
            print(f"\n📝 结果预览:\n{result.handler_output[:200]}...\n")
        else:
            print(f"❌ 路由失败: {result.error_message}")
        
        import time
        time.sleep(1)


def demo_custom_routes():
    """演示自定义路由"""
    print_section("演示3: 自定义路由配置")
    
    llm_client = GiteeAIClient()
    agent = RoutingAgent(
        llm_client=llm_client,
        strategy=RoutingStrategy.HYBRID,
        verbose=True
    )
    
    # 定义自定义处理器
    def greeting_handler(input_text: str, context: dict) -> str:
        """问候语处理器"""
        return "你好！很高兴见到你！有什么我可以帮助的吗？"
    
    def calculation_handler(input_text: str, context: dict) -> str:
        """计算处理器"""
        return f"让我帮你计算一下：{input_text}"
    
    # 注册自定义路由
    agent.register_route(RouteConfig(
        name="greeting",
        description="问候和打招呼",
        handler=greeting_handler,
        keywords=["你好", "hi", "hello", "嗨"],
        pattern=r"^(你好|hi|hello|嗨)",
        priority=10,
        examples=["你好", "hello"]
    ))
    
    agent.register_route(RouteConfig(
        name="calculation",
        description="数学计算",
        handler=calculation_handler,
        keywords=["计算", "算", "多少"],
        pattern=r"(计算|算)\s*[:：]?\s*(.+)",
        priority=9,
        examples=["计算：1+1", "算一下100*5"]
    ))
    
    # 测试自定义路由
    test_inputs = [
        "你好，今天天气不错",
        "计算：123 + 456",
        "hello world",
        "算一下100乘以5"
    ]
    
    for input_text in test_inputs:
        print(f"\n输入: {input_text}")
        result = agent.route(input_text)
        
        if result.success:
            print(f"路由: {result.route_name}")
            print(f"结果: {result.handler_output}")


def demo_strategy_comparison():
    """演示不同路由策略的对比"""
    print_section("演示4: 路由策略对比")
    
    llm_client = GiteeAIClient()
    
    # 测试输入
    test_input = "帮我写一个Python快速排序函数"
    
    strategies = [
        RoutingStrategy.KEYWORD,
        RoutingStrategy.RULE_BASED,
        RoutingStrategy.LLM_BASED,
        RoutingStrategy.HYBRID
    ]
    
    for strategy in strategies:
        print(f"\n{'='*40}")
        print(f"策略: {strategy.value}")
        print(f"{'='*40}\n")
        
        agent = RoutingAgent(
            llm_client=llm_client,
            strategy=strategy,
            verbose=False  # 关闭详细输出以便对比
        )
        
        # 注册路由
        routes = SmartAssistantRoutes.get_routes(llm_client)
        agent.register_routes(routes)
        
        # 执行路由
        result = agent.route(test_input)
        
        if result.success:
            print(f"✅ 路由到: {result.route_name}")
            print(f"📊 置信度: {result.confidence:.2%}")
            print(f"💡 原因: {result.routing_reason}")
            print(f"⏱️  时间: {result.execution_time:.2f}秒")
        else:
            print(f"❌ 失败: {result.error_message}")


def interactive_mode():
    """交互模式"""
    print_section("交互模式")
    
    llm_client = GiteeAIClient()
    
    # 选择场景
    print("请选择场景：")
    print("1. 智能助手")
    print("2. 开发者助手")
    
    choice = input("\n请输入选项 (1/2): ").strip()
    
    agent = RoutingAgent(
        llm_client=llm_client,
        strategy=RoutingStrategy.HYBRID,
        verbose=True
    )
    
    if choice == "1":
        routes = SmartAssistantRoutes.get_routes(llm_client)
        print("\n✓ 已加载智能助手场景")
    elif choice == "2":
        routes = DeveloperAssistantRoutes.get_routes(llm_client)
        print("\n✓ 已加载开发者助手场景")
    else:
        print("\n❌ 无效选项")
        return
    
    agent.register_routes(routes)
    
    print("\n" + "-"*60)
    print("开始交互模式（输入 'quit' 退出）")
    print("-"*60 + "\n")
    
    while True:
        user_input = input("\n你: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q', '退出']:
            print("\n再见！")
            break
        
        if not user_input:
            continue
        
        result = agent.route(user_input)
        
        if result.success:
            print(f"\nAI [{result.route_name}]: {result.handler_output}")
        else:
            print(f"\n❌ 错误: {result.error_message}")


def main():
    """主函数"""
    print("\n" + "🎯"*30)
    print(" " * 20 + "Routing Agent 演示")
    print("🎯"*30 + "\n")
    
    print("请选择演示模式：")
    print("1. 智能助手路由演示")
    print("2. 开发者助手路由演示")
    print("3. 自定义路由演示")
    print("4. 策略对比演示")
    print("5. 交互模式")
    print("0. 运行所有演示")
    
    choice = input("\n请输入选项: ").strip()
    
    if choice == "1":
        demo_smart_assistant()
    elif choice == "2":
        demo_developer_assistant()
    elif choice == "3":
        demo_custom_routes()
    elif choice == "4":
        demo_strategy_comparison()
    elif choice == "5":
        interactive_mode()
    elif choice == "0":
        demo_smart_assistant()
        demo_developer_assistant()
        demo_custom_routes()
        demo_strategy_comparison()
    else:
        print("\n❌ 无效选项")
        return
    
    print("\n" + "="*60)
    print("演示完成！")
    print("="*60 + "\n")
    
    print("💡 提示：")
    print("  - 可以通过 Web 界面使用 Routing Agent")
    print("  - 运行: python run_web.py")
    print("  - 访问: http://localhost:8001")
    print("  - 点击 '🎯 Routing Agent' 标签页\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

