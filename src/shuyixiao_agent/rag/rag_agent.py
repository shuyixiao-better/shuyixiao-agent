"""
RAG Agent

集成所有 RAG 模块，提供完整的检索增强生成功能
"""

from typing import List, Dict, Any, Optional, Iterator
from pathlib import Path
from langchain_core.documents import Document

from .embeddings import EmbeddingManager, BatchEmbeddingManager
from .cloud_embeddings import CloudEmbeddingManager, BatchCloudEmbeddingManager
from .vector_store import VectorStoreManager
from .document_loader import DocumentLoader
from .retrievers import VectorRetriever, KeywordRetriever, HybridRetriever
from .query_optimizer import QueryOptimizer
from .reranker import Reranker, SimpleReranker, CloudReranker
from .context_manager import ContextManager

from ..gitee_ai_client import GiteeAIClient
from ..config import settings


class RAGAgent:
    """
    RAG Agent
    
    完整的检索增强生成 Agent，支持：
    - 文档加载和向量化
    - 多模态检索（向量、关键词、混合）
    - 查询优化
    - 重排序
    - 上下文管理
    - 流式响应
    """
    
    def __init__(
        self,
        collection_name: str = "default",
        system_message: Optional[str] = None,
        use_reranker: bool = True,
        retrieval_mode: str = "hybrid",  # vector, keyword, hybrid
        enable_query_optimization: bool = True,
        enable_context_expansion: bool = True
    ):
        """
        初始化 RAG Agent
        
        Args:
            collection_name: 向量数据库集合名称
            system_message: 系统消息
            use_reranker: 是否使用重排序
            retrieval_mode: 检索模式 (vector/keyword/hybrid)
            enable_query_optimization: 是否启用查询优化
            enable_context_expansion: 是否启用上下文扩展
        """
        self.collection_name = collection_name
        self.system_message = system_message or "你是一个有帮助的AI助手。请基于提供的文档内容回答用户的问题。"
        self.retrieval_mode = retrieval_mode
        
        # 初始化组件
        print(f"正在初始化 RAG Agent (集合: {collection_name})...")
        
        # 1. 嵌入模型（优先使用云端服务）
        if settings.use_cloud_embedding:
            print("✓ 使用云端嵌入服务（无需下载模型，启动更快）")
            try:
                self.embedding_manager = BatchCloudEmbeddingManager(
                    model=settings.cloud_embedding_model
                )
            except Exception as e:
                print(f"⚠️  云端嵌入服务初始化失败: {e}")
                print("⚠️  请检查 API Key 配置或设置 USE_CLOUD_EMBEDDING=false 使用本地模型")
                raise
        else:
            print("使用本地嵌入模型（首次启动会下载模型文件）")
            self.embedding_manager = BatchEmbeddingManager()
        
        # 2. 向量存储
        self.vector_store = VectorStoreManager(
            collection_name=collection_name,
            embedding_manager=self.embedding_manager
        )
        
        # 3. 文档加载器
        self.document_loader = DocumentLoader()
        
        # 4. 检索器
        self.vector_retriever = VectorRetriever(self.vector_store)
        self.keyword_retriever = KeywordRetriever()
        self.hybrid_retriever = HybridRetriever(
            self.vector_retriever,
            self.keyword_retriever
        )
        
        # 5. 查询优化器
        self.query_optimizer = QueryOptimizer() if enable_query_optimization else None
        
        # 6. 重排序器（优先使用云端服务）
        if use_reranker:
            if settings.use_cloud_reranker:
                print("✓ 使用云端重排序服务（无需下载模型，启动更快）")
                try:
                    self.reranker = CloudReranker()
                except Exception as e:
                    print(f"⚠️  云端重排序服务初始化失败: {e}")
                    print("⚠️  降级到简单重排序器")
                    self.reranker = SimpleReranker()
            else:
                print("使用本地重排序模型（首次启动会下载模型文件）")
                try:
                    self.reranker = Reranker(
                        model_name=settings.reranker_model,
                        device=settings.reranker_device
                    )
                except Exception as e:
                    print(f"⚠️  本地重排序器初始化失败: {e}")
                    print("⚠️  降级到简单重排序器")
                    self.reranker = SimpleReranker()
        else:
            self.reranker = SimpleReranker()
        
        # 7. 上下文管理器
        self.context_manager = ContextManager(
            enable_expansion=enable_context_expansion
        )
        
        # 8. LLM 客户端
        self.llm_client = GiteeAIClient()
        
        # 对话历史
        self.chat_history: List[Dict[str, str]] = []
        
        print("RAG Agent 初始化完成！")
    
    def add_documents_from_file(
        self,
        file_path: str,
        show_progress: bool = True
    ) -> int:
        """
        从文件添加文档
        
        Args:
            file_path: 文件路径
            show_progress: 是否显示进度
            
        Returns:
            添加的文档片段数量
        """
        if show_progress:
            print(f"正在加载文件: {file_path}")
        
        # 加载并分割文档
        chunks = self.document_loader.load_and_split(file_path)
        
        if show_progress:
            print(f"文档已分割为 {len(chunks)} 个片段")
            print("正在向量化并存储...")
        
        # 添加到向量存储
        self.vector_store.add_documents(chunks)
        
        # 更新关键词检索器
        self.keyword_retriever.add_documents(chunks)
        
        if show_progress:
            print(f"成功添加 {len(chunks)} 个文档片段")
        
        return len(chunks)
    
    def add_documents_from_directory(
        self,
        directory_path: str,
        glob_pattern: str = "**/*.*",
        show_progress: bool = True
    ) -> int:
        """
        从目录批量添加文档
        
        Args:
            directory_path: 目录路径
            glob_pattern: 文件匹配模式
            show_progress: 是否显示进度
            
        Returns:
            添加的文档片段数量
        """
        if show_progress:
            print(f"正在加载目录: {directory_path}")
        
        # 加载并分割文档
        chunks = self.document_loader.load_directory_and_split(
            directory_path,
            glob_pattern,
            show_progress
        )
        
        if show_progress:
            print("正在向量化并存储...")
        
        # 添加到向量存储
        self.vector_store.add_documents(chunks)
        
        # 更新关键词检索器
        self.keyword_retriever.update_documents(chunks)
        
        if show_progress:
            print(f"成功添加 {len(chunks)} 个文档片段")
        
        return len(chunks)
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> int:
        """
        直接添加文本
        
        Args:
            texts: 文本列表
            metadatas: 元数据列表
            
        Returns:
            添加的文档数量
        """
        # 分割文本
        all_chunks = []
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            chunks = self.document_loader.split_text(text, metadata)
            all_chunks.extend(chunks)
        
        # 添加到向量存储
        self.vector_store.add_documents(all_chunks)
        
        # 更新关键词检索器
        self.keyword_retriever.add_documents(all_chunks)
        
        return len(all_chunks)
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        mode: Optional[str] = None,
        use_rerank: bool = True
    ) -> List[Document]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            mode: 检索模式 (vector/keyword/hybrid)
            use_rerank: 是否使用重排序
            
        Returns:
            相关文档列表
        """
        k = top_k or settings.retrieval_top_k
        retrieval_mode = mode or self.retrieval_mode
        
        # 选择检索器
        if retrieval_mode == "vector":
            results = self.vector_retriever.retrieve(query, top_k=k)
        elif retrieval_mode == "keyword":
            results = self.keyword_retriever.retrieve(query, top_k=k)
        else:  # hybrid
            results = self.hybrid_retriever.retrieve(query, top_k=k)
        
        # 重排序
        if use_rerank and self.reranker:
            results = self.reranker.rerank_results(
                query,
                results,
                top_k=settings.rerank_top_k
            )
        
        # 提取文档
        documents = [doc for doc, score in results]
        
        return documents
    
    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        use_history: bool = True,
        optimize_query: bool = True,
        expand_context: bool = True,
        stream: bool = False
    ) -> str:
        """
        RAG 查询
        
        Args:
            question: 问题
            top_k: 检索文档数量
            use_history: 是否使用对话历史
            optimize_query: 是否优化查询
            expand_context: 是否扩展上下文
            stream: 是否流式输出
            
        Returns:
            回答文本（非流式）或 None（流式）
        """
        # 1. 查询优化
        optimized_query = question
        if optimize_query and self.query_optimizer:
            history = self.chat_history[-5:] if use_history else None
            optimization_result = self.query_optimizer.optimize_query(
                question,
                history=history,
                enable_expansion=False
            )
            optimized_query = optimization_result["rewritten_query"]
            print(f"优化后的查询: {optimized_query}")
        
        # 2. 检索相关文档
        documents = self.retrieve(
            optimized_query,
            top_k=top_k,
            use_rerank=True
        )
        
        if not documents:
            no_doc_response = "抱歉，我在知识库中没有找到相关信息来回答您的问题。"
            if not stream:
                return no_doc_response
            else:
                return self._stream_response([no_doc_response])
        
        # 3. 上下文扩展
        if expand_context:
            # 获取所有文档（用于扩展）
            all_docs = []
            if hasattr(self.keyword_retriever, 'documents'):
                all_docs = self.keyword_retriever.documents
            
            if all_docs:
                documents = self.context_manager.expand_context(
                    documents,
                    all_docs
                )
        
        # 4. 构建提示词
        prompt = self.context_manager.format_documents_for_prompt(
            documents,
            question,
            instruction="请基于以下文档内容回答问题。如果文档中没有相关信息，请如实说明。"
        )
        
        # 5. 构建消息
        messages = [
            {"role": "system", "content": self.system_message}
        ]
        
        # 添加历史对话（最近3轮）
        if use_history and self.chat_history:
            messages.extend(self.chat_history[-6:])
        
        # 添加当前问题
        messages.append({"role": "user", "content": prompt})
        
        # 6. 调用 LLM
        if stream:
            return self._generate_stream(messages, question)
        else:
            response = self.llm_client.chat_completion(
                messages=messages,
                temperature=0.7
            )
            
            answer = response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            # 更新对话历史
            self.chat_history.append({"role": "user", "content": question})
            self.chat_history.append({"role": "assistant", "content": answer})
            
            return answer
    
    def _generate_stream(
        self,
        messages: List[Dict[str, str]],
        question: str
    ) -> Iterator[str]:
        """
        生成流式响应
        
        Args:
            messages: 消息列表
            question: 问题
            
        Yields:
            响应片段
        """
        full_response = ""
        
        try:
            stream = self.llm_client.chat_completion(
                messages=messages,
                temperature=0.7,
                stream=True
            )
            
            for chunk in stream:
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    
                    if content:
                        full_response += content
                        yield content
            
            # 更新对话历史
            self.chat_history.append({"role": "user", "content": question})
            self.chat_history.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            error_msg = f"生成回答时出错: {str(e)}"
            yield error_msg
    
    def _stream_response(self, texts: List[str]) -> Iterator[str]:
        """
        将文本列表转换为流式输出
        
        Args:
            texts: 文本列表
            
        Yields:
            文本片段
        """
        for text in texts:
            yield text
    
    def clear_history(self):
        """清除对话历史"""
        self.chat_history = []
    
    def get_document_count(self) -> int:
        """获取文档数量"""
        return self.vector_store.get_document_count()
    
    def list_documents(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        列出知识库中的文档
        
        Args:
            limit: 返回文档数量限制
            offset: 偏移量
            
        Returns:
            文档列表
        """
        return self.vector_store.list_documents(limit=limit, offset=offset)
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取文档
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            文档信息
        """
        return self.vector_store.get_document_by_id(doc_id)
    
    def delete_document(self, doc_id: str) -> bool:
        """
        删除指定文档
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            是否删除成功
        """
        success = self.vector_store.delete_document_by_id(doc_id)
        if success:
            # 同时从关键词检索器中移除（重新加载所有文档）
            all_docs = self.vector_store.list_documents()
            documents = [
                Document(page_content=doc['text'], metadata=doc['metadata'])
                for doc in all_docs
            ]
            self.keyword_retriever.update_documents(documents)
        return success
    
    def clear_knowledge_base(self):
        """清空知识库"""
        self.vector_store.clear()
        self.keyword_retriever.update_documents([])
        print("知识库已清空")

