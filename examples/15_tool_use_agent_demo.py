#!/usr/bin/env python3
"""
Tool Use Agent 演示程序

展示如何使用 Tool Use Agent 来智能选择和执行工具完成各种任务。

运行方式:
    python examples/15_tool_use_agent_demo.py

功能特性:
- 🔧 智能工具选择：自动分析需求并选择最合适的工具
- ⚡ 高效执行：支持同步和异步工具执行
- 📊 执行追踪：详细记录每个工具的执行过程和结果
- 🔄 链式调用：支持多个工具协作完成复杂任务
- 🛠️ 丰富工具库：内置20+常用工具，覆盖多个领域
- 📈 统计分析：提供工具使用统计和性能分析
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.shuyixiao_agent.gitee_ai_client import GiteeAIClient
from src.shuyixiao_agent.agents.tool_use_agent import ToolUseAgent, ToolType
from src.shuyixiao_agent.tools.predefined_tools import PredefinedToolsRegistry


def print_header(title: str):
    """打印标题"""
    print("\n" + "="*60)
    print(f"🔧 {title}")
    print("="*60)


def print_section(title: str):
    """打印章节标题"""
    print(f"\n📋 {title}")
    print("-" * 40)


def print_result(result: dict):
    """打印执行结果"""
    if result["success"]:
        print(f"✅ 执行成功！")
        print(f"📊 总轮次: {result.get('total_iterations', 0)}")
        print(f"🛠️ 使用工具: {len(result.get('results', []))}")
        
        print("\n📋 执行步骤:")
        for i, step in enumerate(result.get('results', []), 1):
            status = "✅" if step['success'] else "❌"
            print(f"  {status} 步骤{i}: {step['tool_name']}")
            print(f"     推理: {step.get('reasoning', '自动选择')}")
            print(f"     耗时: {step.get('execution_time', 0):.2f}s")
            if step['success']:
                result_text = str(step['result'])[:100]
                print(f"     结果: {result_text}{'...' if len(str(step['result'])) > 100 else ''}")
            else:
                print(f"     错误: {step.get('error_message', '未知错误')}")
    else:
        print(f"❌ 执行失败: {result.get('message', '未知错误')}")


async def demo_basic_usage():
    """基础使用演示"""
    print_header("Tool Use Agent 基础使用演示")
    
    # 初始化客户端和智能体
    llm_client = GiteeAIClient()
    agent = ToolUseAgent(llm_client=llm_client, verbose=True)
    
    # 注册所有预定义工具
    PredefinedToolsRegistry.register_all_tools(agent)
    
    print(f"✅ 已注册 {len(agent.tools)} 个工具")
    
    # 演示任务列表
    demo_tasks = [
        {
            "name": "文件操作",
            "task": "读取当前目录下的README.md文件内容",
            "description": "演示文件读取功能"
        },
        {
            "name": "数学计算",
            "task": "计算 2^10 + sqrt(144) - 5*3 的值",
            "description": "演示数学计算功能"
        },
        {
            "name": "系统信息",
            "task": "获取当前系统的CPU和内存使用情况",
            "description": "演示系统监控功能"
        },
        {
            "name": "文本处理",
            "task": "分析这段文本的统计信息：'Hello world! This is a test message with multiple sentences. How many words and sentences are there?'",
            "description": "演示文本分析功能"
        },
        {
            "name": "单位转换",
            "task": "将100摄氏度转换为华氏度",
            "description": "演示单位转换功能"
        }
    ]
    
    for i, demo in enumerate(demo_tasks, 1):
        print_section(f"演示 {i}: {demo['name']}")
        print(f"📝 任务: {demo['task']}")
        print(f"💡 说明: {demo['description']}")
        
        try:
            result = await agent.process_request(demo['task'], max_iterations=3)
            print_result(result)
        except Exception as e:
            print(f"❌ 执行失败: {e}")
        
        input("\n按回车键继续下一个演示...")


async def demo_complex_tasks():
    """复杂任务演示"""
    print_header("复杂任务链式执行演示")
    
    llm_client = GiteeAIClient()
    agent = ToolUseAgent(llm_client=llm_client, verbose=True)
    PredefinedToolsRegistry.register_all_tools(agent)
    
    complex_tasks = [
        {
            "name": "数据分析流程",
            "task": "创建一个包含学生成绩的JSON文件，然后分析数据并计算平均分",
            "description": "演示文件创建 → 数据处理 → 统计计算的完整流程"
        },
        {
            "name": "系统监控报告",
            "task": "获取系统信息、CPU使用率和内存信息，然后生成一个监控报告",
            "description": "演示多个系统工具的协作使用"
        },
        {
            "name": "文本处理管道",
            "task": "分析一段英文文本的统计信息，然后计算其MD5哈希值",
            "description": "演示文本分析 → 哈希计算的处理管道"
        }
    ]
    
    for i, demo in enumerate(complex_tasks, 1):
        print_section(f"复杂任务 {i}: {demo['name']}")
        print(f"📝 任务: {demo['task']}")
        print(f"💡 说明: {demo['description']}")
        
        try:
            result = await agent.process_request(demo['task'], max_iterations=5)
            print_result(result)
        except Exception as e:
            print(f"❌ 执行失败: {e}")
        
        input("\n按回车键继续下一个演示...")


async def demo_tool_types():
    """工具类型演示"""
    print_header("不同类型工具演示")
    
    llm_client = GiteeAIClient()
    agent = ToolUseAgent(llm_client=llm_client, verbose=True)
    PredefinedToolsRegistry.register_all_tools(agent)
    
    # 按工具类型分组演示
    tool_type_demos = {
        ToolType.FILE_OPERATION: [
            "列出当前目录的所有文件",
            "检查README.md文件是否存在"
        ],
        ToolType.NETWORK_REQUEST: [
            "检查百度网站的连通性",
            "获取httpbin.org/json的API数据"
        ],
        ToolType.DATA_PROCESSING: [
            "解析这个JSON: {'name': 'Alice', 'age': 30, 'city': 'Beijing'}",
            "过滤数据：从 [{'name': 'Alice', 'score': 85}, {'name': 'Bob', 'score': 92}] 中找出分数大于90的"
        ],
        ToolType.SYSTEM_INFO: [
            "获取系统基本信息",
            "查看磁盘使用情况"
        ],
        ToolType.CALCULATION: [
            "计算数列 [1,2,3,4,5,6,7,8,9,10] 的平均值和标准差",
            "将50公里转换为英里"
        ],
        ToolType.TEXT_PROCESSING: [
            "计算文本 'Hello World' 的SHA256哈希值",
            "将文本 'hello world' 转换为大写"
        ]
    }
    
    for tool_type, tasks in tool_type_demos.items():
        print_section(f"{tool_type.value} 工具演示")
        
        # 获取该类型的工具列表
        tools = agent.get_available_tools(tool_type=tool_type)
        print(f"📊 该类型包含 {len(tools)} 个工具:")
        for tool in tools[:3]:  # 只显示前3个
            print(f"  • {tool['name']}: {tool['description']}")
        
        for i, task in enumerate(tasks, 1):
            print(f"\n🔧 任务 {i}: {task}")
            try:
                result = await agent.process_request(task, max_iterations=2)
                if result["success"] and result.get("results"):
                    last_result = result["results"][-1]
                    print(f"✅ 使用工具: {last_result['tool_name']}")
                    result_text = str(last_result['result'])[:100]
                    print(f"📊 结果: {result_text}{'...' if len(str(last_result['result'])) > 100 else ''}")
                else:
                    print(f"❌ 失败: {result.get('message', '未知错误')}")
            except Exception as e:
                print(f"❌ 执行失败: {e}")
        
        input("\n按回车键继续下一类型工具演示...")


async def demo_statistics():
    """统计信息演示"""
    print_header("工具使用统计演示")
    
    llm_client = GiteeAIClient()
    agent = ToolUseAgent(llm_client=llm_client, verbose=True)
    PredefinedToolsRegistry.register_all_tools(agent)
    
    # 执行一些任务来生成统计数据
    test_tasks = [
        "计算 1+1",
        "获取系统信息",
        "分析文本 'test' 的长度",
        "将10米转换为厘米",
        "计算数列 [1,2,3] 的平均值"
    ]
    
    print("🔄 执行测试任务以生成统计数据...")
    for task in test_tasks:
        try:
            await agent.process_request(task, max_iterations=2)
        except:
            pass  # 忽略错误，继续执行
    
    # 显示统计信息
    print_section("执行统计")
    stats = agent.get_tool_statistics()
    
    print(f"📊 总执行次数: {stats['total_executions']}")
    print(f"✅ 成功次数: {stats['successful_executions']}")
    print(f"❌ 失败次数: {stats['failed_executions']}")
    print(f"⏱️ 平均执行时间: {stats['average_execution_time']:.2f}s")
    
    if stats['most_used_tools']:
        print("\n🏆 最常用工具:")
        for tool_name, count in stats['most_used_tools']:
            print(f"  • {tool_name}: {count}次")
    
    # 显示执行历史
    print_section("执行历史")
    history = agent.get_execution_history()
    print(f"📋 历史记录数: {len(history)}")
    
    if history:
        print("\n最近5次执行:")
        for record in history[-5:]:
            status = "✅" if record['success'] else "❌"
            print(f"  {status} {record['tool_name']} - {record['timestamp']}")


async def interactive_demo():
    """交互式演示"""
    print_header("交互式 Tool Use Agent")
    
    llm_client = GiteeAIClient()
    agent = ToolUseAgent(llm_client=llm_client, verbose=True)
    PredefinedToolsRegistry.register_all_tools(agent)
    
    print("🎯 欢迎使用 Tool Use Agent 交互模式！")
    print("💡 您可以输入任何任务，系统会自动选择合适的工具来完成。")
    print("📝 输入 'help' 查看示例，输入 'quit' 退出。")
    
    while True:
        try:
            user_input = input("\n🔧 请输入任务: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            if user_input.lower() == 'help':
                print("\n💡 示例任务:")
                examples = [
                    "读取某个文件的内容",
                    "计算数学表达式",
                    "获取系统信息",
                    "分析文本统计",
                    "转换单位",
                    "发送HTTP请求",
                    "处理JSON数据"
                ]
                for example in examples:
                    print(f"  • {example}")
                continue
            
            if user_input.lower() == 'stats':
                stats = agent.get_tool_statistics()
                print(f"\n📊 统计信息:")
                print(f"  总执行: {stats['total_executions']}")
                print(f"  成功: {stats['successful_executions']}")
                print(f"  失败: {stats['failed_executions']}")
                continue
            
            print(f"\n🔄 正在处理: {user_input}")
            result = await agent.process_request(user_input, max_iterations=5)
            print_result(result)
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 处理失败: {e}")


async def main():
    """主函数"""
    print_header("Tool Use Agent 完整演示程序")
    
    print("🎯 本演示将展示 Tool Use Agent 的各种功能:")
    print("  1. 基础工具使用")
    print("  2. 复杂任务链式执行")
    print("  3. 不同类型工具演示")
    print("  4. 统计信息展示")
    print("  5. 交互式体验")
    
    demos = [
        ("1", "基础使用演示", demo_basic_usage),
        ("2", "复杂任务演示", demo_complex_tasks),
        ("3", "工具类型演示", demo_tool_types),
        ("4", "统计信息演示", demo_statistics),
        ("5", "交互式演示", interactive_demo),
    ]
    
    while True:
        print("\n" + "="*50)
        print("📋 请选择演示:")
        for code, name, _ in demos:
            print(f"  {code}. {name}")
        print("  0. 退出程序")
        
        choice = input("\n请输入选项 (0-5): ").strip()
        
        if choice == "0":
            print("👋 感谢使用 Tool Use Agent 演示程序！")
            break
        
        # 查找对应的演示
        demo_func = None
        for code, name, func in demos:
            if choice == code:
                demo_func = func
                break
        
        if demo_func:
            try:
                await demo_func()
            except KeyboardInterrupt:
                print("\n⏹️ 演示被中断")
            except Exception as e:
                print(f"❌ 演示执行失败: {e}")
        else:
            print("❌ 无效选项，请重新选择")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序被中断，再见！")
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
