"""
向量存储管理器

提供向量数据库的统一接口，支持 ChromaDB
"""

from typing import List, Dict, Any, Optional, Tuple
import os
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from .embeddings import EmbeddingManager
from ..config import settings


class VectorStoreManager:
    """
    向量存储管理器
    
    封装 ChromaDB 的操作，提供文档存储、检索等功能
    """
    
    def __init__(
        self,
        collection_name: str = "default",
        persist_directory: Optional[str] = None,
        embedding_manager: Optional[EmbeddingManager] = None
    ):
        """
        初始化向量存储管理器
        
        Args:
            collection_name: 集合名称
            persist_directory: 持久化目录
            embedding_manager: 嵌入模型管理器
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory or settings.vector_db_path
        
        # 确保持久化目录存在
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # 初始化嵌入模型
        self.embedding_manager = embedding_manager or EmbeddingManager()
        
        # 初始化 ChromaDB 客户端
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 获取或创建集合
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
            )
            print(f"已加载现有集合: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
            )
            print(f"已创建新集合: {collection_name}")
        
        # 初始化 Langchain VectorStore
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embedding_manager
        )
    
    def add_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        添加文档到向量存储
        
        Args:
            documents: 文档列表
            ids: 文档 ID 列表
            
        Returns:
            文档 ID 列表
        """
        if not documents:
            return []
        
        # 使用 Langchain 的 add_documents 方法
        doc_ids = self.vectorstore.add_documents(
            documents=documents,
            ids=ids
        )
        
        print(f"已添加 {len(documents)} 个文档到集合 {self.collection_name}")
        return doc_ids
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        添加文本到向量存储
        
        Args:
            texts: 文本列表
            metadatas: 元数据列表
            ids: 文档 ID 列表
            
        Returns:
            文档 ID 列表
        """
        if not texts:
            return []
        
        doc_ids = self.vectorstore.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"已添加 {len(texts)} 个文本到集合 {self.collection_name}")
        return doc_ids
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        相似度搜索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            filter: 元数据过滤条件
            
        Returns:
            相关文档列表
        """
        results = self.vectorstore.similarity_search(
            query=query,
            k=k,
            filter=filter
        )
        
        return results
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        """
        相似度搜索并返回分数
        
        Args:
            query: 查询文本
            k: 返回结果数量
            filter: 元数据过滤条件
            
        Returns:
            (文档, 相似度分数) 元组列表
        """
        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter
        )
        
        return results
    
    def delete_documents(self, ids: List[str]) -> None:
        """
        删除文档
        
        Args:
            ids: 要删除的文档 ID 列表
        """
        if not ids:
            return
        
        self.collection.delete(ids=ids)
        print(f"已删除 {len(ids)} 个文档")
    
    def get_document_count(self) -> int:
        """获取文档数量"""
        return self.collection.count()
    
    def list_documents(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        列出集合中的文档
        
        Args:
            limit: 返回文档数量限制
            offset: 偏移量
            
        Returns:
            文档列表，每个文档包含 id, text, metadata
        """
        try:
            # 获取所有文档
            results = self.collection.get(
                limit=limit,
                offset=offset,
                include=['documents', 'metadatas']
            )
            
            documents = []
            ids = results.get('ids', [])
            texts = results.get('documents', [])
            metadatas = results.get('metadatas', [])
            
            for i, doc_id in enumerate(ids):
                documents.append({
                    'id': doc_id,
                    'text': texts[i] if i < len(texts) else '',
                    'metadata': metadatas[i] if i < len(metadatas) else {}
                })
            
            return documents
        except Exception as e:
            print(f"列出文档时出错: {e}")
            return []
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取单个文档
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            文档信息字典，包含 id, text, metadata
        """
        try:
            results = self.collection.get(
                ids=[doc_id],
                include=['documents', 'metadatas']
            )
            
            if results and results.get('ids'):
                return {
                    'id': results['ids'][0],
                    'text': results['documents'][0] if results.get('documents') else '',
                    'metadata': results['metadatas'][0] if results.get('metadatas') else {}
                }
            return None
        except Exception as e:
            print(f"获取文档时出错: {e}")
            return None
    
    def delete_document_by_id(self, doc_id: str) -> bool:
        """
        根据 ID 删除单个文档
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            是否删除成功
        """
        try:
            self.collection.delete(ids=[doc_id])
            print(f"已删除文档: {doc_id}")
            return True
        except Exception as e:
            print(f"删除文档时出错: {e}")
            return False
    
    def clear(self) -> None:
        """清空集合"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"已清空集合: {self.collection_name}")
        except Exception as e:
            print(f"清空集合时出错: {e}")
    
    def get_vectorstore(self) -> Chroma:
        """获取 Langchain VectorStore 对象"""
        return self.vectorstore
    
    def get_retriever(self, **kwargs):
        """
        获取检索器
        
        Args:
            **kwargs: 传递给检索器的参数
            
        Returns:
            Langchain Retriever
        """
        return self.vectorstore.as_retriever(**kwargs)

