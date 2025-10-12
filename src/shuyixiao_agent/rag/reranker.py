"""
重排序模块

通过 ReRank 模型提升召回质量
"""

from typing import List, Tuple, Optional
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
import requests
import time

from ..config import settings


class Reranker:
    """
    重排序器
    
    使用交叉编码器模型对检索结果进行重排序
    """
    
    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-base",
        device: Optional[str] = None,
        top_k: Optional[int] = None
    ):
        """
        初始化重排序器
        
        Args:
            model_name: 重排序模型名称
            device: 运行设备 (cpu/cuda)
            top_k: 重排序后保留的文档数量
        """
        self.model_name = model_name
        self.device = device or settings.embedding_device
        self.top_k = top_k or settings.rerank_top_k
        
        # 加载交叉编码器模型
        print(f"正在加载重排序模型: {self.model_name} (设备: {self.device})")
        try:
            self.model = CrossEncoder(
                self.model_name,
                device=self.device,
                max_length=512
            )
            print(f"重排序模型加载完成")
        except Exception as e:
            print(f"重排序模型加载失败: {e}")
            print("将使用简单的分数排序作为后备方案")
            self.model = None
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
        scores: Optional[List[float]] = None,
        top_k: Optional[int] = None
    ) -> List[Tuple[Document, float]]:
        """
        对检索结果进行重排序
        
        Args:
            query: 查询文本
            documents: 文档列表
            scores: 原始分数列表（可选）
            top_k: 返回的文档数量
            
        Returns:
            (文档, 重排序分数) 元组列表
        """
        if not documents:
            return []
        
        k = top_k or self.top_k
        k = min(k, len(documents))  # 确保不超过文档数量
        
        # 如果模型加载失败，使用原始分数
        if self.model is None:
            if scores:
                sorted_results = sorted(
                    zip(documents, scores),
                    key=lambda x: x[1],
                    reverse=True
                )
                return sorted_results[:k]
            else:
                return [(doc, 1.0) for doc in documents[:k]]
        
        try:
            # 准备输入对（查询-文档对）
            pairs = [(query, doc.page_content) for doc in documents]
            
            # 计算重排序分数
            rerank_scores = self.model.predict(pairs)
            
            # 按分数排序
            sorted_results = sorted(
                zip(documents, rerank_scores),
                key=lambda x: x[1],
                reverse=True
            )
            
            return sorted_results[:k]
        
        except Exception as e:
            print(f"重排序失败: {e}")
            # 降级到原始分数排序
            if scores:
                sorted_results = sorted(
                    zip(documents, scores),
                    key=lambda x: x[1],
                    reverse=True
                )
                return sorted_results[:k]
            else:
                return [(doc, 1.0) for doc in documents[:k]]
    
    def rerank_results(
        self,
        query: str,
        results: List[Tuple[Document, float]],
        top_k: Optional[int] = None
    ) -> List[Tuple[Document, float]]:
        """
        对带分数的检索结果进行重排序
        
        Args:
            query: 查询文本
            results: (文档, 分数) 元组列表
            top_k: 返回的文档数量
            
        Returns:
            (文档, 重排序分数) 元组列表
        """
        if not results:
            return []
        
        documents, scores = zip(*results)
        return self.rerank(query, list(documents), list(scores), top_k)


class SimpleReranker(Reranker):
    """
    简单重排序器
    
    不使用深度学习模型，只基于简单的规则进行重排序
    """
    
    def __init__(self, top_k: Optional[int] = None):
        """
        初始化简单重排序器
        
        Args:
            top_k: 重排序后保留的文档数量
        """
        self.top_k = top_k or settings.rerank_top_k
        self.model = None  # 不加载模型
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
        scores: Optional[List[float]] = None,
        top_k: Optional[int] = None
    ) -> List[Tuple[Document, float]]:
        """
        基于规则的简单重排序
        
        Args:
            query: 查询文本
            documents: 文档列表
            scores: 原始分数列表（可选）
            top_k: 返回的文档数量
            
        Returns:
            (文档, 调整后的分数) 元组列表
        """
        if not documents:
            return []
        
        k = top_k or self.top_k
        k = min(k, len(documents))
        
        # 如果没有原始分数，使用默认分数
        if scores is None:
            scores = [1.0] * len(documents)
        
        # 计算调整后的分数
        adjusted_scores = []
        query_lower = query.lower()
        
        for doc, base_score in zip(documents, scores):
            content_lower = doc.page_content.lower()
            
            # 分数调整因子
            boost = 1.0
            
            # 如果文档包含完整的查询短语，提高分数
            if query_lower in content_lower:
                boost *= 1.5
            
            # 根据文档长度调整（过短或过长的文档降低分数）
            doc_length = len(doc.page_content)
            if doc_length < 50:
                boost *= 0.8
            elif doc_length > 2000:
                boost *= 0.9
            
            # 如果文档有元数据中的优先级标记，调整分数
            if "priority" in doc.metadata:
                boost *= doc.metadata["priority"]
            
            adjusted_scores.append(base_score * boost)
        
        # 按调整后的分数排序
        sorted_results = sorted(
            zip(documents, adjusted_scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_results[:k]


class CloudReranker:
    """
    云端重排序器
    
    使用 Gitee AI 等云端 API 提供重排序服务，无需下载本地模型
    优点：
    - 无需下载大型模型文件
    - 启动速度快
    - 始终使用最新版本
    - 支持 GPU 加速（云端）
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        top_k: Optional[int] = None,
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        初始化云端重排序器
        
        Args:
            api_key: API 密钥，默认从配置读取
            base_url: API 基础 URL，默认从配置读取
            model: 重排序模型名称
            top_k: 重排序后保留的文档数量
            max_retries: 最大重试次数
            timeout: 请求超时时间
        """
        self.api_key = api_key or settings.gitee_ai_api_key
        self.base_url = base_url or settings.gitee_ai_base_url
        self.model = model or settings.cloud_reranker_model
        self.top_k = top_k or settings.rerank_top_k
        self.max_retries = max_retries
        self.timeout = timeout
        
        if not self.api_key:
            raise ValueError(
                "API Key 未配置！请设置 GITEE_AI_API_KEY 环境变量或在 .env 文件中配置"
            )
        
        print(f"✓ 使用云端重排序服务: {self.model} (无需下载模型)")
    
    def _call_rerank_api(
        self,
        query: str,
        documents: List[str],
        top_k: int
    ) -> List[Tuple[int, float]]:
        """
        调用云端重排序 API
        
        Args:
            query: 查询文本
            documents: 文档文本列表
            top_k: 返回的文档数量
            
        Returns:
            (文档索引, 重排序分数) 元组列表
        """
        # 构建请求 URL
        # 注意：实际的 endpoint 可能需要根据 Gitee AI 文档调整
        url = f"{self.base_url}/rerank"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "query": query,
            "documents": documents,
            "top_n": top_k
        }
        
        # 重试机制
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout,
                    verify=settings.ssl_verify
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # 提取重排序结果
                    # 返回格式：[{"index": 0, "relevance_score": 0.95}, ...]
                    rerank_results = [
                        (item["index"], item["relevance_score"]) 
                        for item in result["results"]
                    ]
                    return rerank_results
                else:
                    error_msg = f"API 调用失败: {response.status_code} - {response.text}"
                    if attempt < self.max_retries - 1:
                        print(f"⚠️  {error_msg}，正在重试 ({attempt + 1}/{self.max_retries})...")
                        time.sleep(1)
                    else:
                        raise Exception(error_msg)
                        
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"⚠️  请求失败: {e}，正在重试 ({attempt + 1}/{self.max_retries})...")
                    time.sleep(1)
                else:
                    raise Exception(f"云端重排序服务调用失败: {e}")
        
        raise Exception("云端重排序服务调用失败：超过最大重试次数")
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
        scores: Optional[List[float]] = None,
        top_k: Optional[int] = None
    ) -> List[Tuple[Document, float]]:
        """
        对检索结果进行重排序
        
        Args:
            query: 查询文本
            documents: 文档列表
            scores: 原始分数列表（可选，云端重排序时不使用）
            top_k: 返回的文档数量
            
        Returns:
            (文档, 重排序分数) 元组列表
        """
        if not documents:
            return []
        
        k = top_k or self.top_k
        k = min(k, len(documents))  # 确保不超过文档数量
        
        try:
            # 提取文档内容
            doc_texts = [doc.page_content for doc in documents]
            
            # 调用云端重排序 API
            rerank_results = self._call_rerank_api(query, doc_texts, k)
            
            # 构建结果
            sorted_results = [
                (documents[idx], score) 
                for idx, score in rerank_results
            ]
            
            return sorted_results
        
        except Exception as e:
            print(f"云端重排序失败: {e}")
            print("降级到简单重排序器")
            # 降级到简单重排序
            fallback_reranker = SimpleReranker(top_k=k)
            return fallback_reranker.rerank(query, documents, scores, k)
    
    def rerank_results(
        self,
        query: str,
        results: List[Tuple[Document, float]],
        top_k: Optional[int] = None
    ) -> List[Tuple[Document, float]]:
        """
        对带分数的检索结果进行重排序
        
        Args:
            query: 查询文本
            results: (文档, 分数) 元组列表
            top_k: 返回的文档数量
            
        Returns:
            (文档, 重排序分数) 元组列表
        """
        if not results:
            return []
        
        documents, scores = zip(*results)
        return self.rerank(query, list(documents), list(scores), top_k)

