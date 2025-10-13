"""
Prompt Chaining Agent - 提示链代理

这个模块实现了 Agentic Design Pattern 中的 Prompt Chaining 模式。
提示链将复杂任务分解为一系列更小、更易管理的子任务，每个子任务通过专门的提示处理，
前一步的输出作为下一步的输入，形成链式依赖。

核心优势：
1. 模块化：将复杂任务分解为可管理的步骤
2. 可控性：每一步都有明确的输入输出
3. 可调试：容易定位问题所在的环节
4. 可复用：单个步骤可以在不同链中复用
5. 高质量：专注的提示通常产生更好的结果
"""

from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
import json
from datetime import datetime


@dataclass
class ChainStep:
    """提示链中的单个步骤"""
    name: str  # 步骤名称
    prompt_template: str  # 提示模板
    description: str = ""  # 步骤描述
    transform_fn: Optional[Callable] = None  # 可选的转换函数
    

@dataclass
class ChainResult:
    """提示链的执行结果"""
    final_output: str  # 最终输出
    intermediate_results: List[Dict[str, Any]]  # 中间结果
    total_steps: int  # 总步骤数
    success: bool  # 是否成功
    error_message: str = ""  # 错误信息
    execution_time: float = 0.0  # 执行时间（秒）


class PromptChainingAgent:
    """
    提示链代理 - 实现 Prompt Chaining 设计模式
    
    示例用法:
        agent = PromptChainingAgent(llm_client)
        chain = agent.create_chain([
            ChainStep("分析", "分析这个问题: {input}"),
            ChainStep("方案", "基于分析结果提出解决方案: {input}"),
            ChainStep("实施", "详细说明实施步骤: {input}")
        ])
        result = agent.run_chain(chain, "如何提高代码质量？")
    """
    
    def __init__(self, llm_client, verbose: bool = True):
        """
        初始化提示链代理
        
        Args:
            llm_client: 大语言模型客户端（需要有 chat 方法）
            verbose: 是否打印详细执行信息
        """
        self.llm_client = llm_client
        self.verbose = verbose
        self.chains: Dict[str, List[ChainStep]] = {}
        
    def create_chain(self, name: str, steps: List[ChainStep]) -> str:
        """
        创建一个提示链
        
        Args:
            name: 链的名称
            steps: 步骤列表
            
        Returns:
            链的标识符
        """
        self.chains[name] = steps
        if self.verbose:
            print(f"✓ 创建提示链 '{name}'，共 {len(steps)} 个步骤")
        return name
        
    def run_chain(self, chain_name: str, initial_input: str, 
                  context: Optional[Dict[str, Any]] = None) -> ChainResult:
        """
        执行提示链
        
        Args:
            chain_name: 链的名称
            initial_input: 初始输入
            context: 额外的上下文信息
            
        Returns:
            ChainResult 包含最终输出和中间结果
        """
        if chain_name not in self.chains:
            return ChainResult(
                final_output="",
                intermediate_results=[],
                total_steps=0,
                success=False,
                error_message=f"链 '{chain_name}' 不存在"
            )
            
        start_time = datetime.now()
        steps = self.chains[chain_name]
        intermediate_results = []
        current_input = initial_input
        context = context or {}
        
        try:
            for i, step in enumerate(steps, 1):
                if self.verbose:
                    print(f"\n{'='*60}")
                    print(f"步骤 {i}/{len(steps)}: {step.name}")
                    print(f"描述: {step.description}")
                    print(f"{'='*60}")
                
                # 格式化提示词
                prompt = step.prompt_template.format(
                    input=current_input,
                    **context
                )
                
                if self.verbose:
                    print(f"\n📝 提示词:\n{prompt}\n")
                
                # 调用 LLM
                response = self.llm_client.chat(prompt)
                
                # 应用转换函数（如果有）
                if step.transform_fn:
                    output = step.transform_fn(response)
                else:
                    output = response
                
                if self.verbose:
                    print(f"\n💡 输出:\n{output}\n")
                
                # 记录中间结果
                intermediate_results.append({
                    "step": i,
                    "name": step.name,
                    "prompt": prompt,
                    "output": output,
                    "timestamp": datetime.now().isoformat()
                })
                
                # 下一步的输入是当前步的输出
                current_input = output
                
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"✓ 链执行完成！总耗时: {execution_time:.2f}秒")
                print(f"{'='*60}\n")
            
            return ChainResult(
                final_output=current_input,
                intermediate_results=intermediate_results,
                total_steps=len(steps),
                success=True,
                execution_time=execution_time
            )
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return ChainResult(
                final_output="",
                intermediate_results=intermediate_results,
                total_steps=len(steps),
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def save_chain_result(self, result: ChainResult, filepath: str):
        """保存链执行结果到文件"""
        output = {
            "final_output": result.final_output,
            "intermediate_results": result.intermediate_results,
            "total_steps": result.total_steps,
            "success": result.success,
            "error_message": result.error_message,
            "execution_time": result.execution_time
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        if self.verbose:
            print(f"✓ 结果已保存到: {filepath}")


# ==================== 预定义的提示链场景 ====================

class DocumentGenerationChain:
    """文档生成提示链 - 自动生成结构化技术文档"""
    
    @staticmethod
    def get_steps() -> List[ChainStep]:
        return [
            ChainStep(
                name="生成大纲",
                description="根据主题生成文档大纲",
                prompt_template="""你是一位专业的技术文档撰写专家。请为以下主题生成一份详细的技术文档大纲。

主题: {input}

要求：
1. 包含引言、核心内容、实践示例、最佳实践、总结等部分
2. 每个部分要有2-4个子章节
3. 大纲要清晰、有逻辑性
4. 适合技术人员阅读

请以 Markdown 格式输出大纲。"""
            ),
            ChainStep(
                name="撰写内容",
                description="根据大纲撰写详细内容",
                prompt_template="""你是一位专业的技术文档撰写专家。请根据以下大纲撰写详细的技术文档内容。

大纲:
{input}

要求：
1. 内容要专业、准确、易懂
2. 每个章节要有充实的内容（不少于200字）
3. 使用清晰的技术术语
4. 保持 Markdown 格式
5. 适当使用列表、表格等元素

请撰写完整的文档内容。"""
            ),
            ChainStep(
                name="添加示例",
                description="在文档中添加代码示例和实践案例",
                prompt_template="""你是一位经验丰富的技术专家。请在以下文档中添加实用的代码示例和实践案例。

当前文档:
{input}

要求：
1. 在适当位置添加代码示例（使用代码块格式）
2. 示例要实用、可运行
3. 添加必要的注释说明
4. 可以添加使用场景说明
5. 保持文档的完整性和连贯性

请输出添加示例后的完整文档。"""
            ),
            ChainStep(
                name="优化润色",
                description="对文档进行最终优化和润色",
                prompt_template="""你是一位资深的技术文档审核专家。请对以下文档进行最后的优化和润色。

当前文档:
{input}

要求：
1. 检查并修正错别字和语法错误
2. 优化语言表达，使其更流畅专业
3. 确保格式统一规范
4. 添加必要的提示框（注意、警告等）
5. 确保文档结构清晰、易读

请输出最终优化后的文档。"""
            )
        ]


class CodeReviewChain:
    """代码审查提示链 - 系统化的代码审查流程"""
    
    @staticmethod
    def get_steps() -> List[ChainStep]:
        return [
            ChainStep(
                name="理解代码",
                description="分析代码的功能和结构",
                prompt_template="""你是一位资深代码审查专家。请仔细分析以下代码，理解其功能和结构。

代码:
{input}

请回答：
1. 这段代码的主要功能是什么？
2. 代码的整体结构如何？
3. 使用了哪些关键技术或模式？
4. 代码的复杂度如何？

请提供详细的分析。"""
            ),
            ChainStep(
                name="检查问题",
                description="识别代码中的潜在问题",
                prompt_template="""基于之前的代码理解，现在请检查代码中的潜在问题。

之前的分析:
{input}

请检查以下方面：
1. **Bug 和错误**: 逻辑错误、边界条件、异常处理
2. **性能问题**: 效率低下的代码、不必要的计算
3. **安全问题**: SQL注入、XSS、敏感数据泄露等
4. **可维护性**: 代码重复、命名不清、缺少注释
5. **最佳实践**: 是否符合语言和框架的最佳实践

请列出发现的所有问题，按严重程度排序。"""
            ),
            ChainStep(
                name="提出建议",
                description="提供具体的改进建议",
                prompt_template="""基于发现的问题，现在请提供具体的改进建议。

问题列表:
{input}

对每个问题，请提供：
1. 问题的严重程度（高/中/低）
2. 具体的改进建议
3. 修改后的代码示例（如适用）
4. 预期的改进效果

请以清晰的格式组织建议，优先级从高到低。"""
            ),
            ChainStep(
                name="生成报告",
                description="生成完整的代码审查报告",
                prompt_template="""请基于以上分析，生成一份完整的代码审查报告。

改进建议:
{input}

报告应包括：
1. **执行摘要**: 总体评价和主要发现
2. **详细分析**: 按类别列出问题和建议
3. **优先级行动项**: 需要立即处理的问题
4. **优点**: 代码中做得好的地方
5. **总体建议**: 下一步的行动建议

请生成专业的 Markdown 格式报告。"""
            )
        ]


class ResearchPlanningChain:
    """研究规划提示链 - 将问题转化为系统化的研究计划"""
    
    @staticmethod
    def get_steps() -> List[ChainStep]:
        return [
            ChainStep(
                name="问题分析",
                description="深入分析研究问题",
                prompt_template="""你是一位经验丰富的研究专家。请深入分析以下研究问题。

问题: {input}

请分析：
1. 问题的核心是什么？
2. 问题的范围和边界
3. 相关的关键概念和术语
4. 这个问题为什么重要？
5. 已知和未知的方面

请提供详细的问题分析。"""
            ),
            ChainStep(
                name="文献综述",
                description="规划文献调研方向",
                prompt_template="""基于问题分析，请规划文献调研方向。

问题分析:
{input}

请提供：
1. 需要调研的关键主题和领域
2. 建议的搜索关键词
3. 相关的学术期刊和会议
4. 需要关注的研究团队或专家
5. 文献阅读的优先级顺序

请给出系统化的文献调研计划。"""
            ),
            ChainStep(
                name="研究方法",
                description="设计研究方法和实验方案",
                prompt_template="""基于之前的分析，请设计研究方法和实验方案。

文献调研计划:
{input}

请设计：
1. 适用的研究方法（定性/定量/混合）
2. 数据收集方案
3. 实验设计（如适用）
4. 数据分析方法
5. 验证和评估标准

请提供详细的方法论设计。"""
            ),
            ChainStep(
                name="时间规划",
                description="制定详细的时间线和里程碑",
                prompt_template="""请为这个研究项目制定详细的时间规划。

研究方法:
{input}

请制定：
1. 项目分阶段计划（建议6个月周期）
2. 每个阶段的具体任务和产出
3. 关键里程碑和检查点
4. 风险评估和应对策略
5. 资源需求（人力、设备、预算）

请以甘特图或表格形式呈现时间规划。"""
            )
        ]


class StoryCreationChain:
    """故事创作提示链 - 创意写作工作流"""
    
    @staticmethod
    def get_steps() -> List[ChainStep]:
        return [
            ChainStep(
                name="构思情节",
                description="基于主题构思故事情节",
                prompt_template="""你是一位富有创意的故事创作者。请基于以下主题构思一个引人入胜的故事情节。

主题: {input}

请设计：
1. 故事的核心冲突
2. 主要角色（3-5个）
3. 故事发生的时间和地点
4. 情节的起承转合
5. 故事的高潮和结局

请提供详细的故事大纲。"""
            ),
            ChainStep(
                name="角色塑造",
                description="深化角色设定和背景",
                prompt_template="""基于故事大纲，请深化主要角色的设定。

故事大纲:
{input}

对每个主要角色，请设计：
1. 外貌特征和性格特点
2. 背景故事和动机
3. 角色关系网络
4. 角色成长弧线
5. 标志性对白或行为

请创建丰富立体的角色。"""
            ),
            ChainStep(
                name="撰写初稿",
                description="撰写故事的初稿",
                prompt_template="""现在请基于情节和角色设定，撰写故事的初稿。

角色设定:
{input}

要求：
1. 使用生动的语言描述
2. 注重场景和氛围营造
3. 通过对话展现角色性格
4. 控制节奏，营造张力
5. 长度约1500-2000字

请撰写完整的故事初稿。"""
            ),
            ChainStep(
                name="润色完善",
                description="对故事进行润色和完善",
                prompt_template="""请对故事初稿进行润色和完善。

初稿:
{input}

请优化：
1. 语言表达的流畅性和文学性
2. 细节描写的丰富度
3. 情感渲染的深度
4. 对话的真实性和个性化
5. 结构的紧凑性和完整性

请输出最终的精修版故事。"""
            )
        ]


class ProductAnalysisChain:
    """产品分析提示链 - 系统化的产品需求分析"""
    
    @staticmethod
    def get_steps() -> List[ChainStep]:
        return [
            ChainStep(
                name="需求理解",
                description="深入理解产品需求",
                prompt_template="""你是一位资深产品经理。请深入分析以下产品需求。

需求描述: {input}

请分析：
1. 用户痛点和需求背景
2. 目标用户群体画像
3. 核心价值主张
4. 与现有解决方案的差异
5. 成功的关键因素

请提供详细的需求分析。"""
            ),
            ChainStep(
                name="功能设计",
                description="设计产品功能和特性",
                prompt_template="""基于需求分析，请设计产品的功能和特性。

需求分析:
{input}

请设计：
1. 核心功能列表（MVP）
2. 高级功能和扩展特性
3. 功能优先级排序
4. 用户使用流程
5. 关键交互设计

请提供详细的功能规划。"""
            ),
            ChainStep(
                name="技术方案",
                description="提出技术实现方案",
                prompt_template="""请为这个产品提出技术实现方案。

功能设计:
{input}

请规划：
1. 系统架构设计
2. 技术栈选择（前端、后端、数据库等）
3. 关键技术难点和解决方案
4. 可扩展性和性能考虑
5. 安全性和数据隐私保护

请提供技术方案建议。"""
            ),
            ChainStep(
                name="实施计划",
                description="制定产品实施和上线计划",
                prompt_template="""请制定详细的产品实施和上线计划。

技术方案:
{input}

请规划：
1. 开发阶段划分（Sprint计划）
2. 团队组成和角色分工
3. 关键里程碑和交付物
4. 测试和质量保证策略
5. 上线和运营计划
6. 风险评估和应对措施

请提供完整的项目实施计划。"""
            )
        ]

