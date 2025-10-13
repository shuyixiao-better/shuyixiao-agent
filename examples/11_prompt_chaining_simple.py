"""
简单的 Prompt Chaining 示例

这是一个最简单的提示链示例，演示核心概念。
适合快速理解和测试 Prompt Chaining 的工作原理。
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.shuyixiao_agent.gitee_ai_client import GiteeAIClient
from src.shuyixiao_agent.agents.prompt_chaining_agent import (
    PromptChainingAgent,
    ChainStep
)


def example_1_simple_translation():
    """示例1：简单的翻译改进链"""
    print("\n" + "="*60)
    print("示例1：翻译改进链")
    print("="*60)
    print("任务：将中文翻译成英文，并进行改进和润色")
    print()
    
    # 初始化
    llm_client = GiteeAIClient()
    agent = PromptChainingAgent(llm_client, verbose=True)
    
    # 定义提示链步骤
    steps = [
        ChainStep(
            name="初步翻译",
            description="将中文翻译成英文",
            prompt_template="请将以下中文翻译成英文：\n\n{input}"
        ),
        ChainStep(
            name="改进表达",
            description="改进英文表达的地道性",
            prompt_template="请改进以下英文翻译，使其更加地道和流畅：\n\n{input}"
        ),
        ChainStep(
            name="专业润色",
            description="进行最终的专业润色",
            prompt_template="请对以下英文进行专业润色，确保语法正确、表达优雅：\n\n{input}"
        )
    ]
    
    # 创建并执行链
    agent.create_chain("translation", steps)
    
    chinese_text = "人工智能正在深刻改变我们的生活方式，从智能助手到自动驾驶，AI技术的应用无处不在。"
    result = agent.run_chain("translation", chinese_text)
    
    if result.success:
        print("\n" + "="*60)
        print("✅ 最终结果:")
        print("="*60)
        print(result.final_output)
        print(f"\n总耗时: {result.execution_time:.2f}秒")


def example_2_blog_post():
    """示例2：博客文章生成链"""
    print("\n" + "="*60)
    print("示例2：博客文章生成链")
    print("="*60)
    print("任务：从标题生成完整的博客文章")
    print()
    
    # 初始化
    llm_client = GiteeAIClient()
    agent = PromptChainingAgent(llm_client, verbose=True)
    
    # 定义提示链步骤
    steps = [
        ChainStep(
            name="构思大纲",
            description="根据标题构思文章大纲",
            prompt_template="""你是一位专业博主。请为以下博客标题构思一个详细大纲：

标题：{input}

要求：
- 包含引言、3-4个主要段落、结论
- 每个段落要有小标题
- 大纲要有逻辑性和吸引力"""
        ),
        ChainStep(
            name="撰写内容",
            description="根据大纲撰写完整文章",
            prompt_template="""请根据以下大纲撰写一篇完整的博客文章：

{input}

要求：
- 每个段落内容充实（至少150字）
- 语言生动、易读
- 适当使用例子和比喻
- 保持友好的语气"""
        ),
        ChainStep(
            name="添加互动元素",
            description="添加读者互动元素",
            prompt_template="""请在以下博客文章中添加互动元素：

{input}

要求：
- 在适当位置添加问题引发思考
- 添加行动号召（CTA）
- 可以添加小贴士或注意事项框
- 保持文章的完整性"""
        )
    ]
    
    # 创建并执行链
    agent.create_chain("blog", steps)
    
    title = "为什么学习 Python 是2024年最好的选择"
    result = agent.run_chain("blog", title)
    
    if result.success:
        # 保存文章
        with open("blog_post.md", 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(result.final_output)
        
        print("\n" + "="*60)
        print("✅ 博客文章已生成并保存到 blog_post.md")
        print(f"总耗时: {result.execution_time:.2f}秒")


def example_3_custom_chain():
    """示例3：自定义提示链"""
    print("\n" + "="*60)
    print("示例3：自定义提示链 - 问题解决流程")
    print("="*60)
    print("任务：使用提示链系统化地解决问题")
    print()
    
    # 初始化
    llm_client = GiteeAIClient()
    agent = PromptChainingAgent(llm_client, verbose=True)
    
    # 定义提示链步骤 - 经典的问题解决流程
    steps = [
        ChainStep(
            name="理解问题",
            description="深入理解和分析问题",
            prompt_template="""请深入分析以下问题：

{input}

请回答：
1. 问题的核心是什么？
2. 有哪些已知条件？
3. 有哪些未知因素？
4. 有什么限制条件？"""
        ),
        ChainStep(
            name="头脑风暴",
            description="提出多个可能的解决方案",
            prompt_template="""基于问题分析，请提出至少3个不同的解决方案：

{input}

对每个方案，请简要说明：
- 方案描述
- 主要优点
- 可能的缺点"""
        ),
        ChainStep(
            name="评估选择",
            description="评估并选择最佳方案",
            prompt_template="""请评估以下解决方案并推荐最佳方案：

{input}

请提供：
1. 各方案的综合评分（1-10分）
2. 推荐的最佳方案及理由
3. 实施该方案的关键成功因素"""
        ),
        ChainStep(
            name="制定计划",
            description="为最佳方案制定详细实施计划",
            prompt_template="""请为推荐的方案制定详细的实施计划：

{input}

请包括：
1. 具体实施步骤（分阶段）
2. 每个步骤的关键行动
3. 可能的风险和应对措施
4. 预期成果和验证方法"""
        )
    ]
    
    # 创建并执行链
    agent.create_chain("problem_solving", steps)
    
    problem = "如何在3个月内将网站的用户留存率从40%提升到60%？"
    result = agent.run_chain("problem_solving", problem)
    
    if result.success:
        # 保存完整的分析过程
        with open("problem_solution.md", 'w', encoding='utf-8') as f:
            f.write(f"# 问题解决方案\n\n")
            f.write(f"## 原始问题\n{problem}\n\n")
            
            for i, step_result in enumerate(result.intermediate_results, 1):
                f.write(f"## 步骤 {i}: {step_result['name']}\n\n")
                f.write(f"{step_result['output']}\n\n")
            
            f.write(f"## 最终方案\n\n{result.final_output}\n")
        
        print("\n" + "="*60)
        print("✅ 问题解决方案已保存到 problem_solution.md")
        print(f"总耗时: {result.execution_time:.2f}秒")


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         🔗 Prompt Chaining 简单示例 🔗                      ║
║                                                              ║
║  快速体验提示链（Prompt Chaining）的强大功能               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    examples = {
        '1': example_1_simple_translation,
        '2': example_2_blog_post,
        '3': example_3_custom_chain
    }
    
    while True:
        print("\n" + "="*60)
        print("选择要运行的示例：")
        print("="*60)
        print("[1] 翻译改进链 - 演示基础的链式处理")
        print("[2] 博客文章生成链 - 从标题到完整文章")
        print("[3] 问题解决链 - 系统化的问题分析和解决")
        print("[0] 退出")
        print("="*60)
        
        choice = input("\n请选择 (0-3): ").strip()
        
        if choice == '0':
            print("\n👋 再见！\n")
            break
        elif choice in examples:
            try:
                examples[choice]()
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
                import traceback
                traceback.print_exc()
            
            input("\n按 Enter 继续...")
        else:
            print("❌ 无效选择")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")

