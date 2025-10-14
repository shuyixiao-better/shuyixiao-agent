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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "shuyixiao_agent.web_app:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )

