"""
多模态检索器

支持向量检索、关键词检索和混合检索
"""

from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import jieba
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document

from .vector_store import VectorStoreManager
from ..config import settings


class BaseRetriever(ABC):
    """检索器基类"""
    
    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        **kwargs
    ) -> List[Tuple[Document, float]]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            **kwargs: 其他参数
            
        Returns:
            (文档, 相关性分数) 元组列表
        """
        pass


class VectorRetriever(BaseRetriever):
    """
    向量检索器
    
    基于向量相似度的检索
    """
    
    def __init__(
        self,
        vector_store: VectorStoreManager,
        top_k: Optional[int] = None
    ):
        """
        初始化向量检索器
        
        Args:
            vector_store: 向量存储管理器
            top_k: 默认返回结果数量
        """
        self.vector_store = vector_store
        self.top_k = top_k or settings.retrieval_top_k
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Tuple[Document, float]]:
        """
        基于向量相似度检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter: 元数据过滤条件
            **kwargs: 其他参数
            
        Returns:
            (文档, 相似度分数) 元组列表
        """
        k = top_k or self.top_k
        
        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter
        )
        
        return results


class KeywordRetriever(BaseRetriever):
    """
    关键词检索器
    
    基于 BM25 算法的关键词检索
    """
    
    def __init__(
        self,
        documents: Optional[List[Document]] = None,
        top_k: Optional[int] = None,
        use_jieba: bool = True
    ):
        """
        初始化关键词检索器
        
        Args:
            documents: 文档列表
            top_k: 默认返回结果数量
            use_jieba: 是否使用 jieba 分词（针对中文）
        """
        self.documents = documents or []
        self.top_k = top_k or settings.retrieval_top_k
        self.use_jieba = use_jieba
        
        # 初始化 BM25
        self.bm25 = None
        self.tokenized_corpus = []
        
        if self.documents:
            self._build_index()
    
    def _tokenize(self, text: str) -> List[str]:
        """
        分词
        
        Args:
            text: 文本
            
        Returns:
            词语列表
        """
        if self.use_jieba:
            # 使用 jieba 分词（适用于中文）
            return list(jieba.cut(text))
        else:
            # 简单的空格分词（适用于英文）
            return text.lower().split()
    
    def _build_index(self):
        """构建 BM25 索引"""
        if not self.documents:
            return
        
        # 对所有文档进行分词
        self.tokenized_corpus = [
            self._tokenize(doc.page_content)
            for doc in self.documents
        ]
        
        # 创建 BM25 索引
        self.bm25 = BM25Okapi(self.tokenized_corpus)
    
    def update_documents(self, documents: List[Document]):
        """
        更新文档并重建索引
        
        Args:
            documents: 新的文档列表
        """
        self.documents = documents
        self._build_index()
    
    def add_documents(self, documents: List[Document]):
        """
        添加文档并更新索引
        
        Args:
            documents: 要添加的文档列表
        """
        self.documents.extend(documents)
        self._build_index()
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        **kwargs
    ) -> List[Tuple[Document, float]]:
        """
        基于 BM25 关键词检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            **kwargs: 其他参数
            
        Returns:
            (文档, BM25 分数) 元组列表
        """
        if not self.bm25 or not self.documents:
            return []
        
        k = top_k or self.top_k
        
        # 对查询进行分词
        tokenized_query = self._tokenize(query)
        
        # 计算 BM25 分数
        scores = self.bm25.get_scores(tokenized_query)
        
        # 获取 top-k 结果
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:k]
        
        results = [
            (self.documents[i], float(scores[i]))
            for i in top_indices
        ]
        
        return results


class HybridRetriever(BaseRetriever):
    """
    混合检索器
    
    结合向量检索和关键词检索
    """
    
    def __init__(
        self,
        vector_retriever: VectorRetriever,
        keyword_retriever: KeywordRetriever,
        vector_weight: Optional[float] = None,
        top_k: Optional[int] = None
    ):
        """
        初始化混合检索器
        
        Args:
            vector_retriever: 向量检索器
            keyword_retriever: 关键词检索器
            vector_weight: 向量检索的权重 (0-1)，关键词检索权重为 1-vector_weight
            top_k: 默认返回结果数量
        """
        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever
        self.vector_weight = vector_weight or settings.hybrid_search_weight
        self.keyword_weight = 1.0 - self.vector_weight
        self.top_k = top_k or settings.retrieval_top_k
    
    def _normalize_scores(
        self,
        results: List[Tuple[Document, float]]
    ) -> List[Tuple[Document, float]]:
        """
        归一化分数到 [0, 1] 区间
        
        Args:
            results: (文档, 分数) 元组列表
            
        Returns:
            归一化后的 (文档, 分数) 元组列表
        """
        if not results:
            return []
        
        scores = [score for _, score in results]
        min_score = min(scores)
        max_score = max(scores)
        
        # 避免除以零
        if max_score == min_score:
            return [(doc, 1.0) for doc, _ in results]
        
        normalized = [
            (doc, (score - min_score) / (max_score - min_score))
            for doc, score in results
        ]
        
        return normalized
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        vector_weight: Optional[float] = None,
        **kwargs
    ) -> List[Tuple[Document, float]]:
        """
        混合检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            vector_weight: 向量检索权重（可临时覆盖默认值）
            **kwargs: 其他参数
            
        Returns:
            (文档, 混合分数) 元组列表
        """
        k = top_k or self.top_k
        v_weight = vector_weight if vector_weight is not None else self.vector_weight
        k_weight = 1.0 - v_weight
        
        # 执行向量检索
        vector_results = self.vector_retriever.retrieve(
            query=query,
            top_k=k * 2,  # 获取更多结果以便合并
            **kwargs
        )
        
        # 执行关键词检索
        keyword_results = self.keyword_retriever.retrieve(
            query=query,
            top_k=k * 2,
            **kwargs
        )
        
        # 归一化分数
        vector_results = self._normalize_scores(vector_results)
        keyword_results = self._normalize_scores(keyword_results)
        
        # 合并结果
        doc_scores: Dict[str, Tuple[Document, float]] = {}
        
        # 添加向量检索结果
        for doc, score in vector_results:
            doc_id = id(doc)
            doc_scores[doc_id] = (doc, score * v_weight)
        
        # 添加关键词检索结果
        for doc, score in keyword_results:
            doc_id = id(doc)
            if doc_id in doc_scores:
                # 文档已存在，累加分数
                existing_doc, existing_score = doc_scores[doc_id]
                doc_scores[doc_id] = (existing_doc, existing_score + score * k_weight)
            else:
                doc_scores[doc_id] = (doc, score * k_weight)
        
        # 按分数排序并返回 top-k
        sorted_results = sorted(
            doc_scores.values(),
            key=lambda x: x[1],
            reverse=True
        )[:k]
        
        return sorted_results
    
    def update_keyword_documents(self, documents: List[Document]):
        """
        更新关键词检索器的文档
        
        Args:
            documents: 文档列表
        """
        self.keyword_retriever.update_documents(documents)

