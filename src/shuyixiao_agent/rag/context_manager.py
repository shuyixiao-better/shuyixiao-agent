"""
上下文管理器

智能上下文窗口管理和临近片段扩展
"""

from typing import List, Dict, Any, Optional, Tuple
import tiktoken
from langchain_core.documents import Document

from ..config import settings


class ContextManager:
    """
    上下文管理器
    
    管理上下文窗口，支持临近片段扩展
    """
    
    def __init__(
        self,
        max_tokens: Optional[int] = None,
        enable_expansion: Optional[bool] = None,
        encoding_name: str = "cl100k_base"
    ):
        """
        初始化上下文管理器
        
        Args:
            max_tokens: 最大上下文 token 数量
            enable_expansion: 是否启用上下文扩展
            encoding_name: tiktoken 编码名称
        """
        self.max_tokens = max_tokens or settings.max_context_tokens
        self.enable_expansion = (
            enable_expansion
            if enable_expansion is not None
            else settings.enable_context_expansion
        )
        
        # 初始化 tokenizer
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
        except Exception as e:
            print(f"加载 tiktoken 编码失败: {e}")
            self.encoding = None
    
    def count_tokens(self, text: str) -> int:
        """
        计算文本的 token 数量
        
        Args:
            text: 文本
            
        Returns:
            token 数量
        """
        if self.encoding is None:
            # 如果编码器加载失败，使用简单的估算
            # 一般中文 1 字约等于 2-3 tokens，英文 1 词约等于 1-2 tokens
            # 这里使用保守估计
            return int(len(text) * 0.4)
        
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            print(f"Token 计数失败: {e}")
            return int(len(text) * 0.4)
    
    def truncate_text(
        self,
        text: str,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        截断文本到指定的 token 数量
        
        Args:
            text: 文本
            max_tokens: 最大 token 数量
            
        Returns:
            截断后的文本
        """
        max_tok = max_tokens or self.max_tokens
        
        current_tokens = self.count_tokens(text)
        
        if current_tokens <= max_tok:
            return text
        
        # 二分查找最佳截断位置
        left, right = 0, len(text)
        
        while left < right:
            mid = (left + right + 1) // 2
            truncated = text[:mid]
            
            if self.count_tokens(truncated) <= max_tok:
                left = mid
            else:
                right = mid - 1
        
        return text[:left]
    
    def expand_context(
        self,
        documents: List[Document],
        all_documents: List[Document]
    ) -> List[Document]:
        """
        扩展上下文，包含临近的文档片段
        
        Args:
            documents: 选中的文档列表
            all_documents: 所有文档列表
            
        Returns:
            扩展后的文档列表
        """
        if not self.enable_expansion or not documents:
            return documents
        
        # 按文档源分组
        doc_groups: Dict[str, List[Tuple[int, Document]]] = {}
        
        for doc in all_documents:
            source = doc.metadata.get("source", "unknown")
            chunk_index = doc.metadata.get("chunk_index", -1)
            
            if source not in doc_groups:
                doc_groups[source] = []
            
            doc_groups[source].append((chunk_index, doc))
        
        # 对每个源的文档按 chunk_index 排序
        for source in doc_groups:
            doc_groups[source].sort(key=lambda x: x[0])
        
        # 扩展选中的文档
        expanded_docs = []
        added_ids = set()
        
        for doc in documents:
            doc_id = id(doc)
            
            if doc_id in added_ids:
                continue
            
            source = doc.metadata.get("source", "unknown")
            chunk_index = doc.metadata.get("chunk_index", -1)
            
            # 添加当前文档
            expanded_docs.append(doc)
            added_ids.add(doc_id)
            
            # 如果启用扩展，尝试添加前后的文档片段
            if chunk_index >= 0 and source in doc_groups:
                source_docs = doc_groups[source]
                
                # 找到当前文档的位置
                current_pos = None
                for i, (idx, d) in enumerate(source_docs):
                    if idx == chunk_index:
                        current_pos = i
                        break
                
                if current_pos is not None:
                    # 添加前一个片段
                    if current_pos > 0:
                        prev_doc = source_docs[current_pos - 1][1]
                        prev_id = id(prev_doc)
                        
                        if prev_id not in added_ids:
                            expanded_docs.insert(
                                expanded_docs.index(doc),
                                prev_doc
                            )
                            added_ids.add(prev_id)
                    
                    # 添加后一个片段
                    if current_pos < len(source_docs) - 1:
                        next_doc = source_docs[current_pos + 1][1]
                        next_id = id(next_doc)
                        
                        if next_id not in added_ids:
                            expanded_docs.append(next_doc)
                            added_ids.add(next_id)
        
        return expanded_docs
    
    def build_context(
        self,
        documents: List[Document],
        query: Optional[str] = None,
        max_tokens: Optional[int] = None,
        separator: str = "\n\n---\n\n"
    ) -> str:
        """
        构建上下文字符串
        
        Args:
            documents: 文档列表
            query: 查询文本（可选，用于显示）
            max_tokens: 最大 token 数量
            separator: 文档分隔符
            
        Returns:
            上下文字符串
        """
        if not documents:
            return ""
        
        max_tok = max_tokens or self.max_tokens
        
        # 保留一些 token 给查询和提示
        reserve_tokens = 100
        available_tokens = max_tok - reserve_tokens
        
        # 构建上下文
        context_parts = []
        total_tokens = 0
        
        for i, doc in enumerate(documents):
            # 格式化文档
            doc_text = doc.page_content
            
            # 添加来源信息
            source = doc.metadata.get("source", "未知")
            doc_formatted = f"[文档 {i+1}] (来源: {source})\n{doc_text}"
            
            # 计算 tokens
            doc_tokens = self.count_tokens(doc_formatted + separator)
            
            # 检查是否超过限制
            if total_tokens + doc_tokens > available_tokens:
                # 尝试截断当前文档
                remaining_tokens = available_tokens - total_tokens
                
                if remaining_tokens > 100:  # 至少保留 100 tokens
                    truncated = self.truncate_text(
                        doc_formatted,
                        remaining_tokens
                    )
                    context_parts.append(truncated + "...")
                
                break
            
            context_parts.append(doc_formatted)
            total_tokens += doc_tokens
        
        context = separator.join(context_parts)
        
        return context
    
    def merge_contexts(
        self,
        contexts: List[str],
        max_tokens: Optional[int] = None,
        separator: str = "\n\n"
    ) -> str:
        """
        合并多个上下文
        
        Args:
            contexts: 上下文列表
            max_tokens: 最大 token 数量
            separator: 分隔符
            
        Returns:
            合并后的上下文
        """
        if not contexts:
            return ""
        
        max_tok = max_tokens or self.max_tokens
        
        merged_parts = []
        total_tokens = 0
        
        for context in contexts:
            context_tokens = self.count_tokens(context + separator)
            
            if total_tokens + context_tokens > max_tok:
                # 截断最后一个上下文
                remaining_tokens = max_tok - total_tokens
                
                if remaining_tokens > 100:
                    truncated = self.truncate_text(context, remaining_tokens)
                    merged_parts.append(truncated + "...")
                
                break
            
            merged_parts.append(context)
            total_tokens += context_tokens
        
        return separator.join(merged_parts)
    
    def format_documents_for_prompt(
        self,
        documents: List[Document],
        query: str,
        instruction: str = "请基于以下文档内容回答问题。"
    ) -> str:
        """
        格式化文档为提示词
        
        Args:
            documents: 文档列表
            query: 查询文本
            instruction: 指令文本
            
        Returns:
            格式化后的提示词
        """
        context = self.build_context(documents)
        
        prompt = f"""{instruction}

相关文档：
{context}

问题：{query}

请回答："""
        
        return prompt

