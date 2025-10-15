"""
Memory Management Agent - 记忆管理代理

这个模块实现了 Agentic Design Pattern 中的 Memory Management（记忆管理）模式。
记忆管理是智能代理的核心能力之一，使代理能够保持上下文、学习经验、积累知识。

核心优势：
1. 多层次记忆：支持短期、长期、工作记忆等多种记忆类型
2. 智能检索：根据相关性和重要性检索记忆
3. 自动管理：自动整理、压缩、遗忘不重要的记忆
4. 持久化：记忆可以持久化存储，跨会话使用
5. 上下文感知：根据当前任务动态调整记忆使用策略
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib
from collections import defaultdict
import time


class MemoryType(Enum):
    """记忆类型枚举"""
    SHORT_TERM = "short_term"      # 短期记忆：最近的对话和交互
    LONG_TERM = "long_term"        # 长期记忆：重要的知识和经验
    WORKING = "working"            # 工作记忆：当前任务相关的临时信息
    SEMANTIC = "semantic"          # 语义记忆：事实和概念性知识
    EPISODIC = "episodic"          # 情景记忆：具体的事件和经历
    PROCEDURAL = "procedural"      # 程序性记忆：技能和操作步骤


class MemoryImportance(Enum):
    """记忆重要性级别"""
    CRITICAL = 5    # 关键：必须保留
    HIGH = 4        # 高：应该保留
    MEDIUM = 3      # 中：可以保留
    LOW = 2         # 低：可以遗忘
    MINIMAL = 1     # 最低：优先遗忘


@dataclass
class Memory:
    """记忆单元"""
    id: str                                      # 记忆唯一标识
    content: str                                 # 记忆内容
    memory_type: MemoryType                      # 记忆类型
    importance: MemoryImportance                 # 重要性级别
    timestamp: str                               # 创建时间
    last_accessed: str                           # 最后访问时间
    access_count: int = 0                        # 访问次数
    tags: List[str] = field(default_factory=list)  # 标签
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    embedding: Optional[List[float]] = None      # 向量表示（用于相似度检索）
    related_memories: List[str] = field(default_factory=list)  # 相关记忆ID
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "importance": self.importance.value,
            "timestamp": self.timestamp,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "tags": self.tags,
            "metadata": self.metadata,
            "related_memories": self.related_memories
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """从字典创建"""
        return cls(
            id=data["id"],
            content=data["content"],
            memory_type=MemoryType(data["memory_type"]),
            importance=MemoryImportance(data["importance"]),
            timestamp=data["timestamp"],
            last_accessed=data["last_accessed"],
            access_count=data.get("access_count", 0),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            related_memories=data.get("related_memories", [])
        )


@dataclass
class MemorySearchResult:
    """记忆搜索结果"""
    memory: Memory
    relevance_score: float  # 相关性分数 (0-1)
    reason: str            # 检索原因


@dataclass
class MemoryStats:
    """记忆统计信息"""
    total_memories: int
    by_type: Dict[str, int]
    by_importance: Dict[str, int]
    oldest_memory: Optional[str]
    newest_memory: Optional[str]
    most_accessed: Optional[Memory]
    storage_size_bytes: int


class MemoryStrategy(Enum):
    """记忆管理策略"""
    FIFO = "fifo"              # 先进先出
    LRU = "lru"                # 最近最少使用
    IMPORTANCE = "importance"  # 基于重要性
    HYBRID = "hybrid"          # 混合策略


class MemoryAgent:
    """
    记忆管理代理 - 实现 Memory Management 设计模式
    
    示例用法:
        agent = MemoryAgent(llm_client=llm_client, max_memories=1000)
        
        # 存储记忆
        agent.store_memory(
            content="用户喜欢Python编程",
            memory_type=MemoryType.SEMANTIC,
            importance=MemoryImportance.HIGH,
            tags=["用户偏好", "编程语言"]
        )
        
        # 检索记忆
        results = agent.retrieve_memories(
            query="用户喜欢什么编程语言？",
            top_k=5
        )
        
        # 与记忆对话
        response = agent.chat_with_memory(
            "你知道我喜欢什么编程语言吗？"
        )
    """
    
    def __init__(
        self,
        llm_client=None,
        max_memories: int = 1000,
        strategy: MemoryStrategy = MemoryStrategy.HYBRID,
        short_term_duration: int = 3600,  # 短期记忆保留时长（秒）
        consolidation_threshold: int = 100,  # 记忆整合阈值
        verbose: bool = True,
        storage_path: Optional[str] = None  # 持久化存储路径
    ):
        """
        初始化记忆管理代理
        
        Args:
            llm_client: 大语言模型客户端
            max_memories: 最大记忆数量
            strategy: 记忆管理策略
            short_term_duration: 短期记忆保留时长（秒）
            consolidation_threshold: 触发记忆整合的阈值
            verbose: 是否打印详细信息
            storage_path: 持久化存储路径
        """
        self.llm_client = llm_client
        self.max_memories = max_memories
        self.strategy = strategy
        self.short_term_duration = short_term_duration
        self.consolidation_threshold = consolidation_threshold
        self.verbose = verbose
        self.storage_path = storage_path
        
        # 记忆存储（内存）
        self.memories: Dict[str, Memory] = {}
        
        # 索引：按类型
        self.type_index: Dict[MemoryType, List[str]] = defaultdict(list)
        
        # 索引：按标签
        self.tag_index: Dict[str, List[str]] = defaultdict(list)
        
        # 会话上下文（短期记忆）
        self.session_context: List[Dict[str, str]] = []
        
        # 工作记忆（当前任务相关）
        self.working_memory: Dict[str, Any] = {}
        
        # 从持久化存储加载
        if self.storage_path:
            self._load_from_storage()
        
        if self.verbose:
            print(f"✓ 记忆管理代理已初始化")
            print(f"  - 最大记忆数: {self.max_memories}")
            print(f"  - 管理策略: {self.strategy.value}")
            print(f"  - 当前记忆数: {len(self.memories)}")
    
    def _generate_memory_id(self, content: str) -> str:
        """生成记忆唯一ID"""
        timestamp = datetime.now().isoformat()
        unique_str = f"{content}_{timestamp}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def store_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.SEMANTIC,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Memory:
        """
        存储新记忆
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型
            importance: 重要性级别
            tags: 标签列表
            metadata: 元数据
            
        Returns:
            创建的记忆对象
        """
        # 生成记忆ID
        memory_id = self._generate_memory_id(content)
        
        # 创建记忆对象
        now = datetime.now().isoformat()
        memory = Memory(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            timestamp=now,
            last_accessed=now,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # 检查是否需要清理旧记忆
        if len(self.memories) >= self.max_memories:
            self._cleanup_memories()
        
        # 存储记忆
        self.memories[memory_id] = memory
        
        # 更新索引
        self.type_index[memory_type].append(memory_id)
        for tag in memory.tags:
            self.tag_index[tag].append(memory_id)
        
        if self.verbose:
            print(f"✓ 已存储记忆: {content[:50]}... (类型: {memory_type.value})")
        
        # 检查是否需要整合
        if len(self.memories) % self.consolidation_threshold == 0:
            self._consolidate_memories()
        
        # 持久化
        if self.storage_path:
            self._save_to_storage()
        
        return memory
    
    def retrieve_memories(
        self,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        tags: Optional[List[str]] = None,
        top_k: int = 5,
        min_importance: Optional[MemoryImportance] = None
    ) -> List[MemorySearchResult]:
        """
        检索相关记忆
        
        Args:
            query: 查询内容
            memory_types: 限定记忆类型
            tags: 限定标签
            top_k: 返回前K个结果
            min_importance: 最小重要性级别
            
        Returns:
            记忆搜索结果列表
        """
        candidate_ids = set(self.memories.keys())
        
        # 按类型过滤
        if memory_types:
            type_ids = set()
            for mem_type in memory_types:
                type_ids.update(self.type_index[mem_type])
            candidate_ids &= type_ids
        
        # 按标签过滤
        if tags:
            tag_ids = set()
            for tag in tags:
                tag_ids.update(self.tag_index[tag])
            candidate_ids &= tag_ids
        
        # 按重要性过滤
        if min_importance:
            candidate_ids = {
                mid for mid in candidate_ids
                if self.memories[mid].importance.value >= min_importance.value
            }
        
        # 计算相关性并排序
        results = []
        for memory_id in candidate_ids:
            memory = self.memories[memory_id]
            
            # 简单的相关性计算（基于关键词匹配）
            relevance = self._calculate_relevance(query, memory)
            
            # 更新访问信息
            memory.last_accessed = datetime.now().isoformat()
            memory.access_count += 1
            
            results.append(MemorySearchResult(
                memory=memory,
                relevance_score=relevance,
                reason=self._generate_retrieval_reason(query, memory, relevance)
            ))
        
        # 按相关性排序
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        if self.verbose:
            print(f"✓ 检索到 {len(results)} 条相关记忆（返回前 {top_k} 条）")
        
        return results[:top_k]
    
    def _calculate_relevance(self, query: str, memory: Memory) -> float:
        """计算查询与记忆的相关性"""
        query_lower = query.lower()
        content_lower = memory.content.lower()
        
        # 基础分数：关键词重叠
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())
        overlap = len(query_words & content_words)
        base_score = min(overlap / max(len(query_words), 1), 1.0)
        
        # 考虑重要性
        importance_bonus = memory.importance.value * 0.05
        
        # 考虑访问频率
        access_bonus = min(memory.access_count * 0.01, 0.1)
        
        # 考虑时间衰减（越新越好）
        time_diff = (datetime.now() - datetime.fromisoformat(memory.timestamp)).total_seconds()
        time_decay = 1.0 / (1.0 + time_diff / 86400)  # 按天衰减
        time_bonus = time_decay * 0.1
        
        total_score = min(base_score + importance_bonus + access_bonus + time_bonus, 1.0)
        
        return total_score
    
    def _generate_retrieval_reason(self, query: str, memory: Memory, score: float) -> str:
        """生成检索原因说明"""
        reasons = []
        
        if score > 0.7:
            reasons.append("高度相关")
        elif score > 0.5:
            reasons.append("相关")
        else:
            reasons.append("可能相关")
        
        if memory.importance.value >= 4:
            reasons.append("重要性高")
        
        if memory.access_count > 5:
            reasons.append("经常访问")
        
        # 检查标签匹配
        query_words = set(query.lower().split())
        matching_tags = [tag for tag in memory.tags if tag.lower() in query_words]
        if matching_tags:
            reasons.append(f"标签匹配: {', '.join(matching_tags)}")
        
        return "; ".join(reasons)
    
    def chat_with_memory(self, user_input: str, use_memory_types: Optional[List[MemoryType]] = None) -> str:
        """
        基于记忆的对话
        
        Args:
            user_input: 用户输入
            use_memory_types: 使用的记忆类型
            
        Returns:
            AI响应
        """
        if not self.llm_client:
            return "错误：未配置LLM客户端"
        
        # 检索相关记忆
        relevant_memories = self.retrieve_memories(
            query=user_input,
            memory_types=use_memory_types,
            top_k=5
        )
        
        # 构建上下文
        context_parts = []
        
        # 添加相关记忆
        if relevant_memories:
            context_parts.append("### 相关记忆：")
            for i, result in enumerate(relevant_memories, 1):
                context_parts.append(
                    f"{i}. [{result.memory.memory_type.value}] {result.memory.content} "
                    f"(相关性: {result.relevance_score:.2f})"
                )
            context_parts.append("")
        
        # 添加会话上下文（最近5轮对话）
        if self.session_context:
            context_parts.append("### 最近对话：")
            for msg in self.session_context[-10:]:
                role = "用户" if msg["role"] == "user" else "助手"
                context_parts.append(f"{role}: {msg['content']}")
            context_parts.append("")
        
        # 添加工作记忆
        if self.working_memory:
            context_parts.append("### 当前任务信息：")
            for key, value in self.working_memory.items():
                context_parts.append(f"- {key}: {value}")
            context_parts.append("")
        
        context = "\n".join(context_parts)
        
        # 构建提示词
        prompt = f"""你是一个具有记忆能力的AI助手。请基于提供的记忆和上下文信息回答用户的问题。

{context}

用户问题: {user_input}

请提供准确、有帮助的回答。如果记忆中没有相关信息，请如实告知。"""
        
        # 调用LLM
        response = self.llm_client.simple_chat(prompt)
        
        # 更新会话上下文
        self.session_context.append({"role": "user", "content": user_input})
        self.session_context.append({"role": "assistant", "content": response})
        
        # 自动存储重要对话为记忆
        if self._is_important_conversation(user_input, response):
            self.store_memory(
                content=f"用户问: {user_input} | 助手答: {response}",
                memory_type=MemoryType.EPISODIC,
                importance=MemoryImportance.MEDIUM,
                tags=["对话", "自动记录"]
            )
        
        return response
    
    def _is_important_conversation(self, user_input: str, response: str) -> bool:
        """判断对话是否重要，需要存储"""
        # 简单规则：包含特定关键词的对话更重要
        important_keywords = [
            "记住", "保存", "重要", "喜欢", "不喜欢", "偏好",
            "经常", "总是", "从不", "习惯", "计划", "目标"
        ]
        
        combined = f"{user_input} {response}".lower()
        return any(keyword in combined for keyword in important_keywords)
    
    def _cleanup_memories(self):
        """清理旧记忆以腾出空间"""
        if self.verbose:
            print(f"⚠️  记忆数量达到上限，开始清理...")
        
        if self.strategy == MemoryStrategy.FIFO:
            self._cleanup_fifo()
        elif self.strategy == MemoryStrategy.LRU:
            self._cleanup_lru()
        elif self.strategy == MemoryStrategy.IMPORTANCE:
            self._cleanup_by_importance()
        else:  # HYBRID
            self._cleanup_hybrid()
    
    def _cleanup_fifo(self):
        """先进先出清理"""
        sorted_memories = sorted(
            self.memories.values(),
            key=lambda m: m.timestamp
        )
        to_remove = sorted_memories[:len(self.memories) // 10]  # 删除10%
        for memory in to_remove:
            self._remove_memory(memory.id)
    
    def _cleanup_lru(self):
        """最近最少使用清理"""
        sorted_memories = sorted(
            self.memories.values(),
            key=lambda m: (m.last_accessed, m.access_count)
        )
        to_remove = sorted_memories[:len(self.memories) // 10]
        for memory in to_remove:
            self._remove_memory(memory.id)
    
    def _cleanup_by_importance(self):
        """按重要性清理"""
        sorted_memories = sorted(
            self.memories.values(),
            key=lambda m: (m.importance.value, m.access_count)
        )
        to_remove = sorted_memories[:len(self.memories) // 10]
        for memory in to_remove:
            if memory.importance.value <= MemoryImportance.LOW.value:
                self._remove_memory(memory.id)
    
    def _cleanup_hybrid(self):
        """混合策略清理"""
        # 计算每个记忆的综合分数
        scored_memories = []
        for memory in self.memories.values():
            # 时间分数（越新越高）
            age_days = (datetime.now() - datetime.fromisoformat(memory.timestamp)).days
            time_score = 1.0 / (1.0 + age_days)
            
            # 重要性分数
            importance_score = memory.importance.value / 5.0
            
            # 访问分数
            access_score = min(memory.access_count / 10.0, 1.0)
            
            # 综合分数
            total_score = (time_score * 0.3 + importance_score * 0.5 + access_score * 0.2)
            
            scored_memories.append((memory, total_score))
        
        # 删除分数最低的10%
        sorted_memories = sorted(scored_memories, key=lambda x: x[1])
        to_remove = sorted_memories[:len(self.memories) // 10]
        for memory, _ in to_remove:
            self._remove_memory(memory.id)
    
    def _remove_memory(self, memory_id: str):
        """删除记忆"""
        if memory_id in self.memories:
            memory = self.memories[memory_id]
            
            # 从主存储删除
            del self.memories[memory_id]
            
            # 从索引删除
            if memory_id in self.type_index[memory.memory_type]:
                self.type_index[memory.memory_type].remove(memory_id)
            
            for tag in memory.tags:
                if memory_id in self.tag_index[tag]:
                    self.tag_index[tag].remove(memory_id)
    
    def _consolidate_memories(self):
        """整合记忆：合并相似记忆，提取关键信息"""
        if not self.llm_client or len(self.memories) < 10:
            return
        
        if self.verbose:
            print(f"🔄 开始记忆整合...")
        
        # 这里可以实现更复杂的记忆整合逻辑
        # 例如：使用LLM识别和合并相似记忆，提取关键信息等
        pass
    
    def update_working_memory(self, key: str, value: Any):
        """更新工作记忆"""
        self.working_memory[key] = value
        if self.verbose:
            print(f"✓ 更新工作记忆: {key} = {value}")
    
    def clear_working_memory(self):
        """清空工作记忆"""
        self.working_memory.clear()
        if self.verbose:
            print("✓ 已清空工作记忆")
    
    def clear_session_context(self):
        """清空会话上下文"""
        self.session_context.clear()
        if self.verbose:
            print("✓ 已清空会话上下文")
    
    def get_memory_by_id(self, memory_id: str) -> Optional[Memory]:
        """根据ID获取记忆"""
        return self.memories.get(memory_id)
    
    def get_memories_by_type(self, memory_type: MemoryType) -> List[Memory]:
        """获取指定类型的所有记忆"""
        memory_ids = self.type_index[memory_type]
        return [self.memories[mid] for mid in memory_ids if mid in self.memories]
    
    def get_memories_by_tag(self, tag: str) -> List[Memory]:
        """获取指定标签的所有记忆"""
        memory_ids = self.tag_index[tag]
        return [self.memories[mid] for mid in memory_ids if mid in self.memories]
    
    def get_statistics(self) -> MemoryStats:
        """获取记忆统计信息"""
        if not self.memories:
            return MemoryStats(
                total_memories=0,
                by_type={},
                by_importance={},
                oldest_memory=None,
                newest_memory=None,
                most_accessed=None,
                storage_size_bytes=0
            )
        
        # 按类型统计
        by_type = {}
        for mem_type in MemoryType:
            count = len(self.type_index[mem_type])
            if count > 0:
                by_type[mem_type.value] = count
        
        # 按重要性统计
        by_importance = {}
        for memory in self.memories.values():
            imp_key = memory.importance.name
            by_importance[imp_key] = by_importance.get(imp_key, 0) + 1
        
        # 最老和最新的记忆
        sorted_by_time = sorted(self.memories.values(), key=lambda m: m.timestamp)
        oldest = sorted_by_time[0].timestamp if sorted_by_time else None
        newest = sorted_by_time[-1].timestamp if sorted_by_time else None
        
        # 最常访问的记忆
        most_accessed = max(self.memories.values(), key=lambda m: m.access_count)
        
        # 存储大小（估算）
        storage_size = sum(
            len(json.dumps(m.to_dict()).encode('utf-8'))
            for m in self.memories.values()
        )
        
        return MemoryStats(
            total_memories=len(self.memories),
            by_type=by_type,
            by_importance=by_importance,
            oldest_memory=oldest,
            newest_memory=newest,
            most_accessed=most_accessed,
            storage_size_bytes=storage_size
        )
    
    def _save_to_storage(self):
        """持久化存储记忆"""
        if not self.storage_path:
            return
        
        try:
            data = {
                "memories": [m.to_dict() for m in self.memories.values()],
                "session_context": self.session_context,
                "working_memory": self.working_memory,
                "metadata": {
                    "saved_at": datetime.now().isoformat(),
                    "total_memories": len(self.memories)
                }
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  保存记忆失败: {e}")
    
    def _load_from_storage(self):
        """从持久化存储加载记忆"""
        if not self.storage_path:
            return
        
        try:
            import os
            if not os.path.exists(self.storage_path):
                return
            
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载记忆
            for mem_dict in data.get("memories", []):
                memory = Memory.from_dict(mem_dict)
                self.memories[memory.id] = memory
                
                # 重建索引
                self.type_index[memory.memory_type].append(memory.id)
                for tag in memory.tags:
                    self.tag_index[tag].append(memory.id)
            
            # 加载会话上下文
            self.session_context = data.get("session_context", [])
            
            # 加载工作记忆
            self.working_memory = data.get("working_memory", {})
            
            if self.verbose:
                print(f"✓ 从存储加载了 {len(self.memories)} 条记忆")
        
        except Exception as e:
            if self.verbose:
                print(f"⚠️  加载记忆失败: {e}")
    
    def export_memories(self, filepath: str, memory_types: Optional[List[MemoryType]] = None):
        """导出记忆到文件"""
        memories_to_export = []
        
        if memory_types:
            for mem_type in memory_types:
                memories_to_export.extend(self.get_memories_by_type(mem_type))
        else:
            memories_to_export = list(self.memories.values())
        
        data = {
            "exported_at": datetime.now().isoformat(),
            "total_count": len(memories_to_export),
            "memories": [m.to_dict() for m in memories_to_export]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        if self.verbose:
            print(f"✓ 已导出 {len(memories_to_export)} 条记忆到 {filepath}")
    
    def import_memories(self, filepath: str):
        """从文件导入记忆"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        imported_count = 0
        for mem_dict in data.get("memories", []):
            memory = Memory.from_dict(mem_dict)
            
            # 避免重复
            if memory.id not in self.memories:
                self.memories[memory.id] = memory
                self.type_index[memory.memory_type].append(memory.id)
                for tag in memory.tags:
                    self.tag_index[tag].append(memory.id)
                imported_count += 1
        
        if self.verbose:
            print(f"✓ 已导入 {imported_count} 条新记忆")
        
        # 持久化
        if self.storage_path:
            self._save_to_storage()

