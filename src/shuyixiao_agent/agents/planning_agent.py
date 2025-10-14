"""
Planning Agent - 基于 Agentic Design Patterns 的规划智能体

Planning（规划）设计模式的核心思想是让AI智能体能够：
1. 分析复杂目标并分解为可执行的子任务
2. 制定合理的执行计划和时间安排
3. 动态调整计划以应对变化
4. 监控执行进度并提供反馈

与其他模式的区别：
- Routing: 选择合适的处理器
- Prompt Chaining: 按预定义步骤执行
- Planning: 动态制定和调整执行计划
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"          # 待执行
    IN_PROGRESS = "in_progress"  # 执行中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"           # 执行失败
    BLOCKED = "blocked"         # 被阻塞
    CANCELLED = "cancelled"     # 已取消


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class PlanningStrategy(Enum):
    """规划策略枚举"""
    SEQUENTIAL = "sequential"    # 顺序执行
    PARALLEL = "parallel"       # 并行执行
    ADAPTIVE = "adaptive"       # 自适应执行
    DEPENDENCY_BASED = "dependency_based"  # 基于依赖关系


@dataclass
class Task:
    """任务定义类"""
    id: str
    name: str
    description: str
    handler: Optional[Callable] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_duration: int = 60  # 预估时间（秒）
    dependencies: List[str] = field(default_factory=list)  # 依赖的任务ID
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error_message: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress: float = 0.0  # 进度百分比 0-1
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[int]:
        """获取实际执行时间（秒）"""
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds())
        return None

    @property
    def is_ready(self) -> bool:
        """检查任务是否可以执行（依赖已满足）"""
        return self.status == TaskStatus.PENDING

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority.value,
            "estimated_duration": self.estimated_duration,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "result": self.result,
            "error_message": self.error_message,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "progress": self.progress,
            "duration": self.duration,
            "metadata": self.metadata
        }


@dataclass
class ExecutionPlan:
    """执行计划类"""
    id: str
    name: str
    description: str
    tasks: List[Task] = field(default_factory=list)
    strategy: PlanningStrategy = PlanningStrategy.DEPENDENCY_BASED
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_task(self, task: Task):
        """添加任务到计划中"""
        self.tasks.append(task)
        self.updated_at = datetime.now()

    def get_task(self, task_id: str) -> Optional[Task]:
        """根据ID获取任务"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_ready_tasks(self) -> List[Task]:
        """获取可以执行的任务（依赖已满足）"""
        ready_tasks = []
        completed_task_ids = {task.id for task in self.tasks if task.status == TaskStatus.COMPLETED}
        
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                # 检查依赖是否都已完成
                if all(dep_id in completed_task_ids for dep_id in task.dependencies):
                    ready_tasks.append(task)
        
        # 按优先级排序
        ready_tasks.sort(key=lambda t: t.priority.value, reverse=True)
        return ready_tasks

    def update_progress(self):
        """更新整体进度"""
        if not self.tasks:
            self.progress = 0.0
            return
        
        total_weight = len(self.tasks)
        completed_weight = sum(1 for task in self.tasks if task.status == TaskStatus.COMPLETED)
        in_progress_weight = sum(task.progress for task in self.tasks if task.status == TaskStatus.IN_PROGRESS)
        
        self.progress = (completed_weight + in_progress_weight) / total_weight
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tasks": [task.to_dict() for task in self.tasks],
            "strategy": self.strategy.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status.value,
            "progress": self.progress,
            "metadata": self.metadata
        }


@dataclass
class PlanningResult:
    """规划结果类"""
    success: bool
    plan: Optional[ExecutionPlan] = None
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    total_duration: Optional[int] = None
    completed_tasks: int = 0
    failed_tasks: int = 0

    def add_log(self, level: str, message: str, task_id: Optional[str] = None, **kwargs):
        """添加执行日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "task_id": task_id,
            **kwargs
        }
        self.execution_log.append(log_entry)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "success": self.success,
            "plan": self.plan.to_dict() if self.plan else None,
            "execution_log": self.execution_log,
            "error_message": self.error_message,
            "total_duration": self.total_duration,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks
        }


class PlanningAgent:
    """Planning Agent 核心类"""

    def __init__(
        self,
        llm_client,
        strategy: PlanningStrategy = PlanningStrategy.ADAPTIVE,
        max_parallel_tasks: int = 3,
        verbose: bool = False
    ):
        """
        初始化 Planning Agent
        
        Args:
            llm_client: LLM客户端
            strategy: 默认规划策略
            max_parallel_tasks: 最大并行任务数
            verbose: 是否输出详细日志
        """
        self.llm_client = llm_client
        self.strategy = strategy
        self.max_parallel_tasks = max_parallel_tasks
        self.verbose = verbose
        self.plans: Dict[str, ExecutionPlan] = {}
        self.task_handlers: Dict[str, Callable] = {}

    def register_task_handler(self, task_type: str, handler: Callable):
        """注册任务处理器"""
        self.task_handlers[task_type] = handler
        if self.verbose:
            logger.info(f"注册任务处理器: {task_type}")

    def create_plan_from_goal(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None
    ) -> PlanningResult:
        """
        根据目标创建执行计划
        
        Args:
            goal: 目标描述
            context: 上下文信息
            
        Returns:
            PlanningResult: 规划结果
        """
        try:
            if self.verbose:
                logger.info(f"开始为目标创建计划: {goal}")

            # 使用LLM分析目标并生成任务分解
            planning_prompt = self._build_planning_prompt(goal, context)
            response = self.llm_client.simple_chat(planning_prompt)
            
            # 解析LLM响应并创建计划
            plan = self._parse_planning_response(response, goal)
            
            # 保存计划
            self.plans[plan.id] = plan
            
            result = PlanningResult(success=True, plan=plan)
            result.add_log("INFO", f"成功创建计划: {plan.name}", plan_id=plan.id)
            
            if self.verbose:
                logger.info(f"计划创建完成: {plan.name}, 包含 {len(plan.tasks)} 个任务")
            
            return result

        except Exception as e:
            error_msg = f"创建计划失败: {str(e)}"
            logger.error(error_msg)
            result = PlanningResult(success=False, error_message=error_msg)
            result.add_log("ERROR", error_msg)
            return result

    def execute_plan(
        self,
        plan_id: str,
        progress_callback: Optional[Callable] = None
    ) -> PlanningResult:
        """
        执行计划
        
        Args:
            plan_id: 计划ID
            progress_callback: 进度回调函数
            
        Returns:
            PlanningResult: 执行结果
        """
        if plan_id not in self.plans:
            error_msg = f"计划不存在: {plan_id}"
            result = PlanningResult(success=False, error_message=error_msg)
            result.add_log("ERROR", error_msg)
            return result

        plan = self.plans[plan_id]
        result = PlanningResult(success=True, plan=plan)
        start_time = datetime.now()

        try:
            if self.verbose:
                logger.info(f"开始执行计划: {plan.name}")

            plan.status = TaskStatus.IN_PROGRESS
            result.add_log("INFO", f"开始执行计划: {plan.name}", plan_id=plan_id)

            # 根据策略执行任务
            if plan.strategy == PlanningStrategy.SEQUENTIAL:
                self._execute_sequential(plan, result, progress_callback)
            elif plan.strategy == PlanningStrategy.PARALLEL:
                self._execute_parallel(plan, result, progress_callback)
            elif plan.strategy == PlanningStrategy.DEPENDENCY_BASED:
                self._execute_dependency_based(plan, result, progress_callback)
            else:  # ADAPTIVE
                self._execute_adaptive(plan, result, progress_callback)

            # 计算执行统计
            end_time = datetime.now()
            result.total_duration = int((end_time - start_time).total_seconds())
            result.completed_tasks = sum(1 for task in plan.tasks if task.status == TaskStatus.COMPLETED)
            result.failed_tasks = sum(1 for task in plan.tasks if task.status == TaskStatus.FAILED)

            # 更新计划状态
            if result.failed_tasks > 0:
                plan.status = TaskStatus.FAILED
                result.success = False
                result.add_log("WARNING", f"计划执行完成，但有 {result.failed_tasks} 个任务失败")
            else:
                plan.status = TaskStatus.COMPLETED
                result.add_log("INFO", f"计划执行成功完成，共完成 {result.completed_tasks} 个任务")

            if self.verbose:
                logger.info(f"计划执行完成: {plan.name}, 耗时: {result.total_duration}秒")

        except Exception as e:
            error_msg = f"计划执行失败: {str(e)}"
            logger.error(error_msg)
            plan.status = TaskStatus.FAILED
            result.success = False
            result.error_message = error_msg
            result.add_log("ERROR", error_msg)

        return result

    def _build_planning_prompt(self, goal: str, context: Optional[Dict[str, Any]] = None) -> str:
        """构建规划提示词"""
        context_str = ""
        if context:
            context_str = f"\n\n上下文信息：\n{json.dumps(context, ensure_ascii=False, indent=2)}"

        return f"""你是一个专业的项目规划专家，需要将用户的目标分解为具体可执行的任务。

目标：{goal}{context_str}

请按照以下JSON格式返回任务分解结果：

{{
    "plan_name": "计划名称",
    "plan_description": "计划描述",
    "tasks": [
        {{
            "id": "task_1",
            "name": "任务名称",
            "description": "任务详细描述",
            "task_type": "任务类型（如：analysis, coding, testing, documentation等）",
            "priority": 1-4,
            "estimated_duration": 预估时间（分钟）,
            "dependencies": ["依赖的任务ID列表"],
            "metadata": {{
                "additional_info": "其他信息"
            }}
        }}
    ],
    "strategy": "执行策略（sequential/parallel/dependency_based/adaptive）"
}}

要求：
1. 任务分解要具体、可执行
2. 合理设置任务依赖关系
3. 估算合理的执行时间
4. 按重要性设置优先级
5. 选择合适的执行策略"""

    def _parse_planning_response(self, response: str, goal: str) -> ExecutionPlan:
        """解析LLM规划响应"""
        try:
            # 尝试解析JSON响应
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                # 尝试找到JSON部分
                json_str = response.strip()
                if not json_str.startswith("{"):
                    # 如果不是JSON，使用默认解析
                    return self._create_default_plan(goal)

            data = json.loads(json_str)
            
            # 创建计划
            plan_id = f"plan_{int(time.time())}"
            plan = ExecutionPlan(
                id=plan_id,
                name=data.get("plan_name", f"计划_{goal[:20]}"),
                description=data.get("plan_description", goal),
                strategy=PlanningStrategy(data.get("strategy", "dependency_based"))
            )

            # 创建任务
            for task_data in data.get("tasks", []):
                task = Task(
                    id=task_data["id"],
                    name=task_data["name"],
                    description=task_data["description"],
                    priority=TaskPriority(task_data.get("priority", 2)),
                    estimated_duration=task_data.get("estimated_duration", 60) * 60,  # 转换为秒
                    dependencies=task_data.get("dependencies", []),
                    metadata=task_data.get("metadata", {})
                )
                
                # 设置任务处理器
                task_type = task_data.get("task_type", "default")
                if task_type in self.task_handlers:
                    task.handler = self.task_handlers[task_type]
                else:
                    task.handler = self._default_task_handler

                plan.add_task(task)

            return plan

        except Exception as e:
            logger.warning(f"解析规划响应失败: {e}, 使用默认计划")
            return self._create_default_plan(goal)

    def _create_default_plan(self, goal: str) -> ExecutionPlan:
        """创建默认计划"""
        plan_id = f"plan_{int(time.time())}"
        plan = ExecutionPlan(
            id=plan_id,
            name=f"默认计划_{goal[:20]}",
            description=f"为目标 '{goal}' 创建的默认执行计划",
            strategy=PlanningStrategy.SEQUENTIAL
        )

        # 创建基本任务
        tasks = [
            Task(
                id="task_analysis",
                name="需求分析",
                description=f"分析目标：{goal}",
                priority=TaskPriority.HIGH,
                estimated_duration=300,
                handler=self._default_task_handler
            ),
            Task(
                id="task_planning",
                name="详细规划",
                description="制定详细的实施计划",
                priority=TaskPriority.MEDIUM,
                estimated_duration=600,
                dependencies=["task_analysis"],
                handler=self._default_task_handler
            ),
            Task(
                id="task_execution",
                name="执行实施",
                description="执行具体的实施工作",
                priority=TaskPriority.HIGH,
                estimated_duration=1800,
                dependencies=["task_planning"],
                handler=self._default_task_handler
            ),
            Task(
                id="task_review",
                name="结果检查",
                description="检查和验证执行结果",
                priority=TaskPriority.MEDIUM,
                estimated_duration=300,
                dependencies=["task_execution"],
                handler=self._default_task_handler
            )
        ]

        for task in tasks:
            plan.add_task(task)

        return plan

    def _execute_sequential(
        self,
        plan: ExecutionPlan,
        result: PlanningResult,
        progress_callback: Optional[Callable] = None
    ):
        """顺序执行任务"""
        for task in plan.tasks:
            if task.status == TaskStatus.PENDING:
                self._execute_task(task, result, progress_callback)
                plan.update_progress()
                if progress_callback:
                    progress_callback(plan.progress, task)

    def _execute_dependency_based(
        self,
        plan: ExecutionPlan,
        result: PlanningResult,
        progress_callback: Optional[Callable] = None
    ):
        """基于依赖关系执行任务"""
        while True:
            ready_tasks = plan.get_ready_tasks()
            if not ready_tasks:
                break

            # 执行准备好的任务
            for task in ready_tasks[:self.max_parallel_tasks]:
                self._execute_task(task, result, progress_callback)
                plan.update_progress()
                if progress_callback:
                    progress_callback(plan.progress, task)

    def _execute_parallel(
        self,
        plan: ExecutionPlan,
        result: PlanningResult,
        progress_callback: Optional[Callable] = None
    ):
        """并行执行任务（简化版，实际应使用线程池）"""
        pending_tasks = [task for task in plan.tasks if task.status == TaskStatus.PENDING]
        
        for task in pending_tasks:
            self._execute_task(task, result, progress_callback)
            plan.update_progress()
            if progress_callback:
                progress_callback(plan.progress, task)

    def _execute_adaptive(
        self,
        plan: ExecutionPlan,
        result: PlanningResult,
        progress_callback: Optional[Callable] = None
    ):
        """自适应执行（根据情况选择策略）"""
        # 简化实现：优先执行高优先级任务
        tasks_by_priority = sorted(
            [task for task in plan.tasks if task.status == TaskStatus.PENDING],
            key=lambda t: t.priority.value,
            reverse=True
        )
        
        for task in tasks_by_priority:
            # 检查依赖
            ready_tasks = plan.get_ready_tasks()
            if task in ready_tasks:
                self._execute_task(task, result, progress_callback)
                plan.update_progress()
                if progress_callback:
                    progress_callback(plan.progress, task)

    def _execute_task(
        self,
        task: Task,
        result: PlanningResult,
        progress_callback: Optional[Callable] = None
    ):
        """执行单个任务"""
        try:
            if self.verbose:
                logger.info(f"开始执行任务: {task.name}")

            task.status = TaskStatus.IN_PROGRESS
            task.start_time = datetime.now()
            result.add_log("INFO", f"开始执行任务: {task.name}", task_id=task.id)

            # 调用任务处理器
            if task.handler:
                task.result = task.handler(task)
            else:
                task.result = self._default_task_handler(task)

            task.status = TaskStatus.COMPLETED
            task.end_time = datetime.now()
            task.progress = 1.0
            result.add_log("INFO", f"任务执行完成: {task.name}", task_id=task.id)

            if self.verbose:
                logger.info(f"任务执行完成: {task.name}, 耗时: {task.duration}秒")

        except Exception as e:
            error_msg = f"任务执行失败: {task.name}, 错误: {str(e)}"
            logger.error(error_msg)
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.end_time = datetime.now()
            result.add_log("ERROR", error_msg, task_id=task.id)

    def _default_task_handler(self, task: Task) -> str:
        """默认任务处理器"""
        # 使用LLM处理任务
        prompt = f"""请执行以下任务：

任务名称：{task.name}
任务描述：{task.description}
任务优先级：{task.priority.name}
预估时间：{task.estimated_duration}秒

请提供详细的执行结果和输出。"""

        try:
            response = self.llm_client.simple_chat(prompt)
            return response
        except Exception as e:
            return f"任务执行失败: {str(e)}"

    def get_plan(self, plan_id: str) -> Optional[ExecutionPlan]:
        """获取计划"""
        return self.plans.get(plan_id)

    def list_plans(self) -> List[ExecutionPlan]:
        """列出所有计划"""
        return list(self.plans.values())

    def delete_plan(self, plan_id: str) -> bool:
        """删除计划"""
        if plan_id in self.plans:
            del self.plans[plan_id]
            return True
        return False


# 预定义的Planning场景
class ProjectPlanningScenarios:
    """项目规划场景"""

    @staticmethod
    def software_development_plan(llm_client) -> Dict[str, Any]:
        """软件开发项目规划"""
        return {
            "name": "软件开发项目",
            "description": "完整的软件开发项目规划，包含需求分析、设计、开发、测试、部署等阶段",
            "template_tasks": [
                {
                    "id": "requirements_analysis",
                    "name": "需求分析",
                    "description": "收集和分析项目需求，明确功能和非功能需求",
                    "task_type": "analysis",
                    "priority": 4,
                    "estimated_duration": 480,  # 8小时
                    "dependencies": []
                },
                {
                    "id": "system_design",
                    "name": "系统设计",
                    "description": "设计系统架构、数据库结构、API接口等",
                    "task_type": "design",
                    "priority": 4,
                    "estimated_duration": 720,  # 12小时
                    "dependencies": ["requirements_analysis"]
                },
                {
                    "id": "development_setup",
                    "name": "开发环境搭建",
                    "description": "搭建开发环境、配置工具链、创建项目结构",
                    "task_type": "setup",
                    "priority": 3,
                    "estimated_duration": 240,  # 4小时
                    "dependencies": ["system_design"]
                },
                {
                    "id": "core_development",
                    "name": "核心功能开发",
                    "description": "开发核心业务逻辑和主要功能模块",
                    "task_type": "coding",
                    "priority": 4,
                    "estimated_duration": 2880,  # 48小时
                    "dependencies": ["development_setup"]
                },
                {
                    "id": "unit_testing",
                    "name": "单元测试",
                    "description": "编写和执行单元测试，确保代码质量",
                    "task_type": "testing",
                    "priority": 3,
                    "estimated_duration": 720,  # 12小时
                    "dependencies": ["core_development"]
                },
                {
                    "id": "integration_testing",
                    "name": "集成测试",
                    "description": "进行系统集成测试，验证模块间协作",
                    "task_type": "testing",
                    "priority": 3,
                    "estimated_duration": 480,  # 8小时
                    "dependencies": ["unit_testing"]
                },
                {
                    "id": "documentation",
                    "name": "文档编写",
                    "description": "编写用户手册、API文档、部署指南等",
                    "task_type": "documentation",
                    "priority": 2,
                    "estimated_duration": 360,  # 6小时
                    "dependencies": ["integration_testing"]
                },
                {
                    "id": "deployment",
                    "name": "部署上线",
                    "description": "部署到生产环境，配置监控和日志",
                    "task_type": "deployment",
                    "priority": 4,
                    "estimated_duration": 240,  # 4小时
                    "dependencies": ["documentation"]
                }
            ],
            "strategy": "dependency_based"
        }

    @staticmethod
    def research_project_plan(llm_client) -> Dict[str, Any]:
        """研究项目规划"""
        return {
            "name": "研究项目",
            "description": "学术或技术研究项目规划，包含文献调研、实验设计、数据分析等",
            "template_tasks": [
                {
                    "id": "literature_review",
                    "name": "文献调研",
                    "description": "收集和分析相关领域的研究文献",
                    "task_type": "research",
                    "priority": 4,
                    "estimated_duration": 1440,  # 24小时
                    "dependencies": []
                },
                {
                    "id": "problem_definition",
                    "name": "问题定义",
                    "description": "明确研究问题和假设，确定研究目标",
                    "task_type": "analysis",
                    "priority": 4,
                    "estimated_duration": 480,  # 8小时
                    "dependencies": ["literature_review"]
                },
                {
                    "id": "methodology_design",
                    "name": "方法设计",
                    "description": "设计实验方法、数据收集策略和分析方案",
                    "task_type": "design",
                    "priority": 4,
                    "estimated_duration": 720,  # 12小时
                    "dependencies": ["problem_definition"]
                },
                {
                    "id": "data_collection",
                    "name": "数据收集",
                    "description": "按照设计的方法收集实验数据",
                    "task_type": "data_collection",
                    "priority": 3,
                    "estimated_duration": 2160,  # 36小时
                    "dependencies": ["methodology_design"]
                },
                {
                    "id": "data_analysis",
                    "name": "数据分析",
                    "description": "使用统计方法和工具分析收集的数据",
                    "task_type": "analysis",
                    "priority": 4,
                    "estimated_duration": 1440,  # 24小时
                    "dependencies": ["data_collection"]
                },
                {
                    "id": "results_interpretation",
                    "name": "结果解释",
                    "description": "解释分析结果，验证或修正研究假设",
                    "task_type": "analysis",
                    "priority": 4,
                    "estimated_duration": 720,  # 12小时
                    "dependencies": ["data_analysis"]
                },
                {
                    "id": "paper_writing",
                    "name": "论文撰写",
                    "description": "撰写研究论文或报告",
                    "task_type": "writing",
                    "priority": 3,
                    "estimated_duration": 1440,  # 24小时
                    "dependencies": ["results_interpretation"]
                },
                {
                    "id": "peer_review",
                    "name": "同行评议",
                    "description": "提交论文进行同行评议和修改",
                    "task_type": "review",
                    "priority": 2,
                    "estimated_duration": 720,  # 12小时
                    "dependencies": ["paper_writing"]
                }
            ],
            "strategy": "dependency_based"
        }

    @staticmethod
    def product_launch_plan(llm_client) -> Dict[str, Any]:
        """产品发布规划"""
        return {
            "name": "产品发布",
            "description": "新产品上市规划，包含市场调研、产品开发、营销推广等",
            "template_tasks": [
                {
                    "id": "market_research",
                    "name": "市场调研",
                    "description": "分析目标市场、竞争对手和用户需求",
                    "task_type": "research",
                    "priority": 4,
                    "estimated_duration": 960,  # 16小时
                    "dependencies": []
                },
                {
                    "id": "product_positioning",
                    "name": "产品定位",
                    "description": "确定产品定位、目标用户和价值主张",
                    "task_type": "strategy",
                    "priority": 4,
                    "estimated_duration": 480,  # 8小时
                    "dependencies": ["market_research"]
                },
                {
                    "id": "feature_planning",
                    "name": "功能规划",
                    "description": "规划产品功能、优先级和发布计划",
                    "task_type": "planning",
                    "priority": 4,
                    "estimated_duration": 720,  # 12小时
                    "dependencies": ["product_positioning"]
                },
                {
                    "id": "mvp_development",
                    "name": "MVP开发",
                    "description": "开发最小可行产品进行市场验证",
                    "task_type": "development",
                    "priority": 4,
                    "estimated_duration": 2880,  # 48小时
                    "dependencies": ["feature_planning"]
                },
                {
                    "id": "user_testing",
                    "name": "用户测试",
                    "description": "进行用户测试收集反馈并优化产品",
                    "task_type": "testing",
                    "priority": 3,
                    "estimated_duration": 720,  # 12小时
                    "dependencies": ["mvp_development"]
                },
                {
                    "id": "marketing_strategy",
                    "name": "营销策略",
                    "description": "制定营销推广策略和渠道计划",
                    "task_type": "marketing",
                    "priority": 3,
                    "estimated_duration": 480,  # 8小时
                    "dependencies": ["user_testing"]
                },
                {
                    "id": "launch_preparation",
                    "name": "发布准备",
                    "description": "准备发布材料、培训团队、配置系统",
                    "task_type": "preparation",
                    "priority": 3,
                    "estimated_duration": 360,  # 6小时
                    "dependencies": ["marketing_strategy"]
                },
                {
                    "id": "product_launch",
                    "name": "正式发布",
                    "description": "执行产品发布，监控指标和用户反馈",
                    "task_type": "launch",
                    "priority": 4,
                    "estimated_duration": 240,  # 4小时
                    "dependencies": ["launch_preparation"]
                }
            ],
            "strategy": "dependency_based"
        }

    @staticmethod
    def learning_project_plan(llm_client) -> Dict[str, Any]:
        """学习项目规划"""
        return {
            "name": "学习项目",
            "description": "个人或团队学习项目规划，包含目标设定、资源收集、实践练习等",
            "template_tasks": [
                {
                    "id": "learning_goals",
                    "name": "学习目标设定",
                    "description": "明确学习目标、时间安排和成功标准",
                    "task_type": "planning",
                    "priority": 4,
                    "estimated_duration": 120,  # 2小时
                    "dependencies": []
                },
                {
                    "id": "resource_collection",
                    "name": "资源收集",
                    "description": "收集学习资料、书籍、课程和工具",
                    "task_type": "research",
                    "priority": 3,
                    "estimated_duration": 240,  # 4小时
                    "dependencies": ["learning_goals"]
                },
                {
                    "id": "study_plan",
                    "name": "学习计划制定",
                    "description": "制定详细的学习计划和时间表",
                    "task_type": "planning",
                    "priority": 3,
                    "estimated_duration": 180,  # 3小时
                    "dependencies": ["resource_collection"]
                },
                {
                    "id": "theoretical_learning",
                    "name": "理论学习",
                    "description": "学习理论知识和基础概念",
                    "task_type": "learning",
                    "priority": 4,
                    "estimated_duration": 2400,  # 40小时
                    "dependencies": ["study_plan"]
                },
                {
                    "id": "practical_exercises",
                    "name": "实践练习",
                    "description": "通过练习和项目应用所学知识",
                    "task_type": "practice",
                    "priority": 4,
                    "estimated_duration": 1800,  # 30小时
                    "dependencies": ["theoretical_learning"]
                },
                {
                    "id": "knowledge_assessment",
                    "name": "知识评估",
                    "description": "通过测试或项目评估学习效果",
                    "task_type": "assessment",
                    "priority": 3,
                    "estimated_duration": 360,  # 6小时
                    "dependencies": ["practical_exercises"]
                },
                {
                    "id": "knowledge_sharing",
                    "name": "知识分享",
                    "description": "通过教学或分享巩固所学知识",
                    "task_type": "sharing",
                    "priority": 2,
                    "estimated_duration": 240,  # 4小时
                    "dependencies": ["knowledge_assessment"]
                }
            ],
            "strategy": "sequential"
        }

    @staticmethod
    def get_all_scenarios(llm_client) -> Dict[str, Dict[str, Any]]:
        """获取所有预定义场景"""
        return {
            "software_development": ProjectPlanningScenarios.software_development_plan(llm_client),
            "research_project": ProjectPlanningScenarios.research_project_plan(llm_client),
            "product_launch": ProjectPlanningScenarios.product_launch_plan(llm_client),
            "learning_project": ProjectPlanningScenarios.learning_project_plan(llm_client)
        }


class PlanningTaskHandlers:
    """Planning任务处理器集合"""

    @staticmethod
    def analysis_handler(task: Task) -> str:
        """分析类任务处理器"""
        return f"完成分析任务: {task.name}\n分析结果: 已完成对 '{task.description}' 的详细分析"

    @staticmethod
    def design_handler(task: Task) -> str:
        """设计类任务处理器"""
        return f"完成设计任务: {task.name}\n设计输出: 已完成 '{task.description}' 的设计方案"

    @staticmethod
    def coding_handler(task: Task) -> str:
        """编程类任务处理器"""
        return f"完成编程任务: {task.name}\n代码输出: 已完成 '{task.description}' 的代码实现"

    @staticmethod
    def testing_handler(task: Task) -> str:
        """测试类任务处理器"""
        return f"完成测试任务: {task.name}\n测试结果: 已完成 '{task.description}' 的测试验证"

    @staticmethod
    def documentation_handler(task: Task) -> str:
        """文档类任务处理器"""
        return f"完成文档任务: {task.name}\n文档输出: 已完成 '{task.description}' 的文档编写"

    @staticmethod
    def research_handler(task: Task) -> str:
        """研究类任务处理器"""
        return f"完成研究任务: {task.name}\n研究成果: 已完成 '{task.description}' 的研究工作"

    @staticmethod
    def register_all_handlers(agent: PlanningAgent):
        """注册所有预定义的任务处理器"""
        handlers = {
            "analysis": PlanningTaskHandlers.analysis_handler,
            "design": PlanningTaskHandlers.design_handler,
            "coding": PlanningTaskHandlers.coding_handler,
            "development": PlanningTaskHandlers.coding_handler,
            "testing": PlanningTaskHandlers.testing_handler,
            "documentation": PlanningTaskHandlers.documentation_handler,
            "research": PlanningTaskHandlers.research_handler,
            "planning": PlanningTaskHandlers.analysis_handler,
            "strategy": PlanningTaskHandlers.analysis_handler,
            "marketing": PlanningTaskHandlers.analysis_handler,
            "learning": PlanningTaskHandlers.research_handler,
            "practice": PlanningTaskHandlers.coding_handler,
            "assessment": PlanningTaskHandlers.testing_handler,
            "sharing": PlanningTaskHandlers.documentation_handler,
            "setup": PlanningTaskHandlers.coding_handler,
            "deployment": PlanningTaskHandlers.coding_handler,
            "data_collection": PlanningTaskHandlers.research_handler,
            "writing": PlanningTaskHandlers.documentation_handler,
            "review": PlanningTaskHandlers.analysis_handler,
            "preparation": PlanningTaskHandlers.analysis_handler,
            "launch": PlanningTaskHandlers.coding_handler
        }
        
        for task_type, handler in handlers.items():
            agent.register_task_handler(task_type, handler)
