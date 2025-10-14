"""
Routing Agent - 路由代理

这个模块实现了 Agentic Design Pattern 中的 Routing 模式。
Routing 模式的核心思想是根据输入的特征、意图或类型，智能地将请求路由到
不同的专家模型、处理流程或工具，从而实现更精准和高效的任务处理。

核心优势：
1. 智能分发：根据任务类型自动选择最合适的处理器
2. 专业化：不同类型的任务由专门的模型或流程处理
3. 可扩展：轻松添加新的路由规则和处理器
4. 高效性：避免使用单一模型处理所有类型的任务
5. 灵活性：支持基于规则和基于 LLM 的路由决策
"""

from typing import List, Dict, Any, Callable, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json
import re
from datetime import datetime


class RoutingStrategy(Enum):
    """路由策略枚举"""
    RULE_BASED = "rule_based"  # 基于规则的路由
    LLM_BASED = "llm_based"    # 基于 LLM 的路由
    KEYWORD = "keyword"         # 基于关键词的路由
    HYBRID = "hybrid"           # 混合路由（规则+LLM）


@dataclass
class RouteConfig:
    """路由配置"""
    name: str                              # 路由名称
    description: str                       # 路由描述
    handler: Callable                      # 处理函数
    keywords: Optional[List[str]] = None   # 关键词列表（用于关键词路由）
    pattern: Optional[str] = None          # 正则表达式模式（用于规则路由）
    priority: int = 0                      # 优先级（数字越大优先级越高）
    examples: Optional[List[str]] = None   # 示例输入


@dataclass
class RoutingResult:
    """路由结果"""
    route_name: str              # 选择的路由名称
    route_description: str       # 路由描述
    handler_output: Any          # 处理器输出
    confidence: float            # 置信度（0-1）
    routing_reason: str          # 路由原因
    execution_time: float        # 执行时间
    success: bool                # 是否成功
    error_message: str = ""      # 错误信息


class RoutingAgent:
    """
    路由代理 - 实现 Routing 设计模式
    
    示例用法:
        agent = RoutingAgent(llm_client, strategy="hybrid")
        
        # 注册路由
        agent.register_route(RouteConfig(
            name="code_gen",
            description="生成代码",
            handler=code_generator_handler,
            keywords=["代码", "函数", "实现"],
            priority=10
        ))
        
        # 执行路由
        result = agent.route("帮我写一个Python排序函数")
    """
    
    def __init__(
        self,
        llm_client=None,
        strategy: Union[RoutingStrategy, str] = RoutingStrategy.HYBRID,
        verbose: bool = True,
        default_handler: Optional[Callable] = None
    ):
        """
        初始化路由代理
        
        Args:
            llm_client: 大语言模型客户端（用于基于 LLM 的路由）
            strategy: 路由策略
            verbose: 是否打印详细信息
            default_handler: 默认处理器（当没有匹配的路由时使用）
        """
        self.llm_client = llm_client
        self.strategy = RoutingStrategy(strategy) if isinstance(strategy, str) else strategy
        self.verbose = verbose
        self.default_handler = default_handler
        self.routes: Dict[str, RouteConfig] = {}
        
    def register_route(self, route_config: RouteConfig):
        """
        注册一个路由
        
        Args:
            route_config: 路由配置
        """
        self.routes[route_config.name] = route_config
        if self.verbose:
            print(f"✓ 注册路由 '{route_config.name}': {route_config.description}")
    
    def register_routes(self, route_configs: List[RouteConfig]):
        """批量注册路由"""
        for config in route_configs:
            self.register_route(config)
    
    def _route_by_keyword(self, input_text: str) -> Optional[tuple[str, float]]:
        """
        基于关键词的路由
        
        Returns:
            (route_name, confidence) 或 None
        """
        input_lower = input_text.lower()
        best_match = None
        max_score = 0
        
        for route_name, config in self.routes.items():
            if not config.keywords:
                continue
                
            # 计算关键词匹配分数
            score = 0
            for keyword in config.keywords:
                if keyword.lower() in input_lower:
                    score += 1
            
            # 考虑优先级
            score += config.priority * 0.1
            
            if score > max_score:
                max_score = score
                best_match = route_name
        
        if best_match and max_score > 0:
            confidence = min(max_score / 5.0, 1.0)  # 标准化到 0-1
            return best_match, confidence
        
        return None
    
    def _route_by_rule(self, input_text: str) -> Optional[tuple[str, float]]:
        """
        基于规则（正则表达式）的路由
        
        Returns:
            (route_name, confidence) 或 None
        """
        # 按优先级排序
        sorted_routes = sorted(
            [(name, config) for name, config in self.routes.items() if config.pattern],
            key=lambda x: x[1].priority,
            reverse=True
        )
        
        for route_name, config in sorted_routes:
            if re.search(config.pattern, input_text, re.IGNORECASE):
                return route_name, 0.9  # 规则匹配给予高置信度
        
        return None
    
    def _route_by_llm(self, input_text: str) -> Optional[tuple[str, float, str]]:
        """
        基于 LLM 的路由
        
        Returns:
            (route_name, confidence, reason) 或 None
        """
        if not self.llm_client:
            return None
        
        # 构建路由选项描述
        routes_desc = []
        for name, config in self.routes.items():
            desc = f"- **{name}**: {config.description}"
            if config.examples:
                desc += f"\n  示例: {', '.join(config.examples[:2])}"
            routes_desc.append(desc)
        
        prompt = f"""你是一个智能路由器。请根据用户输入，选择最合适的处理路由。

可用路由：
{chr(10).join(routes_desc)}

用户输入: {input_text}

请以 JSON 格式返回：
{{
    "route": "选择的路由名称",
    "confidence": 0.0-1.0之间的置信度,
    "reason": "选择这个路由的原因"
}}

只返回 JSON，不要其他内容。"""
        
        try:
            response = self.llm_client.simple_chat(prompt)
            
            # 尝试解析 JSON
            # 移除可能的 markdown 代码块标记
            response_clean = response.strip()
            if response_clean.startswith("```"):
                # 移除开头的 ```json 或 ```
                response_clean = re.sub(r'^```(?:json)?\s*\n', '', response_clean)
                # 移除结尾的 ```
                response_clean = re.sub(r'\n```\s*$', '', response_clean)
            
            result = json.loads(response_clean)
            
            route_name = result.get("route")
            confidence = float(result.get("confidence", 0.5))
            reason = result.get("reason", "")
            
            # 验证路由是否存在
            if route_name in self.routes:
                return route_name, confidence, reason
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  LLM 路由失败: {e}")
        
        return None
    
    def route(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> RoutingResult:
        """
        执行路由和处理
        
        Args:
            input_text: 输入文本
            context: 额外的上下文信息
            
        Returns:
            RoutingResult 包含路由决策和处理结果
        """
        start_time = datetime.now()
        context = context or {}
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"🔀 路由代理 - {self.strategy.value}")
            print(f"输入: {input_text[:100]}...")
            print(f"{'='*60}\n")
        
        try:
            route_name = None
            confidence = 0.0
            reason = ""
            
            # 根据策略选择路由方法
            if self.strategy == RoutingStrategy.KEYWORD:
                result = self._route_by_keyword(input_text)
                if result:
                    route_name, confidence = result
                    reason = "基于关键词匹配"
                    
            elif self.strategy == RoutingStrategy.RULE_BASED:
                result = self._route_by_rule(input_text)
                if result:
                    route_name, confidence = result
                    reason = "基于规则匹配"
                    
            elif self.strategy == RoutingStrategy.LLM_BASED:
                result = self._route_by_llm(input_text)
                if result:
                    route_name, confidence, reason = result
                    
            elif self.strategy == RoutingStrategy.HYBRID:
                # 混合策略：先尝试规则，再尝试关键词，最后使用 LLM
                result = self._route_by_rule(input_text)
                if result:
                    route_name, confidence = result
                    reason = "基于规则匹配（混合策略）"
                else:
                    result = self._route_by_keyword(input_text)
                    if result:
                        route_name, confidence = result
                        reason = "基于关键词匹配（混合策略）"
                    else:
                        result = self._route_by_llm(input_text)
                        if result:
                            route_name, confidence, reason = result
            
            # 如果没有匹配到路由，使用默认处理器
            if not route_name:
                if self.default_handler:
                    route_name = "default"
                    confidence = 0.3
                    reason = "使用默认处理器"
                    handler = self.default_handler
                    description = "默认处理"
                else:
                    end_time = datetime.now()
                    return RoutingResult(
                        route_name="none",
                        route_description="无匹配路由",
                        handler_output="未找到合适的路由处理器",
                        confidence=0.0,
                        routing_reason="没有匹配的路由且没有默认处理器",
                        execution_time=(end_time - start_time).total_seconds(),
                        success=False,
                        error_message="未找到合适的路由"
                    )
            else:
                config = self.routes[route_name]
                handler = config.handler
                description = config.description
            
            if self.verbose:
                print(f"📍 选择路由: {route_name}")
                print(f"📊 置信度: {confidence:.2%}")
                print(f"💡 原因: {reason}\n")
            
            # 执行处理器
            if self.verbose:
                print(f"⚙️  执行处理器...\n")
            
            output = handler(input_text, context)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            if self.verbose:
                print(f"\n✅ 路由完成，耗时: {execution_time:.2f}秒\n")
            
            return RoutingResult(
                route_name=route_name,
                route_description=description,
                handler_output=output,
                confidence=confidence,
                routing_reason=reason,
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            if self.verbose:
                print(f"\n❌ 路由失败: {str(e)}\n")
            
            return RoutingResult(
                route_name="error",
                route_description="错误",
                handler_output=None,
                confidence=0.0,
                routing_reason="",
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    def get_routes_info(self) -> List[Dict[str, Any]]:
        """获取所有路由的信息"""
        routes_info = []
        for name, config in self.routes.items():
            routes_info.append({
                "name": name,
                "description": config.description,
                "keywords": config.keywords,
                "pattern": config.pattern,
                "priority": config.priority,
                "examples": config.examples
            })
        return routes_info


# ==================== 预定义的路由场景 ====================


class SmartAssistantRoutes:
    """智能助手路由配置 - 涵盖常见的助手任务"""
    
    @staticmethod
    def get_routes(llm_client) -> List[RouteConfig]:
        """获取智能助手的所有路由配置"""
        
        def code_generation_handler(input_text: str, context: Dict[str, Any]) -> str:
            """代码生成处理器"""
            prompt = f"""你是一个专业的代码生成专家。请根据用户需求生成高质量的代码。

用户需求: {input_text}

要求：
1. 代码要清晰、易读、有注释
2. 遵循最佳实践和设计模式
3. 包含必要的错误处理
4. 提供使用示例

请生成代码："""
            return llm_client.simple_chat(prompt)
        
        def writing_handler(input_text: str, context: Dict[str, Any]) -> str:
            """写作处理器"""
            prompt = f"""你是一个专业的内容创作专家。请根据用户需求创作内容。

用户需求: {input_text}

要求：
1. 内容要有逻辑性和连贯性
2. 语言要流畅、专业
3. 结构要清晰
4. 适当使用修辞手法

请创作内容："""
            return llm_client.simple_chat(prompt)
        
        def analysis_handler(input_text: str, context: Dict[str, Any]) -> str:
            """分析处理器"""
            prompt = f"""你是一个专业的分析专家。请对用户提供的内容进行深入分析。

用户输入: {input_text}

要求：
1. 从多个角度分析问题
2. 提供数据支持（如适用）
3. 给出洞察和建议
4. 结构化呈现分析结果

请进行分析："""
            return llm_client.simple_chat(prompt)
        
        def translation_handler(input_text: str, context: Dict[str, Any]) -> str:
            """翻译处理器"""
            prompt = f"""你是一个专业的翻译专家。请翻译以下内容。

内容: {input_text}

要求：
1. 准确传达原文意思
2. 符合目标语言习惯
3. 保持专业术语的准确性
4. 如果没有明确指定目标语言，请识别源语言并翻译为最合适的语言

请进行翻译："""
            return llm_client.simple_chat(prompt)
        
        def qa_handler(input_text: str, context: Dict[str, Any]) -> str:
            """问答处理器"""
            prompt = f"""你是一个知识渊博的助手。请回答用户的问题。

问题: {input_text}

要求：
1. 回答要准确、全面
2. 提供必要的背景信息
3. 如果可能，给出示例说明
4. 如果不确定，请说明

请回答："""
            return llm_client.simple_chat(prompt)
        
        def summary_handler(input_text: str, context: Dict[str, Any]) -> str:
            """摘要处理器"""
            prompt = f"""你是一个专业的内容摘要专家。请对以下内容生成摘要。

内容: {input_text}

要求：
1. 提取核心要点
2. 保持信息的准确性
3. 简洁明了
4. 结构化呈现

请生成摘要："""
            return llm_client.simple_chat(prompt)
        
        return [
            RouteConfig(
                name="code_generation",
                description="代码生成 - 编写、优化、解释代码",
                handler=code_generation_handler,
                keywords=["代码", "函数", "类", "实现", "编程", "bug", "算法", "程序"],
                pattern=r"(写|生成|创建|实现).*(代码|函数|类|程序|算法)",
                priority=10,
                examples=["写一个Python排序函数", "帮我实现一个二叉树"]
            ),
            RouteConfig(
                name="writing",
                description="内容创作 - 文章、故事、邮件、文案",
                handler=writing_handler,
                keywords=["写作", "文章", "故事", "邮件", "报告", "博客", "文案", "创作"],
                pattern=r"(写|创作|撰写).*(文章|故事|邮件|报告|博客)",
                priority=9,
                examples=["写一篇关于AI的博客", "帮我起草一封感谢信"]
            ),
            RouteConfig(
                name="analysis",
                description="数据分析 - 分析问题、数据、趋势",
                handler=analysis_handler,
                keywords=["分析", "评估", "研究", "调查", "统计", "趋势", "对比"],
                pattern=r"(分析|评估|研究).*(数据|趋势|问题|情况)",
                priority=8,
                examples=["分析这个市场趋势", "评估这个方案的优劣"]
            ),
            RouteConfig(
                name="translation",
                description="翻译 - 多语言翻译",
                handler=translation_handler,
                keywords=["翻译", "translate", "英文", "中文", "日语", "法语", "translation"],
                pattern=r"(翻译|translate).*(成|为|to|into)",
                priority=9,
                examples=["把这段话翻译成英文", "translate this to Chinese"]
            ),
            RouteConfig(
                name="qa",
                description="问答 - 回答各类问题",
                handler=qa_handler,
                keywords=["什么", "为什么", "怎么", "如何", "是否", "能否", "问题"],
                pattern=r"(什么|为什么|怎么|如何|是否|能否|可以|请问)",
                priority=5,
                examples=["什么是量子计算", "Python中的装饰器是什么"]
            ),
            RouteConfig(
                name="summary",
                description="摘要总结 - 提取关键信息",
                handler=summary_handler,
                keywords=["总结", "摘要", "概括", "提炼", "归纳", "简述"],
                pattern=r"(总结|摘要|概括|提炼|归纳).*(内容|文章|要点)",
                priority=8,
                examples=["总结这篇文章的要点", "提炼这段对话的核心内容"]
            ),
        ]


class DeveloperAssistantRoutes:
    """开发者助手路由配置 - 专注于开发相关任务"""
    
    @staticmethod
    def get_routes(llm_client) -> List[RouteConfig]:
        """获取开发者助手的所有路由配置"""
        
        def code_review_handler(input_text: str, context: Dict[str, Any]) -> str:
            """代码审查处理器"""
            prompt = f"""你是一个资深的代码审查专家。请审查以下代码。

代码:
{input_text}

请从以下方面审查：
1. 代码质量和可读性
2. 潜在的bug和错误
3. 性能问题
4. 安全隐患
5. 最佳实践

请提供详细的审查报告："""
            return llm_client.simple_chat(prompt)
        
        def debugging_handler(input_text: str, context: Dict[str, Any]) -> str:
            """调试处理器"""
            prompt = f"""你是一个专业的调试专家。请帮助分析和解决以下问题。

问题描述:
{input_text}

请提供：
1. 问题原因分析
2. 可能的解决方案
3. 预防类似问题的建议
4. 相关最佳实践

请进行分析："""
            return llm_client.simple_chat(prompt)
        
        def optimization_handler(input_text: str, context: Dict[str, Any]) -> str:
            """优化处理器"""
            prompt = f"""你是一个性能优化专家。请优化以下代码或系统。

内容:
{input_text}

请提供：
1. 性能瓶颈分析
2. 优化建议和方案
3. 优化后的代码（如适用）
4. 预期的性能提升

请进行优化："""
            return llm_client.simple_chat(prompt)
        
        def architecture_handler(input_text: str, context: Dict[str, Any]) -> str:
            """架构设计处理器"""
            prompt = f"""你是一个软件架构专家。请设计系统架构。

需求:
{input_text}

请提供：
1. 系统架构设计
2. 技术栈选择
3. 模块划分
4. 关键技术点
5. 可扩展性考虑

请设计架构："""
            return llm_client.simple_chat(prompt)
        
        return [
            RouteConfig(
                name="code_review",
                description="代码审查 - 检查代码质量和问题",
                handler=code_review_handler,
                keywords=["审查", "review", "检查", "代码质量", "重构"],
                pattern=r"(审查|review|检查).*(代码|code)",
                priority=10,
                examples=["审查这段代码", "code review"]
            ),
            RouteConfig(
                name="debugging",
                description="调试 - 查找和修复bug",
                handler=debugging_handler,
                keywords=["bug", "错误", "异常", "调试", "debug", "报错", "崩溃"],
                pattern=r"(bug|错误|异常|调试|debug|报错)",
                priority=10,
                examples=["为什么会报这个错", "debug这个问题"]
            ),
            RouteConfig(
                name="optimization",
                description="性能优化 - 提升代码或系统性能",
                handler=optimization_handler,
                keywords=["优化", "性能", "加速", "效率", "慢"],
                pattern=r"(优化|性能|加速).*(代码|系统|程序)",
                priority=9,
                examples=["如何优化这段代码", "提升查询性能"]
            ),
            RouteConfig(
                name="architecture",
                description="架构设计 - 系统架构和技术选型",
                handler=architecture_handler,
                keywords=["架构", "设计", "技术选型", "系统设计", "微服务"],
                pattern=r"(架构|设计).*(系统|服务|应用)",
                priority=9,
                examples=["设计一个电商系统架构", "微服务架构方案"]
            ),
        ]

