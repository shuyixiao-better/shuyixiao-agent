"""
Web 应用服务

提供 FastAPI 服务来支持前端界面与 Agent 交互
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import os
from datetime import datetime
import json
import re
import hashlib
from pathlib import Path
from langchain_core.messages import HumanMessage

from .agents.simple_agent import SimpleAgent
from .agents.tool_agent import ToolAgent
from .agents.prompt_chaining_agent import (
    PromptChainingAgent,
    DocumentGenerationChain,
    CodeReviewChain,
    ResearchPlanningChain,
    StoryCreationChain,
    ProductAnalysisChain
)
from .agents.routing_agent import (
    RoutingAgent,
    RoutingStrategy,
    SmartAssistantRoutes,
    DeveloperAssistantRoutes
)
from .agents.parallelization_agent import (
    ParallelizationAgent,
    ParallelStrategy,
    AggregationMethod,
    ParallelTask,
    MultiPerspectiveAnalysis,
    ParallelTranslation,
    ParallelContentGeneration,
    ParallelCodeReview,
    ParallelResearch,
    ConsensusGenerator
)
from .agents.reflection_agent import (
    ReflectionAgent,
    ReflectionStrategy,
    ReflectionCriteria,
    ContentReflection,
    CodeReflection,
    AnalysisReflection,
    TranslationReflection
)
from .agents.tool_use_agent import (
    ToolUseAgent,
    ToolType,
    ToolDefinition,
    ToolParameter,
    ToolExecutionResult
)
from .agents.planning_agent import (
    PlanningAgent,
    PlanningStrategy,
    TaskStatus,
    TaskPriority,
    ProjectPlanningScenarios,
    PlanningTaskHandlers
)
from .agents.multi_agent_collaboration import (
    MultiAgentCollaboration,
    CollaborationMode,
    AgentRole,
    AgentProfile,
    SoftwareDevelopmentTeam,
    ResearchTeam,
    ContentCreationTeam,
    BusinessConsultingTeam
)
from .agents.memory_agent import (
    MemoryAgent,
    MemoryType,
    MemoryImportance,
    MemoryStrategy,
    Memory
)
from .tools.predefined_tools import PredefinedToolsRegistry
from .tools.basic_tools import get_basic_tools
from .config import settings
from .gitee_ai_client import GiteeAIClient
from .database_helper import DatabaseHelper

# RAG Agent 延迟导入，避免阻塞启动
# 使用 TYPE_CHECKING 来支持类型注解而不影响运行时
if TYPE_CHECKING:
    from .rag.rag_agent import RAGAgent

# 创建 FastAPI 应用
app = FastAPI(
    title="ShuYixiao Agent Web Interface",
    description="基于 LangGraph 和码云 AI 的智能 Agent Web 界面",
    version="0.1.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print("=" * 60)
    print("🚀 ShuYixiao Agent Web 应用正在启动...")
    print("=" * 60)
    
    # 初始化数据库（修复权限、清理临时文件）
    db_initialized = DatabaseHelper.initialize_database(
        db_path=settings.vector_db_path,
        cleanup_temp=True
    )
    
    if not db_initialized:
        print("⚠️  警告：数据库初始化失败，可能会遇到权限问题")
    
    # 显示数据库健康状态
    health = DatabaseHelper.check_database_health(settings.vector_db_path)
    print(f"📊 数据库状态: 存在={health['exists']}, 可读={health['readable']}, 可写={health['writable']}")
    print(f"📦 数据库大小: {health['size_mb']} MB, 文件数: {health['file_count']}")
    
    # 从数据库恢复知识库名称映射关系
    print("🔄 正在恢复知识库名称映射关系...")
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        
        client = chromadb.PersistentClient(
            path=settings.vector_db_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        collections = client.list_collections()
        
        # 从配置文件加载已知映射（用于旧数据）
        known_mappings = {}
        mapping_file = Path(__file__).parent.parent.parent / "knowledge_base_mappings.json"
        if mapping_file.exists():
            try:
                import json
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    known_mappings = config.get('mappings', {})
                    print(f"  📄 已加载配置文件: {len(known_mappings)} 个预定义映射")
            except Exception as e:
                print(f"  ⚠️  加载配置文件失败: {e}")
        
        # 如果配置文件不存在，使用默认映射
        if not known_mappings:
            known_mappings = {
                "kb_dd65ff91_kb": "舒一笑个人信息",  # 默认映射
            }
        
        for collection in collections:
            try:
                # 从collection的metadata中读取原始名称
                metadata = collection.metadata or {}
                original_name = metadata.get('original_name')
                
                if original_name and original_name != collection.name:
                    collection_name_mapping[original_name] = collection.name
                    print(f"  ✓ 恢复映射(从metadata): '{original_name}' -> '{collection.name}'")
                elif collection.name in known_mappings:
                    # 对于旧数据，使用预定义映射
                    original_name = known_mappings[collection.name]
                    collection_name_mapping[original_name] = collection.name
                    print(f"  ✓ 恢复映射(已知旧数据): '{original_name}' -> '{collection.name}'")
            except Exception as e:
                print(f"  ⚠️  处理collection {collection.name} 时出错: {e}")
        
        print(f"✅ 已恢复 {len(collection_name_mapping)} 个名称映射关系")
    except Exception as e:
        print(f"⚠️  恢复名称映射失败: {e}")
    
    print("=" * 60)
    print("✅ ShuYixiao Agent Web 应用已启动")
    print("=" * 60)
    print(f"API Key 已配置: {bool(settings.gitee_ai_api_key)}")
    print(f"使用模型: {settings.gitee_ai_model}")
    print(f"数据库路径: {settings.vector_db_path}")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("👋 ShuYixiao Agent Web 应用已关闭")

# Agent 实例缓存
agents: Dict[str, Any] = {}

# RAG Agent 实例缓存
rag_agents: Dict[str, Any] = {}

# Prompt Chaining Agent 实例缓存
prompt_chaining_agent: Optional[PromptChainingAgent] = None

# Routing Agent 实例缓存
routing_agents: Dict[str, RoutingAgent] = {}

# Parallelization Agent 实例缓存
parallelization_agent: Optional[ParallelizationAgent] = None

# Reflection Agent 实例缓存
reflection_agent: Optional[ReflectionAgent] = None

# Memory Agent 实例缓存
memory_agents: Dict[str, MemoryAgent] = {}

# 会话消息历史（简单实现，生产环境应使用数据库）
session_histories: Dict[str, List[Dict[str, str]]] = {}

# 知识库名称映射（原始名称 -> 合法名称）
collection_name_mapping: Dict[str, str] = {}


def normalize_collection_name(name: str) -> str:
    """
    将用户输入的名称转换为符合 ChromaDB 要求的合法名称
    
    ChromaDB 要求：
    - 3-512 个字符
    - 只包含 [a-zA-Z0-9._-]
    - 必须以 [a-zA-Z0-9] 开头和结尾
    
    Args:
        name: 用户输入的名称
        
    Returns:
        合法的集合名称
    """
    # 如果已经是合法名称，直接返回
    if re.match(r'^[a-zA-Z0-9][a-zA-Z0-9._-]{1,510}[a-zA-Z0-9]$', name):
        return name
    
    # 如果名称已经被映射过，返回之前的映射
    if name in collection_name_mapping:
        return collection_name_mapping[name]
    
    # 生成一个基于原始名称的哈希值（作为唯一标识）
    name_hash = hashlib.md5(name.encode('utf-8')).hexdigest()[:8]
    
    # 尝试从名称中提取合法字符作为前缀（提高可读性）
    safe_prefix = re.sub(r'[^a-zA-Z0-9._-]', '', name)
    
    # 移除前后的非法字符
    safe_prefix = safe_prefix.strip('._-')
    
    # 如果没有合法字符或太短，使用有意义的默认前缀
    if not safe_prefix or len(safe_prefix) < 2:
        safe_prefix = "kb"  # knowledge base
    else:
        # 限制前缀长度，为哈希值留出空间
        safe_prefix = safe_prefix[:20]
    
    # 组合前缀和哈希值（哈希值确保唯一性，前缀提高可读性）
    normalized_name = f"{safe_prefix}_{name_hash}"
    
    # 最终验证：确保以字母或数字开头和结尾
    if not re.match(r'^[a-zA-Z0-9]', normalized_name):
        normalized_name = "kb_" + normalized_name
    if not re.match(r'[a-zA-Z0-9]$', normalized_name):
        normalized_name = normalized_name + "_kb"
    
    # 确保长度在范围内
    if len(normalized_name) < 3:
        normalized_name = "kb_" + name_hash + "_default"
    elif len(normalized_name) > 512:
        normalized_name = normalized_name[:512]
        # 确保截断后仍以字母或数字结尾
        if not re.match(r'[a-zA-Z0-9]$', normalized_name):
            normalized_name = normalized_name.rstrip('._-')
    
    # 保存映射关系
    collection_name_mapping[name] = normalized_name
    
    print(f"[知识库名称] '{name}' -> '{normalized_name}'")
    
    return normalized_name


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    agent_type: str = "simple"  # simple, tool, rag, 或 prompt_chaining
    session_id: Optional[str] = "default"
    system_message: Optional[str] = None
    collection_name: Optional[str] = "default"  # RAG 专用：知识库集合名


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str
    agent_type: str
    session_id: str


class SessionHistoryResponse(BaseModel):
    """会话历史响应模型"""
    session_id: str
    messages: List[Dict[str, str]]


class DocumentUploadRequest(BaseModel):
    """文档上传请求模型"""
    file_path: str
    collection_name: Optional[str] = "default"


class DirectoryUploadRequest(BaseModel):
    """目录上传请求模型"""
    directory_path: str
    glob_pattern: Optional[str] = "**/*.*"
    collection_name: Optional[str] = "default"


class TextUploadRequest(BaseModel):
    """文本上传请求模型"""
    texts: List[str]
    metadatas: Optional[List[Dict[str, Any]]] = None
    collection_name: Optional[str] = "default"


class RAGQueryRequest(BaseModel):
    """RAG 查询请求模型"""
    question: str
    collection_name: Optional[str] = "default"
    session_id: Optional[str] = "default"
    top_k: Optional[int] = None
    use_history: bool = True
    optimize_query: bool = True


class PromptChainingRequest(BaseModel):
    """Prompt Chaining 请求模型"""
    input_text: str
    chain_type: str  # document_gen, code_review, research, story, product
    save_result: bool = True


class RoutingRequest(BaseModel):
    """Routing 请求模型"""
    input_text: str
    scenario: str = "smart_assistant"  # smart_assistant, developer_assistant, custom
    strategy: str = "hybrid"  # rule_based, keyword, llm_based, hybrid
    verbose: bool = False


class ParallelizationRequest(BaseModel):
    """Parallelization 请求模型"""
    scenario: str  # multi_perspective, translation, content_gen, code_review, research, consensus, custom
    input_text: str
    strategy: str = "full_parallel"  # full_parallel, batch_parallel, pipeline, vote, ensemble
    aggregation: str = "summarize"  # merge, concat, first, best, summarize, vote, consensus
    perspectives: Optional[List[str]] = None  # 用于 multi_perspective
    languages: Optional[List[str]] = None  # 用于 translation
    sections: Optional[List[str]] = None  # 用于 content_gen
    aspects: Optional[List[str]] = None  # 用于 research
    num_generations: Optional[int] = 5  # 用于 consensus
    batch_size: int = 3
    max_workers: int = 5


class ReflectionRequest(BaseModel):
    """Reflection 请求模型"""
    task: str
    initial_content: Optional[str] = None
    strategy: str = "simple"  # simple, multi_aspect, debate, expert
    scenario: Optional[str] = None  # content, code, analysis, translation
    max_iterations: int = 3
    score_threshold: float = 0.85
    expert_role: Optional[str] = None  # 用于 expert 策略
    expert_expertise: Optional[str] = None  # 用于 expert 策略


class ToolUseRequest(BaseModel):
    """Tool Use 请求模型"""
    user_input: str
    max_iterations: int = 5
    tool_type: Optional[str] = None  # 可选的工具类型过滤


class ToolExecuteRequest(BaseModel):
    """工具执行请求模型"""
    tool_name: str
    parameters: Dict[str, Any]


class PlanningRequest(BaseModel):
    """规划请求模型"""
    goal: str
    context: Optional[Dict[str, Any]] = None
    scenario: Optional[str] = None  # 预定义场景
    strategy: Optional[str] = "adaptive"  # 规划策略
    auto_execute: bool = False  # 是否自动执行


class PlanExecutionRequest(BaseModel):
    """计划执行请求模型"""
    plan_id: str


def get_agent(agent_type: str, system_message: Optional[str] = None):
    """获取或创建 Agent 实例"""
    cache_key = f"{agent_type}_{system_message or 'default'}"
    
    if cache_key not in agents:
        if agent_type == "simple":
            agents[cache_key] = SimpleAgent(
                system_message=system_message or "你是一个有帮助的AI助手，请友好、专业地回答用户的问题。"
            )
        elif agent_type == "tool":
            agent = ToolAgent(
                system_message=system_message or "你是一个有帮助的AI助手。你可以使用提供的工具来完成任务。"
            )
            # 注册基础工具
            for tool_info in get_basic_tools():
                agent.register_tool(
                    name=tool_info["name"],
                    func=tool_info["func"],
                    description=tool_info["description"],
                    parameters=tool_info["parameters"]
                )
            agents[cache_key] = agent
        elif agent_type == "tool_use":
            agent = ToolUseAgent(
                llm_client=GiteeAIClient(),
                verbose=True
            )
            # 注册所有预定义工具
            PredefinedToolsRegistry.register_all_tools(agent)
            agents[cache_key] = agent
        elif agent_type == "planning":
            agent = PlanningAgent(
                llm_client=GiteeAIClient(),
                strategy=PlanningStrategy.ADAPTIVE,
                verbose=True
            )
            # 注册所有预定义的任务处理器
            PlanningTaskHandlers.register_all_handlers(agent)
            agents[cache_key] = agent
        else:
            raise ValueError(f"未知的 agent 类型: {agent_type}")
    
    return agents[cache_key]


def get_rag_agent(collection_name: str = "default"):
    """获取或创建 RAG Agent 实例（延迟加载）"""
    # 转换为合法的集合名称
    normalized_name = normalize_collection_name(collection_name)
    
    # 使用转换后的名称作为缓存键
    if normalized_name not in rag_agents:
        # 延迟导入 RAG Agent
        from .rag.rag_agent import RAGAgent
        
        print(f"[信息] 首次创建 RAG Agent: {collection_name} (实际集合: {normalized_name})")
        rag_agents[normalized_name] = RAGAgent(
            collection_name=normalized_name,
            system_message="你是一个有帮助的AI助手。请基于提供的文档内容回答用户的问题。",
            use_reranker=True,
            retrieval_mode="hybrid",
            enable_query_optimization=True,
            enable_context_expansion=True,
            original_name=collection_name  # 传递原始名称用于持久化
        )
        print(f"[成功] RAG Agent 创建完成: {normalized_name}")
    
    return rag_agents[normalized_name]


def get_prompt_chaining_agent():
    """获取或创建 Prompt Chaining Agent 实例"""
    global prompt_chaining_agent
    
    if prompt_chaining_agent is None:
        llm_client = GiteeAIClient()
        prompt_chaining_agent = PromptChainingAgent(llm_client, verbose=False)
        print("[信息] Prompt Chaining Agent 已创建")
    
    return prompt_chaining_agent


def get_routing_agent(scenario: str = "smart_assistant", strategy: str = "hybrid"):
    """获取或创建 Routing Agent 实例"""
    cache_key = f"{scenario}_{strategy}"
    
    if cache_key not in routing_agents:
        llm_client = GiteeAIClient()
        agent = RoutingAgent(
            llm_client=llm_client,
            strategy=RoutingStrategy(strategy),
            verbose=False
        )
        
        # 根据场景注册路由
        if scenario == "smart_assistant":
            routes = SmartAssistantRoutes.get_routes(llm_client)
            agent.register_routes(routes)
        elif scenario == "developer_assistant":
            routes = DeveloperAssistantRoutes.get_routes(llm_client)
            agent.register_routes(routes)
        
        routing_agents[cache_key] = agent
        print(f"[信息] Routing Agent 已创建: {scenario} ({strategy})")
    
    return routing_agents[cache_key]


def get_parallelization_agent(max_workers: int = 5):
    """获取或创建 Parallelization Agent 实例"""
    global parallelization_agent
    
    if parallelization_agent is None or parallelization_agent.max_workers != max_workers:
        llm_client = GiteeAIClient()
        parallelization_agent = ParallelizationAgent(
            llm_client=llm_client,
            max_workers=max_workers,
            verbose=False
        )
        print(f"[信息] Parallelization Agent 已创建 (max_workers={max_workers})")
    
    return parallelization_agent


def get_reflection_agent(max_iterations: int = 3, score_threshold: float = 0.85):
    """获取或创建 Reflection Agent 实例"""
    global reflection_agent
    
    if (reflection_agent is None or 
        reflection_agent.max_iterations != max_iterations or
        reflection_agent.score_threshold != score_threshold):
        llm_client = GiteeAIClient()
        reflection_agent = ReflectionAgent(
            llm_client=llm_client,
            max_iterations=max_iterations,
            score_threshold=score_threshold,
            verbose=False
        )
        print(f"[信息] Reflection Agent 已创建 (max_iterations={max_iterations}, threshold={score_threshold})")
    
    return reflection_agent


def get_memory_agent(session_id: str = "default", max_memories: int = 1000):
    """获取或创建 Memory Agent 实例"""
    cache_key = f"{session_id}_{max_memories}"
    
    if cache_key not in memory_agents:
        llm_client = GiteeAIClient()
        
        # 为每个会话创建独立的存储路径
        storage_path = f"data/memories/memory_{session_id}.json"
        
        memory_agents[cache_key] = MemoryAgent(
            llm_client=llm_client,
            max_memories=max_memories,
            strategy=MemoryStrategy.HYBRID,
            verbose=False,
            storage_path=storage_path
        )
        print(f"[信息] Memory Agent 已创建 (session={session_id}, max_memories={max_memories})")
    
    return memory_agents[cache_key]


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回前端 HTML 页面"""
    print(f"[请求] GET / - 返回主页")
    
    static_dir = Path(__file__).parent / "static"
    html_file = static_dir / "index.html"
    
    print(f"[信息] 静态文件目录: {static_dir}")
    print(f"[信息] HTML 文件路径: {html_file}")
    print(f"[信息] 文件存在: {html_file.exists()}")
    
    if html_file.exists():
        content = html_file.read_text(encoding="utf-8")
        print(f"[成功] 返回 HTML 文件, 大小: {len(content)} 字符")
        return HTMLResponse(content=content)
    else:
        print(f"[警告] HTML 文件不存在: {html_file}")
        return HTMLResponse(content="""
        <html>
            <body>
                <h1>前端页面未找到</h1>
                <p>请确保 static/index.html 文件存在</p>
            </body>
        </html>
        """)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理聊天请求（非流式）"""
    try:
        # 获取 Agent
        agent = get_agent(request.agent_type, request.system_message)
        
        # 初始化会话历史
        if request.session_id not in session_histories:
            session_histories[request.session_id] = []
        
        # 添加用户消息到历史
        session_histories[request.session_id].append({
            "role": "user",
            "content": request.message
        })
        
        # 调用 Agent
        if request.agent_type == "simple":
            response = agent.chat(request.message)
        else:  # tool agent
            response = agent.run(request.message)
        
        # 添加 AI 回复到历史
        session_histories[request.session_id].append({
            "role": "assistant",
            "content": response
        })
        
        return ChatResponse(
            response=response,
            agent_type=request.agent_type,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """处理聊天请求（流式）"""
    
    async def generate():
        try:
            # 初始化会话历史
            if request.session_id not in session_histories:
                session_histories[request.session_id] = []
            
            # 添加用户消息到历史
            session_histories[request.session_id].append({
                "role": "user",
                "content": request.message
            })
            
            # 构建消息历史
            messages = []
            
            # 添加系统消息
            system_message = request.system_message or "你是一个有帮助的AI助手，请友好、专业地回答用户的问题。"
            messages.append({
                "role": "system",
                "content": system_message
            })
            
            # 添加历史消息（最近10条）
            recent_history = session_histories[request.session_id][-10:]
            messages.extend(recent_history)
            
            # 创建客户端并调用流式API
            client = GiteeAIClient()
            full_response = ""
            
            # 对于工具调用模式，暂时使用非流式（因为需要处理工具调用）
            if request.agent_type == "tool":
                agent = get_agent(request.agent_type, request.system_message)
                response = agent.run(request.message)
                full_response = response
                
                # 一次性发送
                yield f"data: {json.dumps({'content': response, 'done': True}, ensure_ascii=False)}\n\n"
            else:
                # 简单对话模式使用流式
                stream = client.chat_completion(messages=messages, stream=True)
                
                for chunk in stream:
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        
                        if content:
                            full_response += content
                            # 发送数据块
                            yield f"data: {json.dumps({'content': content, 'done': False}, ensure_ascii=False)}\n\n"
                
                # 发送完成信号
                yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"
            
            # 添加完整回复到历史
            session_histories[request.session_id].append({
                "role": "assistant",
                "content": full_response
            })
            
        except Exception as e:
            error_msg = f"处理请求时出错: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg, 'done': True}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/history/{session_id}", response_model=SessionHistoryResponse)
async def get_history(session_id: str):
    """获取会话历史"""
    if session_id not in session_histories:
        session_histories[session_id] = []
    
    return SessionHistoryResponse(
        session_id=session_id,
        messages=session_histories[session_id]
    )


@app.delete("/api/history/{session_id}")
async def clear_history(session_id: str):
    """清除会话历史"""
    if session_id in session_histories:
        session_histories[session_id] = []
    return {"message": "历史已清除", "session_id": session_id}


@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    print(f"[请求] GET /api/health - 健康检查")
    result = {
        "status": "healthy",
        "api_key_configured": bool(settings.gitee_ai_api_key),
        "model": settings.gitee_ai_model
    }
    print(f"[响应] 健康检查: {result}")
    return result


# ========== RAG 相关接口 ==========

@app.post("/api/rag/upload/file")
async def upload_file(request: DocumentUploadRequest):
    """上传单个文件到知识库"""
    try:
        # 获取规范化后的集合名称
        normalized_name = normalize_collection_name(request.collection_name)
        agent = get_rag_agent(request.collection_name)
        count = agent.add_documents_from_file(
            request.file_path,
            show_progress=True
        )
        
        return {
            "message": "文件上传成功",
            "collection_name": normalized_name,  # 返回规范化后的名称
            "original_name": request.collection_name,  # 保留原始名称
            "chunks_added": count,
            "total_documents": agent.get_document_count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传文件失败: {str(e)}")


@app.post("/api/rag/upload/directory")
async def upload_directory(request: DirectoryUploadRequest):
    """上传整个目录到知识库"""
    try:
        # 获取规范化后的集合名称
        normalized_name = normalize_collection_name(request.collection_name)
        agent = get_rag_agent(request.collection_name)
        count = agent.add_documents_from_directory(
            request.directory_path,
            request.glob_pattern,
            show_progress=True
        )
        
        return {
            "message": "目录上传成功",
            "collection_name": normalized_name,  # 返回规范化后的名称
            "original_name": request.collection_name,  # 保留原始名称
            "chunks_added": count,
            "total_documents": agent.get_document_count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传目录失败: {str(e)}")


@app.post("/api/rag/upload/texts")
async def upload_texts(request: TextUploadRequest):
    """上传文本列表到知识库"""
    try:
        # 获取规范化后的集合名称
        normalized_name = normalize_collection_name(request.collection_name)
        agent = get_rag_agent(request.collection_name)
        count = agent.add_texts(
            request.texts,
            request.metadatas
        )
        
        return {
            "message": "文本上传成功",
            "collection_name": normalized_name,  # 返回规范化后的名称
            "original_name": request.collection_name,  # 保留原始名称
            "chunks_added": count,
            "total_documents": agent.get_document_count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传文本失败: {str(e)}")


@app.post("/api/rag/query")
async def rag_query(request: RAGQueryRequest):
    """RAG 查询（非流式）"""
    try:
        agent = get_rag_agent(request.collection_name)
        
        answer = agent.query(
            question=request.question,
            top_k=request.top_k,
            use_history=request.use_history,
            optimize_query=request.optimize_query,
            stream=False
        )
        
        return {
            "answer": answer,
            "collection_name": request.collection_name,
            "session_id": request.session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@app.post("/api/rag/query/stream")
async def rag_query_stream(request: RAGQueryRequest):
    """RAG 查询（流式）"""
    
    async def generate():
        try:
            agent = get_rag_agent(request.collection_name)
            
            # 获取流式响应
            stream = agent.query(
                question=request.question,
                top_k=request.top_k,
                use_history=request.use_history,
                optimize_query=request.optimize_query,
                stream=True
            )
            
            # 发送流式数据
            for chunk in stream:
                yield f"data: {json.dumps({'content': chunk, 'done': False}, ensure_ascii=False)}\n\n"
            
            # 发送完成信号
            yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            error_msg = f"查询失败: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg, 'done': True}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/rag/info/{collection_name}")
async def get_rag_info(collection_name: str):
    """获取 RAG 知识库信息"""
    try:
        # 获取规范化后的名称
        normalized_name = normalize_collection_name(collection_name)
        agent = get_rag_agent(collection_name)
        
        # 查找原始名称（反向映射）
        original_name = collection_name
        for orig, norm in collection_name_mapping.items():
            if norm == normalized_name:
                original_name = orig
                break
        
        return {
            "collection_name": normalized_name,
            "original_name": original_name if original_name != normalized_name else None,
            "is_normalized": original_name != normalized_name,
            "document_count": agent.get_document_count(),
            "retrieval_mode": agent.retrieval_mode
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取信息失败: {str(e)}")


@app.get("/api/rag/mappings")
async def get_collection_mappings():
    """获取所有知识库名称映射关系"""
    try:
        mappings = []
        for original_name, normalized_name in collection_name_mapping.items():
            # 尝试获取文档数量
            try:
                if normalized_name in rag_agents:
                    agent = rag_agents[normalized_name]
                    doc_count = agent.get_document_count()
                else:
                    doc_count = None
            except:
                doc_count = None
            
            mappings.append({
                "original_name": original_name,
                "normalized_name": normalized_name,
                "document_count": doc_count
            })
        
        return {
            "mappings": mappings,
            "total_count": len(mappings)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取映射失败: {str(e)}")


@app.delete("/api/rag/clear/{collection_name}")
async def clear_rag_knowledge_base(collection_name: str):
    """清空 RAG 知识库"""
    try:
        agent = get_rag_agent(collection_name)
        agent.clear_knowledge_base()
        
        return {
            "message": "知识库已清空",
            "collection_name": collection_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空知识库失败: {str(e)}")


@app.delete("/api/rag/history/{collection_name}/{session_id}")
async def clear_rag_history(collection_name: str, session_id: str):
    """清空 RAG 对话历史"""
    try:
        agent = get_rag_agent(collection_name)
        agent.clear_history()
        
        return {
            "message": "对话历史已清空",
            "collection_name": collection_name,
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空历史失败: {str(e)}")


@app.get("/api/rag/documents/{collection_name}")
async def list_documents(
    collection_name: str,
    limit: Optional[int] = None,
    offset: Optional[int] = None
):
    """列出知识库中的文档"""
    try:
        agent = get_rag_agent(collection_name)
        documents = agent.list_documents(limit=limit, offset=offset)
        
        return {
            "collection_name": collection_name,
            "total_count": agent.get_document_count(),
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")


@app.get("/api/rag/document/{collection_name}/{doc_id}")
async def get_document(collection_name: str, doc_id: str):
    """获取单个文档内容"""
    try:
        agent = get_rag_agent(collection_name)
        document = agent.get_document_by_id(doc_id)
        
        if document is None:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        return {
            "collection_name": collection_name,
            "document": document
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档失败: {str(e)}")


@app.delete("/api/rag/document/{collection_name}/{doc_id}")
async def delete_document(collection_name: str, doc_id: str):
    """删除指定文档"""
    try:
        agent = get_rag_agent(collection_name)
        success = agent.delete_document(doc_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="文档不存在或删除失败")
        
        return {
            "message": "文档已删除",
            "collection_name": collection_name,
            "document_id": doc_id,
            "remaining_count": agent.get_document_count()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")


@app.get("/api/rag/collections")
async def list_collections():
    """列出所有已存在的知识库集合"""
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        
        print(f"[列出Collections] 开始扫描数据库路径: {settings.vector_db_path}")
        
        # 创建客户端连接到持久化目录
        client = chromadb.PersistentClient(
            path=settings.vector_db_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 获取所有集合
        collections = client.list_collections()
        print(f"[列出Collections] 找到 {len(collections)} 个集合")
        
        result = []
        for collection in collections:
            try:
                collection_name = collection.name
                doc_count = collection.count()
                
                print(f"[列出Collections] 处理集合: {collection_name}, 文档数: {doc_count}")
                
                # 优先从collection metadata中读取原始名称
                metadata = collection.metadata or {}
                original_name = metadata.get('original_name')
                
                # 如果metadata中没有，尝试从内存映射表中查找（包括预定义的旧数据映射）
                if not original_name:
                    for orig, norm in collection_name_mapping.items():
                        if norm == collection_name:
                            original_name = orig
                            break
                
                # 如果还是没有原始名称，说明该collection名称本身就是合法的
                if not original_name:
                    original_name = collection_name
                
                is_normalized = original_name != collection_name
                
                print(f"[列出Collections] 集合: {collection_name}, 原始名称: {original_name}, 是否转换: {is_normalized}")
                
                result.append({
                    "collection_name": collection_name,
                    "original_name": original_name if is_normalized else None,
                    "document_count": doc_count,
                    "is_normalized": is_normalized
                })
            except Exception as coll_error:
                print(f"[列出Collections] 处理集合 {collection.name} 时出错: {coll_error}")
                # 继续处理其他集合
                continue
        
        print(f"[列出Collections] 成功返回 {len(result)} 个集合信息")
        return {
            "collections": result,
            "total_count": len(result)
        }
    except Exception as e:
        import traceback
        error_detail = f"获取集合列表失败: {str(e)}\n{traceback.format_exc()}"
        print(f"[列出Collections] 错误: {error_detail}")
        raise HTTPException(status_code=500, detail=f"获取集合列表失败: {str(e)}")


class BatchDeleteRequest(BaseModel):
    """批量删除请求模型"""
    doc_ids: List[str]
    collection_name: str


@app.delete("/api/rag/documents/batch")
async def batch_delete_documents(request: BatchDeleteRequest):
    """批量删除文档（物理删除）"""
    try:
        agent = get_rag_agent(request.collection_name)
        
        # 使用优化的批量删除方法
        success_count, failed_ids = agent.batch_delete_documents(request.doc_ids)
        
        return {
            "message": f"批量删除完成（已物理删除）",
            "collection_name": request.collection_name,
            "success_count": success_count,
            "failed_count": len(failed_ids),
            "failed_ids": failed_ids,
            "remaining_count": agent.get_document_count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量删除失败: {str(e)}")


# ========== Prompt Chaining 相关接口 ==========

@app.post("/api/prompt-chaining/run")
async def run_prompt_chain(request: PromptChainingRequest):
    """运行提示链（非流式）"""
    try:
        agent = get_prompt_chaining_agent()
        
        # 根据类型选择对应的链
        chain_types = {
            "document_gen": ("文档生成", DocumentGenerationChain.get_steps()),
            "code_review": ("代码审查", CodeReviewChain.get_steps()),
            "research": ("研究规划", ResearchPlanningChain.get_steps()),
            "story": ("故事创作", StoryCreationChain.get_steps()),
            "product": ("产品分析", ProductAnalysisChain.get_steps())
        }
        
        if request.chain_type not in chain_types:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的链类型: {request.chain_type}"
            )
        
        chain_name, steps = chain_types[request.chain_type]
        
        # 创建并运行链
        agent.create_chain(request.chain_type, steps)
        result = agent.run_chain(request.chain_type, request.input_text)
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"链执行失败: {result.error_message}"
            )
        
        # 可选：保存结果到文件
        output_file = None
        if request.save_result:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"prompt_chain_{request.chain_type}_{timestamp}.md"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# {chain_name}结果\n\n")
                f.write(f"**输入:** {request.input_text}\n\n")
                f.write(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                f.write(result.final_output)
        
        return {
            "success": True,
            "chain_type": request.chain_type,
            "chain_name": chain_name,
            "final_output": result.final_output,
            "total_steps": result.total_steps,
            "execution_time": result.execution_time,
            "output_file": output_file,
            "intermediate_results": [
                {
                    "step": r["step"],
                    "name": r["name"],
                    "output": r["output"]
                }
                for r in result.intermediate_results
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"执行提示链失败: {str(e)}")


@app.post("/api/prompt-chaining/run/stream")
async def run_prompt_chain_stream(request: PromptChainingRequest):
    """运行提示链（流式，逐步返回结果）"""
    
    async def generate():
        try:
            agent = get_prompt_chaining_agent()
            
            # 根据类型选择对应的链
            chain_types = {
                "document_gen": ("文档生成", DocumentGenerationChain.get_steps()),
                "code_review": ("代码审查", CodeReviewChain.get_steps()),
                "research": ("研究规划", ResearchPlanningChain.get_steps()),
                "story": ("故事创作", StoryCreationChain.get_steps()),
                "product": ("产品分析", ProductAnalysisChain.get_steps())
            }
            
            if request.chain_type not in chain_types:
                yield f"data: {json.dumps({'error': f'不支持的链类型: {request.chain_type}', 'done': True}, ensure_ascii=False)}\n\n"
                return
            
            chain_name, steps = chain_types[request.chain_type]
            
            # 发送链信息
            yield f"data: {json.dumps({'type': 'info', 'chain_name': chain_name, 'total_steps': len(steps)}, ensure_ascii=False)}\n\n"
            
            # 逐步执行链
            current_input = request.input_text
            llm_client = GiteeAIClient()
            
            for i, step in enumerate(steps, 1):
                # 发送步骤开始信号
                yield f"data: {json.dumps({'type': 'step_start', 'step': i, 'name': step.name, 'description': step.description}, ensure_ascii=False)}\n\n"
                
                # 格式化提示词
                prompt = step.prompt_template.format(input=current_input)
                
                # 调用 LLM（流式）
                full_output = ""
                stream = llm_client.chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    stream=True
                )
                
                for chunk in stream:
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        
                        if content:
                            full_output += content
                            # 发送内容块
                            yield f"data: {json.dumps({'type': 'content', 'step': i, 'content': content}, ensure_ascii=False)}\n\n"
                
                # 应用转换函数（如果有）
                if step.transform_fn:
                    full_output = step.transform_fn(full_output)
                
                # 发送步骤完成信号
                yield f"data: {json.dumps({'type': 'step_complete', 'step': i, 'output': full_output}, ensure_ascii=False)}\n\n"
                
                # 下一步的输入是当前步的输出
                current_input = full_output
            
            # 可选：保存结果
            output_file = None
            if request.save_result:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"prompt_chain_{request.chain_type}_{timestamp}.md"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {chain_name}结果\n\n")
                    f.write(f"**输入:** {request.input_text}\n\n")
                    f.write(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("---\n\n")
                    f.write(current_input)
            
            # 发送完成信号
            yield f"data: {json.dumps({'type': 'done', 'final_output': current_input, 'output_file': output_file}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = f"执行提示链失败: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg, 'done': True}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/prompt-chaining/types")
async def get_chain_types():
    """获取所有可用的提示链类型"""
    return {
        "chain_types": [
            {
                "id": "document_gen",
                "name": "文档生成",
                "description": "根据主题自动生成结构化技术文档",
                "steps": ["生成大纲", "撰写内容", "添加示例", "优化润色"],
                "input_hint": "请输入文档主题，例如：Python 异步编程入门"
            },
            {
                "id": "code_review",
                "name": "代码审查",
                "description": "系统化的代码审查和改进建议",
                "steps": ["理解代码", "检查问题", "提出建议", "生成报告"],
                "input_hint": "请粘贴要审查的代码"
            },
            {
                "id": "research",
                "name": "研究规划",
                "description": "将研究问题转化为系统化的研究计划",
                "steps": ["问题分析", "文献综述", "研究方法", "时间规划"],
                "input_hint": "请输入研究问题，例如：如何提高深度学习模型的训练效率？"
            },
            {
                "id": "story",
                "name": "故事创作",
                "description": "创意写作工作流，生成完整故事",
                "steps": ["构思情节", "角色塑造", "撰写初稿", "润色完善"],
                "input_hint": "请输入故事主题，例如：时间旅行者的困境"
            },
            {
                "id": "product",
                "name": "产品分析",
                "description": "系统化的产品需求分析和规划",
                "steps": ["需求理解", "功能设计", "技术方案", "实施计划"],
                "input_hint": "请描述产品需求，例如：一个帮助开发者快速搭建API的工具"
            }
        ]
    }


# ========== Routing Agent 相关接口 ==========

@app.post("/api/routing/route")
async def route_request(request: RoutingRequest):
    """执行路由决策和处理"""
    try:
        agent = get_routing_agent(request.scenario, request.strategy)
        result = agent.route(request.input_text)
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"路由失败: {result.error_message}"
            )
        
        return {
            "success": True,
            "route_name": result.route_name,
            "route_description": result.route_description,
            "output": result.handler_output,
            "confidence": result.confidence,
            "routing_reason": result.routing_reason,
            "execution_time": result.execution_time
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"路由执行失败: {str(e)}")


@app.get("/api/routing/routes")
async def get_routes(scenario: str = "smart_assistant"):
    """获取指定场景的所有路由信息"""
    try:
        # 创建一个临时 agent 来获取路由信息
        llm_client = GiteeAIClient()
        agent = RoutingAgent(llm_client=llm_client, strategy="hybrid", verbose=False)
        
        # 注册路由
        if scenario == "smart_assistant":
            routes = SmartAssistantRoutes.get_routes(llm_client)
        elif scenario == "developer_assistant":
            routes = DeveloperAssistantRoutes.get_routes(llm_client)
        else:
            raise HTTPException(status_code=400, detail=f"未知场景: {scenario}")
        
        agent.register_routes(routes)
        
        # 获取路由信息
        routes_info = agent.get_routes_info()
        
        return {
            "scenario": scenario,
            "routes": routes_info,
            "total_count": len(routes_info)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取路由信息失败: {str(e)}")


@app.get("/api/routing/scenarios")
async def get_scenarios():
    """获取所有可用的路由场景"""
    return {
        "scenarios": [
            {
                "id": "smart_assistant",
                "name": "智能助手",
                "description": "通用智能助手，支持代码生成、写作、分析、翻译等任务",
                "routes": [
                    "代码生成",
                    "内容创作",
                    "数据分析",
                    "翻译",
                    "问答",
                    "摘要总结"
                ]
            },
            {
                "id": "developer_assistant",
                "name": "开发者助手",
                "description": "专为开发者设计，支持代码审查、调试、优化、架构设计",
                "routes": [
                    "代码审查",
                    "调试",
                    "性能优化",
                    "架构设计"
                ]
            }
        ],
        "strategies": [
            {
                "id": "rule_based",
                "name": "规则路由",
                "description": "基于正则表达式的精确匹配"
            },
            {
                "id": "keyword",
                "name": "关键词路由",
                "description": "基于关键词的快速匹配"
            },
            {
                "id": "llm_based",
                "name": "LLM路由",
                "description": "使用大语言模型进行智能路由决策"
            },
            {
                "id": "hybrid",
                "name": "混合路由（推荐）",
                "description": "结合规则、关键词和LLM的优势"
            }
        ]
    }


# ========== Parallelization Agent 相关接口 ==========

@app.post("/api/parallelization/execute")
async def execute_parallelization(request: ParallelizationRequest):
    """执行并行化任务"""
    try:
        agent = get_parallelization_agent(request.max_workers)
        
        # 根据场景创建任务
        tasks = []
        
        if request.scenario == "multi_perspective":
            tasks = MultiPerspectiveAnalysis.create_tasks(
                request.input_text,
                perspectives=request.perspectives
            )
        
        elif request.scenario == "translation":
            tasks = ParallelTranslation.create_tasks(
                request.input_text,
                target_languages=request.languages
            )
        
        elif request.scenario == "content_gen":
            tasks = ParallelContentGeneration.create_tasks(
                request.input_text,
                sections=request.sections
            )
        
        elif request.scenario == "code_review":
            tasks = ParallelCodeReview.create_tasks(request.input_text)
        
        elif request.scenario == "research":
            tasks = ParallelResearch.create_tasks(
                request.input_text,
                aspects=request.aspects
            )
        
        elif request.scenario == "consensus":
            tasks = ConsensusGenerator.create_tasks(
                request.input_text,
                num_generations=request.num_generations or 5
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的场景类型: {request.scenario}"
            )
        
        # 执行并行任务
        result = agent.execute_parallel(
            tasks,
            strategy=ParallelStrategy(request.strategy),
            aggregation=AggregationMethod(request.aggregation),
            batch_size=request.batch_size
        )
        
        return {
            "success": result.success_count > 0,
            "aggregated_result": result.aggregated_result,
            "total_time": result.total_time,
            "parallel_time": result.parallel_time,
            "success_count": result.success_count,
            "failed_count": result.failed_count,
            "strategy": result.strategy,
            "aggregation_method": result.aggregation_method,
            "task_results": [
                {
                    "task_name": r.task_name,
                    "output": r.output,
                    "success": r.success,
                    "execution_time": r.execution_time,
                    "error_message": r.error_message
                }
                for r in result.task_results
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"执行并行任务失败: {str(e)}")


@app.post("/api/parallelization/execute/stream")
async def execute_parallelization_stream(request: ParallelizationRequest):
    """执行并行化任务（流式，实时返回进度）"""
    
    async def generate():
        try:
            agent = get_parallelization_agent(request.max_workers)
            
            # 根据场景创建任务
            tasks = []
            
            if request.scenario == "multi_perspective":
                tasks = MultiPerspectiveAnalysis.create_tasks(
                    request.input_text,
                    perspectives=request.perspectives
                )
            elif request.scenario == "translation":
                tasks = ParallelTranslation.create_tasks(
                    request.input_text,
                    target_languages=request.languages
                )
            elif request.scenario == "content_gen":
                tasks = ParallelContentGeneration.create_tasks(
                    request.input_text,
                    sections=request.sections
                )
            elif request.scenario == "code_review":
                tasks = ParallelCodeReview.create_tasks(request.input_text)
            elif request.scenario == "research":
                tasks = ParallelResearch.create_tasks(
                    request.input_text,
                    aspects=request.aspects
                )
            elif request.scenario == "consensus":
                tasks = ConsensusGenerator.create_tasks(
                    request.input_text,
                    num_generations=request.num_generations or 5
                )
            else:
                yield f"data: {json.dumps({'error': f'不支持的场景类型: {request.scenario}', 'done': True}, ensure_ascii=False)}\n\n"
                return
            
            # 发送任务信息
            yield f"data: {json.dumps({'type': 'info', 'total_tasks': len(tasks), 'scenario': request.scenario}, ensure_ascii=False)}\n\n"
            
            # 执行并行任务（这里我们使用一个简单的包装来发送进度）
            import time
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            def execute_task_with_progress(task):
                start_time = time.time()
                try:
                    output = task.handler(task.input_data, agent.llm_client)
                    execution_time = time.time() - start_time
                    return {
                        "task_name": task.name,
                        "output": output,
                        "success": True,
                        "execution_time": execution_time,
                        "error_message": ""
                    }
                except Exception as e:
                    execution_time = time.time() - start_time
                    return {
                        "task_name": task.name,
                        "output": None,
                        "success": False,
                        "execution_time": execution_time,
                        "error_message": str(e)
                    }
            
            task_results = []
            parallel_start = time.time()
            
            with ThreadPoolExecutor(max_workers=request.max_workers) as executor:
                future_to_task = {
                    executor.submit(execute_task_with_progress, task): task
                    for task in tasks
                }
                
                for future in as_completed(future_to_task):
                    result = future.result()
                    task_results.append(result)
                    
                    # 发送任务完成事件
                    yield f"data: {json.dumps({'type': 'task_complete', 'task_name': result['task_name'], 'success': result['success'], 'completed': len(task_results), 'total': len(tasks)}, ensure_ascii=False)}\n\n"
            
            parallel_time = time.time() - parallel_start
            
            # 聚合结果
            from src.shuyixiao_agent.agents.parallelization_agent import TaskResult
            
            task_result_objects = [
                TaskResult(
                    task_name=r["task_name"],
                    output=r["output"],
                    success=r["success"],
                    execution_time=r["execution_time"],
                    error_message=r["error_message"]
                )
                for r in task_results
            ]
            
            aggregated = agent._aggregate_results(
                task_result_objects,
                AggregationMethod(request.aggregation)
            )
            
            total_time = time.time() - parallel_start
            success_count = sum(1 for r in task_results if r["success"])
            
            # 发送最终结果
            yield f"data: {json.dumps({'type': 'done', 'aggregated_result': aggregated, 'total_time': total_time, 'parallel_time': parallel_time, 'success_count': success_count, 'task_results': task_results}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = f"执行并行任务失败: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg, 'done': True}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/parallelization/scenarios")
async def get_parallelization_scenarios():
    """获取所有可用的并行化场景"""
    return {
        "scenarios": [
            {
                "id": "multi_perspective",
                "name": "多角度分析",
                "description": "从多个角度同时分析同一问题",
                "default_perspectives": [
                    "技术角度",
                    "商业角度",
                    "用户体验角度",
                    "风险和挑战角度",
                    "创新和机会角度"
                ],
                "input_hint": "请输入要分析的主题或问题"
            },
            {
                "id": "translation",
                "name": "并行翻译",
                "description": "同时将文本翻译成多种语言",
                "default_languages": ["英语", "日语", "法语", "德语", "西班牙语"],
                "input_hint": "请输入要翻译的文本"
            },
            {
                "id": "content_gen",
                "name": "并行内容生成",
                "description": "同时生成文档的不同章节",
                "default_sections": [
                    "简介和背景",
                    "核心概念",
                    "实践示例",
                    "最佳实践",
                    "常见问题"
                ],
                "input_hint": "请输入文档主题"
            },
            {
                "id": "code_review",
                "name": "并行代码审查",
                "description": "从多个维度同时审查代码",
                "aspects": [
                    "代码质量",
                    "性能分析",
                    "安全检查",
                    "最佳实践",
                    "测试建议"
                ],
                "input_hint": "请粘贴要审查的代码"
            },
            {
                "id": "research",
                "name": "并行研究",
                "description": "同时研究问题的不同方面",
                "default_aspects": [
                    "历史背景和发展",
                    "当前状态和趋势",
                    "主要方法和技术",
                    "实际应用案例",
                    "未来展望和挑战"
                ],
                "input_hint": "请输入研究问题"
            },
            {
                "id": "consensus",
                "name": "共识生成",
                "description": "通过多次生成寻找最佳答案",
                "num_generations": 5,
                "input_hint": "请输入问题或提示词"
            }
        ],
        "strategies": [
            {
                "id": "full_parallel",
                "name": "全并行（推荐）",
                "description": "所有任务同时执行，最大化并行效率"
            },
            {
                "id": "batch_parallel",
                "name": "批量并行",
                "description": "将任务分批执行，控制资源使用"
            },
            {
                "id": "pipeline",
                "name": "流水线",
                "description": "考虑任务依赖关系，分阶段并行"
            },
            {
                "id": "vote",
                "name": "投票",
                "description": "多个相同任务并行，结果投票决定"
            },
            {
                "id": "ensemble",
                "name": "集成",
                "description": "多个不同方法并行，结果融合"
            }
        ],
        "aggregation_methods": [
            {
                "id": "merge",
                "name": "合并",
                "description": "将所有结果合并到字典"
            },
            {
                "id": "concat",
                "name": "连接",
                "description": "将所有结果连接成文本"
            },
            {
                "id": "first",
                "name": "第一个",
                "description": "使用第一个完成的结果"
            },
            {
                "id": "best",
                "name": "最佳",
                "description": "选择质量最高的结果"
            },
            {
                "id": "summarize",
                "name": "总结（推荐）",
                "description": "使用LLM总结所有结果"
            },
            {
                "id": "vote",
                "name": "投票",
                "description": "选择最常见的结果"
            },
            {
                "id": "consensus",
                "name": "共识",
                "description": "使用LLM寻找共识"
            }
        ]
    }


# ========== Reflection Agent 相关接口 ==========

@app.post("/api/reflection/reflect")
async def reflect_and_improve(request: ReflectionRequest):
    """执行反思和改进（非流式）"""
    try:
        agent = get_reflection_agent(
            max_iterations=request.max_iterations,
            score_threshold=request.score_threshold
        )
        
        # 根据场景选择标准
        criteria = None
        context = {}
        
        if request.scenario == "content":
            criteria = ContentReflection.get_criteria()
        elif request.scenario == "code":
            criteria = CodeReflection.get_criteria()
        elif request.scenario == "analysis":
            criteria = AnalysisReflection.get_criteria()
        elif request.scenario == "translation":
            criteria = TranslationReflection.get_criteria()
        
        # 设置专家上下文
        if request.strategy == "expert":
            if request.expert_role:
                context['expert_role'] = request.expert_role
            if request.expert_expertise:
                context['expert_expertise'] = request.expert_expertise
        
        # 执行反思
        result = agent.reflect_and_improve(
            task=request.task,
            initial_content=request.initial_content,
            strategy=ReflectionStrategy(request.strategy),
            criteria=criteria,
            context=context
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"反思过程失败: {result.error_message}"
            )
        
        return {
            "success": True,
            "final_content": result.final_content,
            "total_iterations": result.total_iterations,
            "final_score": result.final_score,
            "improvement_summary": result.improvement_summary,
            "total_time": result.total_time,
            "reflection_history": [
                {
                    "iteration": r.iteration,
                    "score": r.score,
                    "critique": r.critique,
                    "improvements": r.improvements,
                    "timestamp": r.timestamp
                }
                for r in result.reflection_history
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"执行反思失败: {str(e)}")


@app.post("/api/reflection/reflect/stream")
async def reflect_and_improve_stream(request: ReflectionRequest):
    """执行反思和改进（流式，实时返回每轮迭代）"""
    
    async def generate():
        from datetime import datetime as dt_now
        
        try:
            agent = get_reflection_agent(
                max_iterations=request.max_iterations,
                score_threshold=request.score_threshold
            )
            
            # 根据场景选择标准
            criteria = None
            context = {}
            
            if request.scenario == "content":
                criteria = ContentReflection.get_criteria()
            elif request.scenario == "code":
                criteria = CodeReflection.get_criteria()
            elif request.scenario == "analysis":
                criteria = AnalysisReflection.get_criteria()
            elif request.scenario == "translation":
                criteria = TranslationReflection.get_criteria()
            
            # 设置专家上下文
            if request.strategy == "expert":
                if request.expert_role:
                    context['expert_role'] = request.expert_role
                if request.expert_expertise:
                    context['expert_expertise'] = request.expert_expertise
            
            # 发送初始信息
            yield f"data: {json.dumps({'type': 'info', 'max_iterations': request.max_iterations, 'strategy': request.strategy}, ensure_ascii=False)}\n\n"
            
            # 1. 生成初始内容（如果没有提供）
            if request.initial_content is None:
                yield f"data: {json.dumps({'type': 'generating', 'message': '正在生成初始内容...'}, ensure_ascii=False)}\n\n"
                
                initial_content = agent._generate_initial_content(request.task, context)
                
                yield f"data: {json.dumps({'type': 'initial_content', 'content': initial_content}, ensure_ascii=False)}\n\n"
            else:
                initial_content = request.initial_content
                yield f"data: {json.dumps({'type': 'initial_content', 'content': initial_content}, ensure_ascii=False)}\n\n"
            
            current_content = initial_content
            reflection_history = []
            
            # 2. 迭代反思和改进
            for iteration in range(1, request.max_iterations + 1):
                # 发送迭代开始信号
                yield f"data: {json.dumps({'type': 'iteration_start', 'iteration': iteration}, ensure_ascii=False)}\n\n"
                
                # 执行反思
                critique, score, improvements = agent._reflect(
                    content=current_content,
                    task=request.task,
                    strategy=ReflectionStrategy(request.strategy),
                    criteria=criteria,
                    context=context
                )
                
                # 发送反思结果
                yield f"data: {json.dumps({'type': 'reflection', 'iteration': iteration, 'critique': critique, 'score': score, 'improvements': improvements}, ensure_ascii=False)}\n\n"
                
                # 记录历史
                reflection_result = {
                    "iteration": iteration,
                    "content": current_content,
                    "critique": critique,
                    "score": score,
                    "improvements": improvements,
                    "timestamp": dt_now.now().isoformat()
                }
                reflection_history.append(reflection_result)
                
                # 检查是否达到质量阈值
                if score >= request.score_threshold:
                    yield f"data: {json.dumps({'type': 'threshold_reached', 'score': score, 'threshold': request.score_threshold}, ensure_ascii=False)}\n\n"
                    break
                
                # 如果不是最后一轮，进行改进
                if iteration < request.max_iterations:
                    yield f"data: {json.dumps({'type': 'improving', 'message': '正在改进内容...'}, ensure_ascii=False)}\n\n"
                    
                    current_content = agent._improve(
                        content=current_content,
                        critique=critique,
                        improvements=improvements,
                        task=request.task,
                        context=context
                    )
                    
                    yield f"data: {json.dumps({'type': 'improved_content', 'iteration': iteration, 'content': current_content}, ensure_ascii=False)}\n\n"
            
            # 3. 生成改进总结
            from src.shuyixiao_agent.agents.reflection_agent import ReflectionResult
            
            history_objects = [
                ReflectionResult(
                    iteration=r['iteration'],
                    content=r['content'],
                    critique=r['critique'],
                    score=r['score'],
                    improvements=r['improvements'],
                    timestamp=r['timestamp']
                )
                for r in reflection_history
            ]
            
            improvement_summary = agent._generate_improvement_summary(history_objects, request.task)
            
            # 发送完成信号
            yield f"data: {json.dumps({'type': 'done', 'final_content': current_content, 'final_score': reflection_history[-1]['score'], 'improvement_summary': improvement_summary, 'total_iterations': len(reflection_history)}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = f"执行反思失败: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg, 'done': True}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/reflection/scenarios")
async def get_reflection_scenarios():
    """获取所有可用的反思场景"""
    return {
        "scenarios": [
            {
                "id": "content",
                "name": "内容创作",
                "description": "对文章、博客、报告等内容进行反思和改进",
                "criteria": [c.name for c in ContentReflection.get_criteria()],
                "input_hint": "请输入要改进的任务描述或内容"
            },
            {
                "id": "code",
                "name": "代码优化",
                "description": "对代码进行反思和优化",
                "criteria": [c.name for c in CodeReflection.get_criteria()],
                "input_hint": "请输入代码编写任务或粘贴要优化的代码"
            },
            {
                "id": "analysis",
                "name": "分析报告",
                "description": "对分析报告进行反思和完善",
                "criteria": [c.name for c in AnalysisReflection.get_criteria()],
                "input_hint": "请输入分析任务或要改进的分析报告"
            },
            {
                "id": "translation",
                "name": "翻译优化",
                "description": "对翻译结果进行反思和改进",
                "criteria": [c.name for c in TranslationReflection.get_criteria()],
                "input_hint": "请输入翻译任务或要改进的译文"
            }
        ],
        "strategies": [
            {
                "id": "simple",
                "name": "简单反思",
                "description": "由单一批评者进行反思，适合一般性改进"
            },
            {
                "id": "multi_aspect",
                "name": "多维度反思（推荐）",
                "description": "从多个维度进行深入反思，全面提升质量"
            },
            {
                "id": "debate",
                "name": "辩论式反思",
                "description": "正反两方辩论，从对立角度发现问题"
            },
            {
                "id": "expert",
                "name": "专家反思",
                "description": "由特定领域专家进行专业评估"
            }
        ],
        "default_settings": {
            "max_iterations": 3,
            "score_threshold": 0.85
        }
    }


# ==================== Tool Use Agent API ====================

@app.post("/api/tool-use/execute")
async def execute_tool_use_request(request: ToolUseRequest):
    """执行Tool Use请求"""
    try:
        agent = get_agent("tool_use")
        
        # 如果指定了工具类型，可以进行过滤（这里简化处理）
        result = await agent.process_request(
            user_input=request.user_input,
            max_iterations=request.max_iterations
        )
        
        return {
            "success": result["success"],
            "message": result["message"],
            "results": result["results"],
            "total_iterations": result.get("total_iterations", 0),
            "execution_history": agent.get_execution_history()[-10:]  # 最近10条记录
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool Use执行失败: {str(e)}")


@app.post("/api/tool-use/execute/stream")
async def execute_tool_use_request_stream(request: ToolUseRequest):
    """流式执行Tool Use请求"""
    async def generate():
        try:
            agent = get_agent("tool_use")
            
            yield f"data: {json.dumps({'type': 'start', 'message': '开始处理请求'}, ensure_ascii=False)}\n\n"
            
            # 简化的流式处理，实际应该在agent中实现真正的流式
            result = await agent.process_request(
                user_input=request.user_input,
                max_iterations=request.max_iterations
            )
            
            # 逐步发送结果
            for i, step_result in enumerate(result.get("results", []), 1):
                yield f"data: {json.dumps({'type': 'step', 'step': i, 'result': step_result}, ensure_ascii=False)}\n\n"
            
            yield f"data: {json.dumps({'type': 'complete', 'final_result': result}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")


@app.post("/api/tool-use/execute-tool")
async def execute_single_tool(request: ToolExecuteRequest):
    """执行单个工具"""
    try:
        agent = get_agent("tool_use")
        
        result = await agent.execute_tool(
            tool_name=request.tool_name,
            parameters=request.parameters
        )
        
        return {
            "success": result.success,
            "result": result.result,
            "error_message": result.error_message,
            "execution_time": result.execution_time,
            "tool_name": result.tool_name,
            "parameters": result.parameters
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"工具执行失败: {str(e)}")


@app.get("/api/tool-use/tools")
async def get_available_tools(tool_type: Optional[str] = None):
    """获取可用工具列表"""
    try:
        agent = get_agent("tool_use")
        
        # 转换工具类型
        filter_type = None
        if tool_type:
            try:
                filter_type = ToolType(tool_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"无效的工具类型: {tool_type}")
        
        tools = agent.get_available_tools(tool_type=filter_type)
        
        return {
            "tools": tools,
            "total_count": len(tools),
            "tool_types": [t.value for t in ToolType]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工具列表失败: {str(e)}")


@app.get("/api/tool-use/history")
async def get_tool_execution_history():
    """获取工具执行历史"""
    try:
        agent = get_agent("tool_use")
        
        history = agent.get_execution_history()
        statistics = agent.get_tool_statistics()
        
        return {
            "history": history,
            "statistics": statistics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取执行历史失败: {str(e)}")


@app.delete("/api/tool-use/history")
async def clear_tool_execution_history():
    """清除工具执行历史"""
    try:
        agent = get_agent("tool_use")
        agent.clear_history()
        
        return {"message": "执行历史已清除"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除历史失败: {str(e)}")


@app.get("/api/tool-use/scenarios")
async def get_tool_use_scenarios():
    """获取Tool Use场景信息"""
    return {
        "scenarios": [
            {
                "id": "file_operations",
                "name": "文件操作",
                "description": "读取、写入、管理文件和目录",
                "example_tasks": [
                    "读取配置文件内容",
                    "保存数据到文件",
                    "列出目录中的文件",
                    "获取文件信息"
                ]
            },
            {
                "id": "network_requests",
                "name": "网络请求",
                "description": "发送HTTP请求，获取网络数据",
                "example_tasks": [
                    "获取API数据",
                    "检查网站状态",
                    "提交表单数据",
                    "测试网络连通性"
                ]
            },
            {
                "id": "data_processing",
                "name": "数据处理",
                "description": "解析、过滤、聚合各种格式的数据",
                "example_tasks": [
                    "解析JSON数据",
                    "过滤符合条件的记录",
                    "按字段聚合统计",
                    "排序数据"
                ]
            },
            {
                "id": "system_monitoring",
                "name": "系统监控",
                "description": "获取系统信息和性能数据",
                "example_tasks": [
                    "查看CPU使用率",
                    "检查内存状态",
                    "获取磁盘信息",
                    "列出运行进程"
                ]
            },
            {
                "id": "calculations",
                "name": "计算工具",
                "description": "数学计算、统计分析、单位转换",
                "example_tasks": [
                    "计算数学表达式",
                    "统计数据分析",
                    "单位换算",
                    "科学计算"
                ]
            },
            {
                "id": "text_processing",
                "name": "文本处理",
                "description": "文本分析、搜索替换、格式化",
                "example_tasks": [
                    "分析文本统计",
                    "搜索替换内容",
                    "提取文本模式",
                    "计算文本哈希"
                ]
            }
        ],
        "tool_types": [
            {
                "id": "file_operation",
                "name": "文件操作",
                "description": "文件和目录的读写操作"
            },
            {
                "id": "network_request",
                "name": "网络请求",
                "description": "HTTP请求和网络通信"
            },
            {
                "id": "data_processing",
                "name": "数据处理",
                "description": "数据解析、转换和分析"
            },
            {
                "id": "system_info",
                "name": "系统信息",
                "description": "系统状态和性能监控"
            },
            {
                "id": "calculation",
                "name": "计算工具",
                "description": "数学计算和统计分析"
            },
            {
                "id": "text_processing",
                "name": "文本处理",
                "description": "文本分析和处理工具"
            }
        ],
        "features": [
            "🔧 智能工具选择：自动分析需求并选择最合适的工具",
            "⚡ 高效执行：支持同步和异步工具执行",
            "📊 执行追踪：详细记录每个工具的执行过程和结果",
            "🔄 链式调用：支持多个工具协作完成复杂任务",
            "🛠️ 丰富工具库：内置20+常用工具，覆盖多个领域",
            "📈 统计分析：提供工具使用统计和性能分析"
        ]
    }


# Planning Agent API 端点

@app.post("/api/planning/create")
async def create_planning(request: PlanningRequest):
    """创建规划计划"""
    try:
        agent = get_agent("planning")
        
        # 如果指定了预定义场景，使用场景模板
        if request.scenario:
            scenarios = ProjectPlanningScenarios.get_all_scenarios(agent.llm_client)
            if request.scenario in scenarios:
                scenario_data = scenarios[request.scenario]
                
                # 创建基于模板的计划
                from .agents.planning_agent import ExecutionPlan, Task
                import time
                
                plan_id = f"plan_{int(time.time())}"
                plan = ExecutionPlan(
                    id=plan_id,
                    name=f"{scenario_data['name']} - {request.goal}",
                    description=f"基于 {scenario_data['description']} 为目标 '{request.goal}' 创建的计划",
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
                
                result_data = {
                    "success": True,
                    "plan": plan.to_dict(),
                    "message": f"成功创建基于 {scenario_data['name']} 的规划计划"
                }
                
                # 如果需要自动执行
                if request.auto_execute:
                    execution_result = agent.execute_plan(plan.id)
                    result_data["execution_result"] = execution_result.to_dict()
                
                return result_data
            else:
                raise HTTPException(status_code=400, detail=f"未知的场景类型: {request.scenario}")
        else:
            # 使用LLM创建自定义计划
            result = agent.create_plan_from_goal(request.goal, request.context)
            
            result_data = {
                "success": result.success,
                "plan": result.plan.to_dict() if result.plan else None,
                "error_message": result.error_message,
                "execution_log": result.execution_log
            }
            
            # 如果需要自动执行
            if request.auto_execute and result.success:
                execution_result = agent.execute_plan(result.plan.id)
                result_data["execution_result"] = execution_result.to_dict()
            
            return result_data
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建规划失败: {str(e)}")


@app.post("/api/planning/execute")
async def execute_planning(request: PlanExecutionRequest):
    """执行规划计划"""
    try:
        agent = get_agent("planning")
        result = agent.execute_plan(request.plan_id)
        
        return {
            "success": result.success,
            "plan": result.plan.to_dict() if result.plan else None,
            "execution_log": result.execution_log,
            "error_message": result.error_message,
            "total_duration": result.total_duration,
            "completed_tasks": result.completed_tasks,
            "failed_tasks": result.failed_tasks
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行规划失败: {str(e)}")


@app.post("/api/planning/execute/stream")
async def execute_planning_stream(request: PlanExecutionRequest):
    """流式执行规划计划"""
    try:
        agent = get_agent("planning")
        
        def generate_progress():
            def progress_callback(progress: float, current_task):
                progress_data = {
                    "type": "progress",
                    "progress": progress,
                    "current_task": current_task.to_dict() if current_task else None,
                    "timestamp": datetime.now().isoformat()
                }
                return f"data: {json.dumps(progress_data, ensure_ascii=False)}\n\n"
            
            # 开始执行
            yield f"data: {json.dumps({'type': 'start', 'message': '开始执行规划'}, ensure_ascii=False)}\n\n"
            
            result = agent.execute_plan(request.plan_id, progress_callback)
            
            # 发送最终结果
            final_data = {
                "type": "complete",
                "success": result.success,
                "plan": result.plan.to_dict() if result.plan else None,
                "execution_log": result.execution_log,
                "error_message": result.error_message,
                "total_duration": result.total_duration,
                "completed_tasks": result.completed_tasks,
                "failed_tasks": result.failed_tasks
            }
            yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_progress(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"流式执行规划失败: {str(e)}")


@app.get("/api/planning/plans")
async def get_all_plans():
    """获取所有规划计划"""
    try:
        agent = get_agent("planning")
        plans = agent.list_plans()
        
        return {
            "success": True,
            "plans": [plan.to_dict() for plan in plans],
            "count": len(plans)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取规划列表失败: {str(e)}")


@app.get("/api/planning/plan/{plan_id}")
async def get_plan_detail(plan_id: str):
    """获取规划计划详情"""
    try:
        agent = get_agent("planning")
        plan = agent.get_plan(plan_id)
        
        if not plan:
            raise HTTPException(status_code=404, detail=f"计划不存在: {plan_id}")
        
        return {
            "success": True,
            "plan": plan.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取规划详情失败: {str(e)}")


@app.delete("/api/planning/plan/{plan_id}")
async def delete_plan(plan_id: str):
    """删除规划计划"""
    try:
        agent = get_agent("planning")
        success = agent.delete_plan(plan_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"计划不存在: {plan_id}")
        
        return {
            "success": True,
            "message": f"成功删除计划: {plan_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除规划失败: {str(e)}")


@app.get("/api/planning/scenarios")
async def get_planning_scenarios():
    """获取所有预定义的规划场景"""
    try:
        agent = get_agent("planning")
        scenarios = ProjectPlanningScenarios.get_all_scenarios(agent.llm_client)
        
        # 转换为前端友好的格式
        scenario_list = []
        for scenario_id, scenario_data in scenarios.items():
            scenario_info = {
                "id": scenario_id,
                "name": scenario_data["name"],
                "description": scenario_data["description"],
                "strategy": scenario_data["strategy"],
                "task_count": len(scenario_data["template_tasks"]),
                "estimated_duration": sum(task["estimated_duration"] for task in scenario_data["template_tasks"]),
                "features": [
                    f"📋 {len(scenario_data['template_tasks'])} 个预定义任务",
                    f"⏱️ 预计耗时 {sum(task['estimated_duration'] for task in scenario_data['template_tasks']) // 3600} 小时",
                    f"🎯 策略: {scenario_data['strategy']}",
                    f"🔄 自动依赖管理"
                ]
            }
            scenario_list.append(scenario_info)
        
        return {
            "success": True,
            "scenarios": scenario_list,
            "count": len(scenario_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取规划场景失败: {str(e)}")


# ==================== Multi-Agent Collaboration APIs ====================

class MultiAgentCollaborationRequest(BaseModel):
    """多智能体协作请求"""
    input_text: str
    team_type: str  # software_dev, research, content, business
    mode: Optional[str] = "hierarchical"
    context: Optional[Dict[str, Any]] = None


class MemoryStoreRequest(BaseModel):
    """存储记忆请求"""
    content: str
    memory_type: str = "semantic"
    importance: int = 3
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    session_id: str = "default"


class MemoryRetrieveRequest(BaseModel):
    """检索记忆请求"""
    query: str
    memory_types: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    top_k: int = 5
    min_importance: Optional[int] = None
    session_id: str = "default"


class MemoryChatRequest(BaseModel):
    """基于记忆的对话请求"""
    user_input: str
    use_memory_types: Optional[List[str]] = None
    session_id: str = "default"


class WorkingMemoryUpdateRequest(BaseModel):
    """工作记忆更新请求"""
    key: str
    value: Any
    session_id: str = "default"


@app.get("/api/multi-agent/teams")
async def get_collaboration_teams():
    """获取可用的协作团队类型"""
    teams = {
        "software_dev": {
            "name": "软件开发团队",
            "description": "产品经理、系统架构师、开发工程师、QA 工程师协同工作",
            "agents": [
                {"name": "产品经理", "role": "coordinator", "expertise": ["需求分析", "产品规划"]},
                {"name": "系统架构师", "role": "specialist", "expertise": ["系统架构", "技术选型"]},
                {"name": "后端开发工程师", "role": "executor", "expertise": ["后端开发", "API设计"]},
                {"name": "前端开发工程师", "role": "executor", "expertise": ["前端开发", "UI实现"]},
                {"name": "QA工程师", "role": "reviewer", "expertise": ["测试", "质量保证"]}
            ],
            "use_cases": ["需求分析与设计", "系统架构设计", "功能开发规划", "代码质量审查"]
        },
        "research": {
            "name": "研究团队",
            "description": "研究负责人、理论专家、数据科学家、实验研究者、同行评审专家协同研究",
            "agents": [
                {"name": "研究负责人", "role": "coordinator", "expertise": ["研究规划", "团队协调"]},
                {"name": "理论研究者", "role": "specialist", "expertise": ["理论分析", "模型构建"]},
                {"name": "数据科学家", "role": "specialist", "expertise": ["数据分析", "统计建模"]},
                {"name": "实验研究者", "role": "executor", "expertise": ["实验设计", "数据收集"]},
                {"name": "同行评审专家", "role": "reviewer", "expertise": ["学术评审", "质量控制"]}
            ],
            "use_cases": ["研究课题设计", "数据分析方案", "实验方案设计", "论文质量评审"]
        },
        "content": {
            "name": "内容创作团队",
            "description": "内容策略师、撰写者、编辑、SEO专家协同创作",
            "agents": [
                {"name": "内容策略师", "role": "coordinator", "expertise": ["内容策划", "受众分析"]},
                {"name": "内容撰写者", "role": "executor", "expertise": ["写作", "文案"]},
                {"name": "内容编辑", "role": "reviewer", "expertise": ["编辑", "校对"]},
                {"name": "SEO专家", "role": "advisor", "expertise": ["SEO", "关键词优化"]}
            ],
            "use_cases": ["文章策划与创作", "营销文案撰写", "技术文档编写", "内容SEO优化"]
        },
        "business": {
            "name": "商业咨询团队",
            "description": "首席顾问、商业分析师、财务顾问、实施专家、质量保证专家协同咨询",
            "agents": [
                {"name": "首席顾问", "role": "coordinator", "expertise": ["战略规划", "项目管理"]},
                {"name": "商业分析师", "role": "specialist", "expertise": ["业务分析", "市场研究"]},
                {"name": "财务顾问", "role": "specialist", "expertise": ["财务分析", "成本效益"]},
                {"name": "实施专家", "role": "executor", "expertise": ["方案实施", "变革管理"]},
                {"name": "质量保证专家", "role": "reviewer", "expertise": ["质量审核", "风险评估"]}
            ],
            "use_cases": ["业务战略规划", "市场分析报告", "财务可行性分析", "项目实施方案"]
        }
    }
    
    return {
        "success": True,
        "teams": teams,
        "count": len(teams)
    }


@app.get("/api/multi-agent/modes")
async def get_collaboration_modes():
    """获取可用的协作模式"""
    modes = {
        "sequential": {
            "name": "顺序协作",
            "description": "Agents 按顺序工作，后面的 Agent 基于前面的结果继续工作",
            "icon": "🔄",
            "use_case": "适合有明确流程的任务"
        },
        "parallel": {
            "name": "并行协作",
            "description": "所有 Agents 同时工作，然后整合各自的结果",
            "icon": "⚡",
            "use_case": "适合需要多角度分析的任务"
        },
        "hierarchical": {
            "name": "层级协作",
            "description": "有明确的管理层级，协调者分配任务，专家执行，审核者检查",
            "icon": "🏢",
            "use_case": "适合复杂的、需要专业分工的任务（推荐）"
        },
        "peer_to_peer": {
            "name": "对等协作",
            "description": "Agents 平等协作，相互讨论和改进",
            "icon": "🤝",
            "use_case": "适合需要反复讨论和优化的任务"
        },
        "hybrid": {
            "name": "混合模式",
            "description": "结合多种协作方式的优势",
            "icon": "🔀",
            "use_case": "灵活适应不同场景"
        }
    }
    
    return {
        "success": True,
        "modes": modes
    }


@app.post("/api/multi-agent/collaborate")
async def multi_agent_collaborate(request: MultiAgentCollaborationRequest):
    """执行多智能体协作"""
    try:
        # 获取 LLM 客户端
        llm_client = GiteeAIClient()
        
        # 创建协作系统
        collaboration = MultiAgentCollaboration(
            llm_client=llm_client,
            mode=request.mode,
            verbose=True
        )
        
        # 根据团队类型注册 Agents
        if request.team_type == "software_dev":
            agents = SoftwareDevelopmentTeam.get_agents()
        elif request.team_type == "research":
            agents = ResearchTeam.get_agents()
        elif request.team_type == "content":
            agents = ContentCreationTeam.get_agents()
        elif request.team_type == "business":
            agents = BusinessConsultingTeam.get_agents()
        else:
            raise HTTPException(status_code=400, detail=f"未知的团队类型: {request.team_type}")
        
        collaboration.register_agents(agents)
        
        # 执行协作
        result = collaboration.collaborate(request.input_text, request.context)
        
        return {
            "success": result.success,
            "final_output": result.final_output,
            "agent_contributions": result.agent_contributions,
            "messages": [
                {
                    "sender": msg.sender,
                    "receiver": msg.receiver,
                    "content": msg.content,
                    "type": msg.message_type,
                    "timestamp": msg.timestamp
                }
                for msg in result.messages
            ],
            "execution_time": result.execution_time,
            "error_message": result.error_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"多智能体协作失败: {str(e)}")


@app.post("/api/multi-agent/collaborate/stream")
async def multi_agent_collaborate_stream(request: MultiAgentCollaborationRequest):
    """流式执行多智能体协作"""
    try:
        # 获取 LLM 客户端
        llm_client = GiteeAIClient()
        
        def generate_collaboration():
            try:
                # 发送开始事件
                yield f"data: {json.dumps({'type': 'start', 'message': '开始多智能体协作'}, ensure_ascii=False)}\n\n"
                
                # 创建协作系统
                collaboration = MultiAgentCollaboration(
                    llm_client=llm_client,
                    mode=request.mode,
                    verbose=False  # 流式模式下关闭控制台输出
                )
                
                # 根据团队类型注册 Agents
                if request.team_type == "software_dev":
                    agents = SoftwareDevelopmentTeam.get_agents()
                    team_name = "软件开发团队"
                elif request.team_type == "research":
                    agents = ResearchTeam.get_agents()
                    team_name = "研究团队"
                elif request.team_type == "content":
                    agents = ContentCreationTeam.get_agents()
                    team_name = "内容创作团队"
                elif request.team_type == "business":
                    agents = BusinessConsultingTeam.get_agents()
                    team_name = "商业咨询团队"
                else:
                    yield f"data: {json.dumps({'type': 'error', 'message': f'未知的团队类型: {request.team_type}'}, ensure_ascii=False)}\n\n"
                    return
                
                collaboration.register_agents(agents)
                
                # 发送团队信息
                team_info = {
                    "type": "team_info",
                    "team_name": team_name,
                    "agent_count": len(agents),
                    "agents": [{"name": a.name, "role": a.role.value, "description": a.description} for a in agents],
                    "mode": request.mode
                }
                yield f"data: {json.dumps(team_info, ensure_ascii=False)}\n\n"
                
                # 执行协作
                result = collaboration.collaborate(request.input_text, request.context)
                
                # 发送完成事件
                complete_data = {
                    "type": "complete",
                    "success": result.success,
                    "final_output": result.final_output,
                    "agent_contributions": result.agent_contributions,
                    "messages": [
                        {
                            "sender": msg.sender,
                            "receiver": msg.receiver,
                            "content": msg.content,
                            "type": msg.message_type,
                            "timestamp": msg.timestamp
                        }
                        for msg in result.messages
                    ],
                    "execution_time": result.execution_time,
                    "error_message": result.error_message
                }
                yield f"data: {json.dumps(complete_data, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                error_data = {
                    "type": "error",
                    "message": f"协作执行失败: {str(e)}"
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_collaboration(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"流式协作失败: {str(e)}")


# ==================== Memory Management APIs ====================

@app.post("/api/memory/store")
async def store_memory(request: MemoryStoreRequest):
    """存储新记忆"""
    try:
        agent = get_memory_agent(request.session_id)
        
        memory = agent.store_memory(
            content=request.content,
            memory_type=MemoryType(request.memory_type),
            importance=MemoryImportance(request.importance),
            tags=request.tags,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            "memory": memory.to_dict(),
            "message": "记忆已存储"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"存储记忆失败: {str(e)}")


@app.post("/api/memory/retrieve")
async def retrieve_memories(request: MemoryRetrieveRequest):
    """检索相关记忆"""
    try:
        agent = get_memory_agent(request.session_id)
        
        # 转换记忆类型
        memory_types = None
        if request.memory_types:
            memory_types = [MemoryType(mt) for mt in request.memory_types]
        
        # 转换重要性
        min_importance = None
        if request.min_importance is not None:
            min_importance = MemoryImportance(request.min_importance)
        
        results = agent.retrieve_memories(
            query=request.query,
            memory_types=memory_types,
            tags=request.tags,
            top_k=request.top_k,
            min_importance=min_importance
        )
        
        return {
            "success": True,
            "results": [
                {
                    "memory": result.memory.to_dict(),
                    "relevance_score": result.relevance_score,
                    "reason": result.reason
                }
                for result in results
            ],
            "count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索记忆失败: {str(e)}")


@app.post("/api/memory/chat")
async def chat_with_memory(request: MemoryChatRequest):
    """基于记忆的对话（非流式）"""
    try:
        agent = get_memory_agent(request.session_id)
        
        # 转换记忆类型
        use_memory_types = None
        if request.use_memory_types:
            use_memory_types = [MemoryType(mt) for mt in request.use_memory_types]
        
        response = agent.chat_with_memory(
            user_input=request.user_input,
            use_memory_types=use_memory_types
        )
        
        return {
            "success": True,
            "response": response,
            "session_id": request.session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")


@app.post("/api/memory/chat/stream")
async def chat_with_memory_stream(request: MemoryChatRequest):
    """基于记忆的对话（流式）"""
    
    async def generate():
        try:
            agent = get_memory_agent(request.session_id)
            
            # 转换记忆类型
            use_memory_types = None
            if request.use_memory_types:
                use_memory_types = [MemoryType(mt) for mt in request.use_memory_types]
            
            # 检索相关记忆
            relevant_memories = agent.retrieve_memories(
                query=request.user_input,
                memory_types=use_memory_types,
                top_k=5
            )
            
            # 发送记忆信息
            if relevant_memories:
                memory_info = {
                    "type": "memories",
                    "memories": [
                        {
                            "content": result.memory.content,
                            "type": result.memory.memory_type.value,
                            "relevance": result.relevance_score
                        }
                        for result in relevant_memories
                    ]
                }
                yield f"data: {json.dumps(memory_info, ensure_ascii=False)}\n\n"
            
            # 调用LLM并流式返回
            response = agent.chat_with_memory(
                user_input=request.user_input,
                use_memory_types=use_memory_types
            )
            
            # 逐字发送响应
            for char in response:
                yield f"data: {json.dumps({'type': 'content', 'content': char}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)  # 模拟流式效果
            
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            error_msg = f"对话失败: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.put("/api/memory/working")
async def update_working_memory(request: WorkingMemoryUpdateRequest):
    """更新工作记忆"""
    try:
        agent = get_memory_agent(request.session_id)
        agent.update_working_memory(request.key, request.value)
        
        return {
            "success": True,
            "message": f"工作记忆已更新: {request.key}",
            "working_memory": agent.working_memory
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新工作记忆失败: {str(e)}")


@app.delete("/api/memory/working/{session_id}")
async def clear_working_memory(session_id: str):
    """清空工作记忆"""
    try:
        agent = get_memory_agent(session_id)
        agent.clear_working_memory()
        
        return {
            "success": True,
            "message": "工作记忆已清空"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空工作记忆失败: {str(e)}")


@app.delete("/api/memory/session/{session_id}")
async def clear_session_context(session_id: str):
    """清空会话上下文"""
    try:
        agent = get_memory_agent(session_id)
        agent.clear_session_context()
        
        return {
            "success": True,
            "message": "会话上下文已清空"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空会话上下文失败: {str(e)}")


@app.get("/api/memory/statistics/{session_id}")
async def get_memory_statistics(session_id: str):
    """获取记忆统计信息"""
    try:
        agent = get_memory_agent(session_id)
        stats = agent.get_statistics()
        
        return {
            "success": True,
            "statistics": {
                "total_memories": stats.total_memories,
                "by_type": stats.by_type,
                "by_importance": stats.by_importance,
                "oldest_memory": stats.oldest_memory,
                "newest_memory": stats.newest_memory,
                "most_accessed": stats.most_accessed.to_dict() if stats.most_accessed else None,
                "storage_size_bytes": stats.storage_size_bytes,
                "storage_size_kb": round(stats.storage_size_bytes / 1024, 2)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@app.get("/api/memory/types/{session_id}/{memory_type}")
async def get_memories_by_type(session_id: str, memory_type: str):
    """获取指定类型的所有记忆"""
    try:
        agent = get_memory_agent(session_id)
        memories = agent.get_memories_by_type(MemoryType(memory_type))
        
        return {
            "success": True,
            "memories": [m.to_dict() for m in memories],
            "count": len(memories),
            "memory_type": memory_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取记忆失败: {str(e)}")


@app.get("/api/memory/tags/{session_id}/{tag}")
async def get_memories_by_tag(session_id: str, tag: str):
    """获取指定标签的所有记忆"""
    try:
        agent = get_memory_agent(session_id)
        memories = agent.get_memories_by_tag(tag)
        
        return {
            "success": True,
            "memories": [m.to_dict() for m in memories],
            "count": len(memories),
            "tag": tag
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取记忆失败: {str(e)}")


@app.get("/api/memory/info")
async def get_memory_info():
    """获取记忆管理系统信息"""
    return {
        "memory_types": [
            {
                "id": "short_term",
                "name": "短期记忆",
                "description": "最近的对话和交互",
                "icon": "⚡"
            },
            {
                "id": "long_term",
                "name": "长期记忆",
                "description": "重要的知识和经验",
                "icon": "💾"
            },
            {
                "id": "working",
                "name": "工作记忆",
                "description": "当前任务相关的临时信息",
                "icon": "🔧"
            },
            {
                "id": "semantic",
                "name": "语义记忆",
                "description": "事实和概念性知识",
                "icon": "📚"
            },
            {
                "id": "episodic",
                "name": "情景记忆",
                "description": "具体的事件和经历",
                "icon": "📖"
            },
            {
                "id": "procedural",
                "name": "程序性记忆",
                "description": "技能和操作步骤",
                "icon": "⚙️"
            }
        ],
        "importance_levels": [
            {"value": 5, "name": "关键", "description": "必须保留"},
            {"value": 4, "name": "高", "description": "应该保留"},
            {"value": 3, "name": "中", "description": "可以保留"},
            {"value": 2, "name": "低", "description": "可以遗忘"},
            {"value": 1, "name": "最低", "description": "优先遗忘"}
        ],
        "strategies": [
            {
                "id": "fifo",
                "name": "先进先出",
                "description": "删除最早的记忆"
            },
            {
                "id": "lru",
                "name": "最近最少使用",
                "description": "删除最少访问的记忆"
            },
            {
                "id": "importance",
                "name": "基于重要性",
                "description": "优先删除不重要的记忆"
            },
            {
                "id": "hybrid",
                "name": "混合策略（推荐）",
                "description": "综合考虑时间、重要性和访问频率"
            }
        ],
        "features": [
            "🧠 多层次记忆：支持短期、长期、工作记忆等多种类型",
            "🔍 智能检索：根据相关性和重要性检索记忆",
            "🔄 自动管理：自动整理、压缩、遗忘不重要的记忆",
            "💾 持久化：记忆可以持久化存储，跨会话使用",
            "🎯 上下文感知：根据当前任务动态调整记忆使用策略",
            "📊 统计分析：提供详细的记忆使用统计和分析"
        ]
    }


@app.post("/api/memory/export/{session_id}")
async def export_memories(session_id: str, memory_types: Optional[List[str]] = None):
    """导出记忆"""
    try:
        agent = get_memory_agent(session_id)
        
        # 转换记忆类型
        types = None
        if memory_types:
            types = [MemoryType(mt) for mt in memory_types]
        
        # 导出到临时文件
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = f"data/memories/export_{session_id}_{timestamp}.json"
        
        agent.export_memories(export_path, types)
        
        return {
            "success": True,
            "message": "记忆已导出",
            "export_path": export_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出记忆失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import asyncio
    uvicorn.run(
        "shuyixiao_agent.web_app:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )

