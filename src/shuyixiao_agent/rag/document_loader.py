"""
文档加载和分片模块

支持多种文档格式的加载和智能分片
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import os

from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    DirectoryLoader,
)

from ..config import settings


class DocumentLoader:
    """
    文档加载器
    
    支持加载多种格式的文档并进行智能分片
    """
    
    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        separators: Optional[List[str]] = None
    ):
        """
        初始化文档加载器
        
        Args:
            chunk_size: 分片大小
            chunk_overlap: 分片重叠大小
            separators: 分隔符列表
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        # 默认分隔符（针对中英文优化）
        self.separators = separators or [
            "\n\n",  # 段落
            "\n",    # 行
            "。",    # 中文句号
            "！",    # 中文感叹号
            "？",    # 中文问号
            ".",     # 英文句号
            "!",     # 英文感叹号
            "?",     # 英文问号
            "；",    # 中文分号
            ";",     # 英文分号
            "，",    # 中文逗号
            ",",     # 英文逗号
            " ",     # 空格
            ""       # 字符
        ]
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len,
        )
    
    def load_text(
        self,
        file_path: str,
        encoding: str = "utf-8"
    ) -> List[Document]:
        """
        加载文本文件
        
        Args:
            file_path: 文件路径
            encoding: 文件编码
            
        Returns:
            文档列表
        """
        loader = TextLoader(file_path, encoding=encoding)
        documents = loader.load()
        
        # 添加源文件信息
        for doc in documents:
            doc.metadata["source"] = file_path
            doc.metadata["type"] = "text"
        
        return documents
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """
        加载 PDF 文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文档列表
        """
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # 添加源文件信息
        for doc in documents:
            doc.metadata["source"] = file_path
            doc.metadata["type"] = "pdf"
        
        return documents
    
    def load_markdown(self, file_path: str) -> List[Document]:
        """
        加载 Markdown 文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文档列表
        """
        loader = UnstructuredMarkdownLoader(file_path)
        documents = loader.load()
        
        # 添加源文件信息
        for doc in documents:
            doc.metadata["source"] = file_path
            doc.metadata["type"] = "markdown"
        
        return documents
    
    def load_file(self, file_path: str) -> List[Document]:
        """
        根据文件扩展名自动选择加载器
        
        Args:
            file_path: 文件路径
            
        Returns:
            文档列表
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        suffix = file_path.suffix.lower()
        
        # 根据文件类型选择加载器
        if suffix == ".pdf":
            return self.load_pdf(str(file_path))
        elif suffix in [".md", ".markdown"]:
            return self.load_markdown(str(file_path))
        elif suffix in [".txt", ".text"]:
            return self.load_text(str(file_path))
        else:
            # 默认尝试作为文本文件加载
            try:
                return self.load_text(str(file_path))
            except Exception as e:
                raise ValueError(f"不支持的文件类型: {suffix}，错误: {e}")
    
    def load_directory(
        self,
        directory_path: str,
        glob_pattern: str = "**/*.*",
        show_progress: bool = True
    ) -> List[Document]:
        """
        加载目录中的所有文档
        
        Args:
            directory_path: 目录路径
            glob_pattern: 文件匹配模式
            show_progress: 是否显示进度
            
        Returns:
            文档列表
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory_path}")
        
        all_documents = []
        
        # 获取所有匹配的文件
        files = list(directory_path.glob(glob_pattern))
        
        if show_progress:
            print(f"找到 {len(files)} 个文件")
        
        # 逐个加载文件
        for i, file_path in enumerate(files, 1):
            if file_path.is_file():
                try:
                    documents = self.load_file(str(file_path))
                    all_documents.extend(documents)
                    
                    if show_progress:
                        print(f"[{i}/{len(files)}] 已加载: {file_path.name}")
                except Exception as e:
                    if show_progress:
                        print(f"[{i}/{len(files)}] 加载失败: {file_path.name}, 错误: {e}")
        
        return all_documents
    
    def split_documents(
        self,
        documents: List[Document],
        add_chunk_index: bool = True
    ) -> List[Document]:
        """
        分割文档
        
        Args:
            documents: 文档列表
            add_chunk_index: 是否添加分片索引到元数据
            
        Returns:
            分片后的文档列表
        """
        chunks = self.text_splitter.split_documents(documents)
        
        # 添加分片索引
        if add_chunk_index:
            for i, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = i
                chunk.metadata["chunk_size"] = len(chunk.page_content)
        
        return chunks
    
    def split_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        分割文本
        
        Args:
            text: 文本内容
            metadata: 元数据
            
        Returns:
            分片后的文档列表
        """
        chunks = self.text_splitter.split_text(text)
        
        # 创建文档对象
        documents = []
        for i, chunk in enumerate(chunks):
            doc_metadata = metadata.copy() if metadata else {}
            doc_metadata["chunk_index"] = i
            doc_metadata["chunk_size"] = len(chunk)
            
            documents.append(
                Document(
                    page_content=chunk,
                    metadata=doc_metadata
                )
            )
        
        return documents
    
    def load_and_split(
        self,
        file_path: str,
        add_chunk_index: bool = True
    ) -> List[Document]:
        """
        加载文件并分割
        
        Args:
            file_path: 文件路径
            add_chunk_index: 是否添加分片索引
            
        Returns:
            分片后的文档列表
        """
        documents = self.load_file(file_path)
        chunks = self.split_documents(documents, add_chunk_index)
        
        return chunks
    
    def load_directory_and_split(
        self,
        directory_path: str,
        glob_pattern: str = "**/*.*",
        show_progress: bool = True,
        add_chunk_index: bool = True
    ) -> List[Document]:
        """
        加载目录中的所有文档并分割
        
        Args:
            directory_path: 目录路径
            glob_pattern: 文件匹配模式
            show_progress: 是否显示进度
            add_chunk_index: 是否添加分片索引
            
        Returns:
            分片后的文档列表
        """
        documents = self.load_directory(directory_path, glob_pattern, show_progress)
        
        if show_progress:
            print(f"正在分割 {len(documents)} 个文档...")
        
        chunks = self.split_documents(documents, add_chunk_index)
        
        if show_progress:
            print(f"分割完成，共 {len(chunks)} 个片段")
        
        return chunks

