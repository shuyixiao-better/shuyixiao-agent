#!/usr/bin/env python3
"""
Planning Agent 演示脚本

展示如何使用 Planning Agent 进行智能规划和任务执行。
Planning Agent 基于 Agentic Design Patterns 的 Planning 设计模式实现。

运行方式：
    python examples/16_planning_agent_demo.py

功能特性：
- 🎯 智能目标分解：将复杂目标分解为可执行的子任务
- 📋 多种规划策略：支持顺序、并行、依赖关系和自适应执行
- 🔄 动态调整：根据执行情况动态调整计划
- 📊 进度监控：实时跟踪任务执行进度
- 🎨 预定义场景：提供软件开发、研究、产品发布等场景模板
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from typing import Dict, Any

from src.shuyixiao_agent.gitee_ai_client import GiteeAIClient
from src.shuyixiao_agent.agents.planning_agent import (
    PlanningAgent,
    PlanningStrategy,
    TaskStatus,
    TaskPriority,
    ProjectPlanningScenarios,
    PlanningTaskHandlers
)


def print_banner():
    """打印横幅"""
    print("=" * 80)
    print("🎯 Planning Agent 演示")
    print("基于 Agentic Design Patterns 的智能规划系统")
    print("=" * 80)
    print()


def print_section(title: str):
    """打印章节标题"""
    print(f"\n{'=' * 60}")
    print(f"📋 {title}")
    print("=" * 60)


def print_subsection(title: str):
    """打印子章节标题"""
    print(f"\n{'-' * 40}")
    print(f"🔹 {title}")
    print("-" * 40)


def print_task_info(task):
    """打印任务信息"""
    status_emoji = {
        TaskStatus.PENDING: "⏳",
        TaskStatus.IN_PROGRESS: "🔄",
        TaskStatus.COMPLETED: "✅",
        TaskStatus.FAILED: "❌",
        TaskStatus.BLOCKED: "🚫",
        TaskStatus.CANCELLED: "⏹️"
    }
    
    priority_emoji = {
        TaskPriority.LOW: "🟢",
        TaskPriority.MEDIUM: "🟡",
        TaskPriority.HIGH: "🟠",
        TaskPriority.CRITICAL: "🔴"
    }
    
    print(f"  {status_emoji.get(task.status, '❓')} {task.name}")
    print(f"     描述: {task.description}")
    print(f"     优先级: {priority_emoji.get(task.priority, '❓')} {task.priority.name}")
    print(f"     预估时间: {task.estimated_duration // 60} 分钟")
    if task.dependencies:
        print(f"     依赖: {', '.join(task.dependencies)}")
    if task.progress > 0:
        print(f"     进度: {task.progress:.1%}")
    print()


def progress_callback(progress: float, current_task):
    """进度回调函数"""
    print(f"📊 执行进度: {progress:.1%} | 当前任务: {current_task.name if current_task else '无'}")


async def demo_basic_planning():
    """演示基本规划功能"""
    print_section("基本规划功能演示")
    
    # 初始化客户端和Agent
    llm_client = GiteeAIClient()
    agent = PlanningAgent(
        llm_client=llm_client,
        strategy=PlanningStrategy.ADAPTIVE,
        verbose=True
    )
    
    # 注册任务处理器
    PlanningTaskHandlers.register_all_handlers(agent)
    
    print("🤖 Planning Agent 已初始化")
    print(f"📋 默认策略: {agent.strategy.value}")
    print(f"🔧 已注册 {len(agent.task_handlers)} 个任务处理器")
    
    # 创建自定义规划
    print_subsection("创建自定义规划")
    goal = "开发一个简单的待办事项管理应用"
    print(f"🎯 目标: {goal}")
    
    result = agent.create_plan_from_goal(goal)
    
    if result.success:
        plan = result.plan
        print(f"✅ 规划创建成功!")
        print(f"📋 计划名称: {plan.name}")
        print(f"📝 计划描述: {plan.description}")
        print(f"🎯 执行策略: {plan.strategy.value}")
        print(f"📊 任务数量: {len(plan.tasks)}")
        
        print("\n📋 任务列表:")
        for i, task in enumerate(plan.tasks, 1):
            print(f"{i}. {task.name}")
            print(f"   描述: {task.description}")
            print(f"   预估: {task.estimated_duration // 60} 分钟")
            if task.dependencies:
                print(f"   依赖: {', '.join(task.dependencies)}")
        
        # 执行计划
        print_subsection("执行规划")
        print("🚀 开始执行计划...")
        
        execution_result = agent.execute_plan(plan.id, progress_callback)
        
        if execution_result.success:
            print(f"✅ 计划执行完成!")
            print(f"⏱️ 总耗时: {execution_result.total_duration} 秒")
            print(f"✅ 完成任务: {execution_result.completed_tasks}")
            print(f"❌ 失败任务: {execution_result.failed_tasks}")
        else:
            print(f"❌ 计划执行失败: {execution_result.error_message}")
    else:
        print(f"❌ 规划创建失败: {result.error_message}")


async def demo_predefined_scenarios():
    """演示预定义场景"""
    print_section("预定义场景演示")
    
    # 初始化客户端和Agent
    llm_client = GiteeAIClient()
    agent = PlanningAgent(
        llm_client=llm_client,
        strategy=PlanningStrategy.DEPENDENCY_BASED,
        verbose=True
    )
    
    # 注册任务处理器
    PlanningTaskHandlers.register_all_handlers(agent)
    
    # 获取所有预定义场景
    scenarios = ProjectPlanningScenarios.get_all_scenarios(llm_client)
    
    print(f"📦 可用场景数量: {len(scenarios)}")
    
    for scenario_id, scenario_data in scenarios.items():
        print(f"\n🎯 {scenario_data['name']}")
        print(f"   描述: {scenario_data['description']}")
        print(f"   策略: {scenario_data['strategy']}")
        print(f"   任务数: {len(scenario_data['template_tasks'])}")
        
        # 计算总预估时间
        total_hours = sum(task['estimated_duration'] for task in scenario_data['template_tasks']) // 3600
        print(f"   预估时间: {total_hours} 小时")
    
    # 演示软件开发场景
    print_subsection("软件开发项目场景演示")
    
    scenario_data = scenarios['software_development']
    goal = "开发一个在线图书管理系统"
    
    print(f"🎯 目标: {goal}")
    print(f"📋 使用场景: {scenario_data['name']}")
    
    # 创建基于场景的计划
    from src.shuyixiao_agent.agents.planning_agent import ExecutionPlan, Task
    
    plan_id = f"plan_{int(time.time())}"
    plan = ExecutionPlan(
        id=plan_id,
        name=f"{scenario_data['name']} - {goal}",
        description=f"基于 {scenario_data['description']} 为目标 '{goal}' 创建的计划",
        strategy=PlanningStrategy(scenario_data['strategy'])
    )
    
    # 创建任务
    for task_data in scenario_data['template_tasks']:
        task = Task(
            id=task_data['id'],
            name=task_data['name'],
            description=task_data['description'],
            priority=TaskPriority(task_data['priority']),
            estimated_duration=task_data['estimated_duration'],
            dependencies=task_data.get('dependencies', []),
            metadata=task_data.get('metadata', {})
        )
        
        # 设置任务处理器
        task_type = task_data.get('task_type', 'default')
        if task_type in agent.task_handlers:
            task.handler = agent.task_handlers[task_type]
        else:
            task.handler = agent._default_task_handler
        
        plan.add_task(task)
    
    # 保存计划
    agent.plans[plan.id] = plan
    
    print(f"✅ 基于场景创建计划成功!")
    print(f"📋 计划名称: {plan.name}")
    print(f"📊 任务数量: {len(plan.tasks)}")
    
    print("\n📋 详细任务列表:")
    for task in plan.tasks:
        print_task_info(task)
    
    # 执行部分任务作为演示
    print_subsection("执行前3个任务（演示）")
    
    # 只执行前3个任务作为演示
    demo_tasks = plan.tasks[:3]
    for task in demo_tasks:
        print(f"🔄 执行任务: {task.name}")
        task.status = TaskStatus.IN_PROGRESS
        
        # 模拟执行
        await asyncio.sleep(1)  # 模拟执行时间
        
        try:
            if task.handler:
                task.result = task.handler(task)
            else:
                task.result = agent._default_task_handler(task)
            
            task.status = TaskStatus.COMPLETED
            task.progress = 1.0
            print(f"✅ 任务完成: {task.name}")
            print(f"   结果: {task.result}")
        except Exception as e:
            task.status = TaskStatus.FAILED
            print(f"❌ 任务失败: {task.name} - {str(e)}")
        
        print()


async def demo_different_strategies():
    """演示不同的规划策略"""
    print_section("不同规划策略演示")
    
    llm_client = GiteeAIClient()
    
    strategies = [
        (PlanningStrategy.SEQUENTIAL, "顺序执行"),
        (PlanningStrategy.PARALLEL, "并行执行"),
        (PlanningStrategy.DEPENDENCY_BASED, "依赖关系"),
        (PlanningStrategy.ADAPTIVE, "自适应")
    ]
    
    goal = "组织一次团队建设活动"
    
    for strategy, strategy_name in strategies:
        print_subsection(f"{strategy_name}策略")
        
        agent = PlanningAgent(
            llm_client=llm_client,
            strategy=strategy,
            verbose=False  # 减少输出
        )
        
        PlanningTaskHandlers.register_all_handlers(agent)
        
        print(f"🎯 目标: {goal}")
        print(f"📋 策略: {strategy_name} ({strategy.value})")
        
        result = agent.create_plan_from_goal(goal)
        
        if result.success:
            plan = result.plan
            print(f"✅ 规划创建成功")
            print(f"📊 任务数量: {len(plan.tasks)}")
            print(f"⏱️ 预估总时间: {sum(task.estimated_duration for task in plan.tasks) // 60} 分钟")
            
            # 显示任务依赖关系
            has_dependencies = any(task.dependencies for task in plan.tasks)
            if has_dependencies:
                print("🔗 任务依赖关系:")
                for task in plan.tasks:
                    if task.dependencies:
                        print(f"   {task.name} 依赖: {', '.join(task.dependencies)}")
            else:
                print("🔗 无任务依赖关系")
        else:
            print(f"❌ 规划创建失败: {result.error_message}")
        
        print()


async def demo_plan_management():
    """演示计划管理功能"""
    print_section("计划管理功能演示")
    
    llm_client = GiteeAIClient()
    agent = PlanningAgent(
        llm_client=llm_client,
        strategy=PlanningStrategy.ADAPTIVE,
        verbose=True
    )
    
    PlanningTaskHandlers.register_all_handlers(agent)
    
    # 创建多个计划
    goals = [
        "学习Python机器学习",
        "开发个人博客网站",
        "准备技术分享演讲"
    ]
    
    print_subsection("创建多个计划")
    
    plan_ids = []
    for i, goal in enumerate(goals, 1):
        print(f"📋 创建计划 {i}: {goal}")
        result = agent.create_plan_from_goal(goal)
        
        if result.success:
            plan_ids.append(result.plan.id)
            print(f"✅ 计划创建成功，ID: {result.plan.id}")
        else:
            print(f"❌ 计划创建失败: {result.error_message}")
    
    # 列出所有计划
    print_subsection("计划列表管理")
    
    all_plans = agent.list_plans()
    print(f"📊 当前计划总数: {len(all_plans)}")
    
    for i, plan in enumerate(all_plans, 1):
        print(f"\n{i}. {plan.name}")
        print(f"   ID: {plan.id}")
        print(f"   描述: {plan.description}")
        print(f"   状态: {plan.status.value}")
        print(f"   进度: {plan.progress:.1%}")
        print(f"   任务数: {len(plan.tasks)}")
        print(f"   创建时间: {plan.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取特定计划详情
    if plan_ids:
        print_subsection("计划详情查看")
        
        first_plan_id = plan_ids[0]
        plan = agent.get_plan(first_plan_id)
        
        if plan:
            print(f"📋 计划详情: {plan.name}")
            print(f"🎯 执行策略: {plan.strategy.value}")
            print(f"📊 总体进度: {plan.progress:.1%}")
            
            print("\n📝 任务详情:")
            for task in plan.tasks:
                print_task_info(task)
        
        # 删除一个计划作为演示
        print_subsection("计划删除")
        
        if len(plan_ids) > 1:
            delete_plan_id = plan_ids[-1]
            success = agent.delete_plan(delete_plan_id)
            
            if success:
                print(f"✅ 成功删除计划: {delete_plan_id}")
                print(f"📊 剩余计划数: {len(agent.list_plans())}")
            else:
                print(f"❌ 删除计划失败: {delete_plan_id}")


def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("🎯 Planning Agent 演示菜单")
    print("=" * 60)
    print("1. 基本规划功能演示")
    print("2. 预定义场景演示")
    print("3. 不同规划策略演示")
    print("4. 计划管理功能演示")
    print("5. 运行所有演示")
    print("0. 退出")
    print("=" * 60)


async def main():
    """主函数"""
    print_banner()
    
    print("🚀 欢迎使用 Planning Agent 演示系统!")
    print("Planning Agent 基于 Agentic Design Patterns 的 Planning 设计模式")
    print("支持智能目标分解、多策略规划、动态调整和进度监控")
    
    while True:
        show_menu()
        
        try:
            choice = input("\n请选择演示项目 (0-5): ").strip()
            
            if choice == '0':
                print("\n👋 感谢使用 Planning Agent 演示系统!")
                break
            elif choice == '1':
                await demo_basic_planning()
            elif choice == '2':
                await demo_predefined_scenarios()
            elif choice == '3':
                await demo_different_strategies()
            elif choice == '4':
                await demo_plan_management()
            elif choice == '5':
                print("🚀 运行所有演示...")
                await demo_basic_planning()
                await demo_predefined_scenarios()
                await demo_different_strategies()
                await demo_plan_management()
                print("\n🎉 所有演示完成!")
            else:
                print("❌ 无效选择，请输入 0-5 之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，退出演示系统")
            break
        except Exception as e:
            print(f"\n❌ 演示过程中出现错误: {str(e)}")
            print("请检查网络连接和API配置")
        
        input("\n按 Enter 键继续...")


if __name__ == "__main__":
    asyncio.run(main())
