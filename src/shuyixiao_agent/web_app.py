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
    agent_type: str = "simple"  # simple, tool, 或 rag
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "shuyixiao_agent.web_app:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )

