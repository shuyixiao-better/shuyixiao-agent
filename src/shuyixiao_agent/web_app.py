"""
Web 应用服务

提供 FastAPI 服务来支持前端界面与 Agent 交互
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
from pathlib import Path
from langchain_core.messages import HumanMessage

from .agents.simple_agent import SimpleAgent
from .agents.tool_agent import ToolAgent
from .tools.basic_tools import get_basic_tools
from .config import settings
from .gitee_ai_client import GiteeAIClient

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

# Agent 实例缓存
agents: Dict[str, Any] = {}

# 会话消息历史（简单实现，生产环境应使用数据库）
session_histories: Dict[str, List[Dict[str, str]]] = {}


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    agent_type: str = "simple"  # simple 或 tool
    session_id: Optional[str] = "default"
    system_message: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str
    agent_type: str
    session_id: str


class SessionHistoryResponse(BaseModel):
    """会话历史响应模型"""
    session_id: str
    messages: List[Dict[str, str]]


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


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回前端 HTML 页面"""
    static_dir = Path(__file__).parent / "static"
    html_file = static_dir / "index.html"
    
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(encoding="utf-8"))
    else:
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
    return {
        "status": "healthy",
        "api_key_configured": bool(settings.gitee_ai_api_key),
        "model": settings.gitee_ai_model
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "shuyixiao_agent.web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

