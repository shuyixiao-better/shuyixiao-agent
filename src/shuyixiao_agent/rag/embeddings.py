"""
嵌入模型管理器

提供统一的嵌入模型接口，支持本地和远程嵌入模型
"""

from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings

from ..config import settings


class EmbeddingManager(Embeddings):
    """
    嵌入模型管理器
    
    支持使用 sentence-transformers 加载本地嵌入模型
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        normalize_embeddings: bool = True
    ):
        """
        初始化嵌入模型管理器
        
        Args:
            model_name: 模型名称，默认使用配置中的模型
            device: 运行设备 (cpu/cuda)，默认使用配置中的设备
            normalize_embeddings: 是否归一化嵌入向量
        """
        self.model_name = model_name or settings.embedding_model
        self.device = device or settings.embedding_device
        self.normalize_embeddings = normalize_embeddings
        
        # 加载模型
        print(f"正在加载嵌入模型: {self.model_name} (设备: {self.device})")
        self.model = SentenceTransformer(
            self.model_name,
            device=self.device
        )
        print(f"嵌入模型加载完成，向量维度: {self.model.get_sentence_embedding_dimension()}")
    
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
        
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=self.normalize_embeddings,
            show_progress_bar=False
        )
        
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """
        嵌入查询文本
        
        Args:
            text: 查询文本
            
        Returns:
            嵌入向量
        """
        embedding = self.model.encode(
            text,
            normalize_embeddings=self.normalize_embeddings,
            show_progress_bar=False
        )
        
        return embedding.tolist()
    
    def get_embedding_dimension(self) -> int:
        """获取嵌入向量维度"""
        return self.model.get_sentence_embedding_dimension()


class BatchEmbeddingManager(EmbeddingManager):
    """
    批量嵌入模型管理器
    
    支持自动分批处理大量文本
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        normalize_embeddings: bool = True,
        batch_size: int = 32
    ):
        """
        初始化批量嵌入模型管理器
        
        Args:
            model_name: 模型名称
            device: 运行设备
            normalize_embeddings: 是否归一化嵌入向量
            batch_size: 批处理大小
        """
        super().__init__(model_name, device, normalize_embeddings)
        self.batch_size = batch_size
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量嵌入文档列表
        
        Args:
            texts: 文档文本列表
            
        Returns:
            嵌入向量列表
        """
        if not texts:
            return []
        
        all_embeddings = []
        
        # 分批处理
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_embeddings = self.model.encode(
                batch_texts,
                normalize_embeddings=self.normalize_embeddings,
                show_progress_bar=False
            )
            all_embeddings.extend(batch_embeddings.tolist())
        
        return all_embeddings

