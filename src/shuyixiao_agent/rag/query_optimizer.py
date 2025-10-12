"""
查询优化模块

支持查询重写、问题修订、子问题扩展等
"""

from typing import List, Optional, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from ..gitee_ai_client import GiteeAIClient
from ..config import settings


class QueryOptimizer:
    """
    查询优化器
    
    提供查询重写、问题修订、子问题扩展等功能
    """
    
    def __init__(
        self,
        client: Optional[GiteeAIClient] = None,
        enable_query_rewrite: Optional[bool] = None,
        enable_subquery_expansion: Optional[bool] = None,
        max_subqueries: Optional[int] = None
    ):
        """
        初始化查询优化器
        
        Args:
            client: GiteeAI 客户端
            enable_query_rewrite: 是否启用查询重写
            enable_subquery_expansion: 是否启用子查询扩展
            max_subqueries: 最大子查询数量
        """
        # 如果配置了专用的查询优化模型，使用该模型
        if settings.query_optimizer_model:
            self.client = client or GiteeAIClient(model=settings.query_optimizer_model)
        else:
            self.client = client or GiteeAIClient()
        self.enable_query_rewrite = (
            enable_query_rewrite 
            if enable_query_rewrite is not None 
            else settings.enable_query_rewrite
        )
        self.enable_subquery_expansion = (
            enable_subquery_expansion
            if enable_subquery_expansion is not None
            else settings.enable_subquery_expansion
        )
        self.max_subqueries = max_subqueries or settings.max_subqueries
    
    def rewrite_query(
        self,
        query: str,
        context: Optional[str] = None
    ) -> str:
        """
        重写查询以提高检索质量
        
        Args:
            query: 原始查询
            context: 上下文信息（如对话历史）
            
        Returns:
            重写后的查询
        """
        if not self.enable_query_rewrite:
            return query
        
        system_prompt = """你是一个查询重写专家。你的任务是将用户的查询重写为更适合检索的形式。

重写原则：
1. 保持查询的核心意图不变
2. 使查询更加明确和具体
3. 补充必要的上下文信息
4. 使用更适合检索的关键词
5. 如果查询已经很清晰，可以保持原样

只输出重写后的查询，不要输出其他内容。"""
        
        user_prompt = f"原始查询：{query}"
        
        if context:
            user_prompt += f"\n\n上下文：{context}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=200
            )
            
            rewritten_query = response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            return rewritten_query if rewritten_query else query
        except Exception as e:
            print(f"查询重写失败: {e}")
            return query
    
    def revise_query_with_history(
        self,
        query: str,
        history: List[Dict[str, str]]
    ) -> str:
        """
        基于对话历史修订查询
        
        Args:
            query: 当前查询
            history: 对话历史
            
        Returns:
            修订后的查询
        """
        if not history:
            return query
        
        system_prompt = """你是一个对话理解专家。你的任务是根据对话历史理解当前查询的完整意图。

任务：
1. 分析对话历史，理解上下文
2. 识别当前查询中的代词和省略部分
3. 将当前查询改写为独立的、完整的查询
4. 保持查询的自然性

只输出修订后的查询，不要输出其他内容。"""
        
        # 构建历史上下文
        history_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in history[-5:]  # 只使用最近5轮对话
        ])
        
        user_prompt = f"""对话历史：
{history_text}

当前查询：{query}

请将当前查询改写为独立完整的查询："""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=200
            )
            
            revised_query = response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            return revised_query if revised_query else query
        except Exception as e:
            print(f"查询修订失败: {e}")
            return query
    
    def expand_to_subqueries(
        self,
        query: str,
        max_subqueries: Optional[int] = None
    ) -> List[str]:
        """
        将复杂查询扩展为多个子查询
        
        Args:
            query: 原始查询
            max_subqueries: 最大子查询数量
            
        Returns:
            子查询列表
        """
        if not self.enable_subquery_expansion:
            return [query]
        
        max_subs = max_subqueries or self.max_subqueries
        
        system_prompt = f"""你是一个查询分解专家。你的任务是将复杂查询分解为多个简单的子查询。

分解原则：
1. 识别查询中的多个方面或维度
2. 将每个方面转化为独立的子查询
3. 子查询应该简单、明确、易于检索
4. 最多生成 {max_subs} 个子查询
5. 如果查询已经很简单，只需返回原查询

输出格式（每行一个子查询）：
子查询1
子查询2
子查询3"""
        
        user_prompt = f"查询：{query}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.5,
                max_tokens=300
            )
            
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            # 解析子查询
            subqueries = [
                line.strip()
                for line in content.split("\n")
                if line.strip()
            ]
            
            # 限制数量
            subqueries = subqueries[:max_subs]
            
            return subqueries if subqueries else [query]
        except Exception as e:
            print(f"子查询扩展失败: {e}")
            return [query]
    
    def optimize_query(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
        enable_expansion: bool = False
    ) -> Dict[str, Any]:
        """
        综合查询优化
        
        Args:
            query: 原始查询
            history: 对话历史
            enable_expansion: 是否启用子查询扩展
            
        Returns:
            优化结果字典，包含：
            - original_query: 原始查询
            - revised_query: 修订后的查询
            - rewritten_query: 重写后的查询
            - subqueries: 子查询列表
        """
        result = {
            "original_query": query,
            "revised_query": query,
            "rewritten_query": query,
            "subqueries": [query]
        }
        
        # 1. 基于历史修订查询
        if history:
            revised = self.revise_query_with_history(query, history)
            result["revised_query"] = revised
            query = revised
        
        # 2. 重写查询
        if self.enable_query_rewrite:
            rewritten = self.rewrite_query(query)
            result["rewritten_query"] = rewritten
            query = rewritten
        
        # 3. 扩展为子查询
        if enable_expansion and self.enable_subquery_expansion:
            subqueries = self.expand_to_subqueries(query)
            result["subqueries"] = subqueries
        else:
            result["subqueries"] = [query]
        
        return result

