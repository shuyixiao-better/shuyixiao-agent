"""
云端嵌入服务管理器

使用 Gitee AI 等云端 API 提供嵌入服务，无需下载本地模型
"""

from typing import List, Optional
from langchain_core.embeddings import Embeddings
import requests
import time

from ..config import settings


class CloudEmbeddingManager(Embeddings):
    """
    云端嵌入服务管理器
    
    使用 Gitee AI 的向量化 API 提供嵌入服务，无需下载本地模型
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
        model: str = "bge-large-zh-v1.5",  # Gitee AI 提供的嵌入模型
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        初始化云端嵌入服务管理器
        
        Args:
            api_key: API 密钥，默认从配置读取
            base_url: API 基础 URL，默认从配置读取
            model: 嵌入模型名称
            max_retries: 最大重试次数
            timeout: 请求超时时间
        """
        self.api_key = api_key or settings.gitee_ai_api_key
        self.base_url = base_url or settings.gitee_ai_base_url
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        
        if not self.api_key:
            raise ValueError(
                "API Key 未配置！请设置 GITEE_AI_API_KEY 环境变量或在 .env 文件中配置"
            )
        
        print(f"✓ 使用云端嵌入服务: {self.model} (无需下载模型)")
    
    def _call_api(self, texts: List[str]) -> List[List[float]]:
        """
        调用云端嵌入 API
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量列表
        """
        # 构建请求 URL
        # 注意：实际的 endpoint 可能需要根据 Gitee AI 文档调整
        url = f"{self.base_url}/embeddings"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "input": texts
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
                    # 提取嵌入向量
                    embeddings = [item["embedding"] for item in result["data"]]
                    return embeddings
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
                    raise Exception(f"云端嵌入服务调用失败: {e}")
        
        raise Exception("云端嵌入服务调用失败：超过最大重试次数")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        嵌入文档列表
        
        Args:
            texts: 文档文本列表
            
        Returns:
            嵌入向量列表
        """
        if not texts:
            return []
        
        # 如果文本过多，分批处理
        batch_size = 20  # 根据 API 限制调整
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self._call_api(batch)
            all_embeddings.extend(embeddings)
        
        return all_embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        嵌入查询文本
        
        Args:
            text: 查询文本
            
        Returns:
            嵌入向量
        """
        embeddings = self._call_api([text])
        return embeddings[0] if embeddings else []
    
    def get_dimension(self) -> int:
        """
        获取嵌入向量维度
        
        Returns:
            向量维度
        """
        # 不同模型的维度
        dimension_map = {
            "bge-large-zh-v1.5": 1024,
            "bge-small-zh-v1.5": 512,
            "text-embedding-ada-002": 1536,
        }
        return dimension_map.get(self.model, 768)  # 默认 768


class BatchCloudEmbeddingManager(CloudEmbeddingManager):
    """
    批量云端嵌入服务管理器
    
    优化了批量处理性能
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache = {}  # 简单的缓存机制
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量嵌入文档（带缓存）
        
        Args:
            texts: 文档文本列表
            
        Returns:
            嵌入向量列表
        """
        if not texts:
            return []
        
        # 检查缓存
        uncached_texts = []
        uncached_indices = []
        result = [None] * len(texts)
        
        for i, text in enumerate(texts):
            if text in self.cache:
                result[i] = self.cache[text]
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # 处理未缓存的文本
        if uncached_texts:
            new_embeddings = super().embed_documents(uncached_texts)
            
            # 更新结果和缓存
            for idx, embedding in zip(uncached_indices, new_embeddings):
                result[idx] = embedding
                self.cache[texts[idx]] = embedding
        
        return result
    
    def clear_cache(self):
        """清除缓存"""
        self.cache.clear()

