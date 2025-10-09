"""
码云 AI API 客户端封装

提供与码云 AI Serverless API 交互的客户端类
"""

import requests
from typing import Dict, List, Optional, Iterator, Any
import json
from .config import settings


class GiteeAIClient:
    """码云 AI API 客户端"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        enable_failover: bool = True
    ):
        """
        初始化码云 AI 客户端
        
        Args:
            api_key: API 访问令牌，如果不提供则从配置中读取
            base_url: API 基础 URL，如果不提供则使用默认值
            model: 使用的模型名称，如果不提供则使用默认模型
            enable_failover: 是否启用故障转移机制
        """
        self.api_key = api_key or settings.gitee_ai_api_key
        self.base_url = base_url or settings.gitee_ai_base_url
        self.model = model or settings.gitee_ai_model
        self.enable_failover = enable_failover
        
        if not self.api_key:
            raise ValueError(
                "未提供 API Key。请通过参数传入或在 .env 文件中设置 GITEE_AI_API_KEY"
            )
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # 添加故障转移标识
        if self.enable_failover:
            headers["X-Failover-Enabled"] = "true"
        else:
            headers["X-Failover-Enabled"] = "false"
            
        return headers
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        调用聊天补全 API
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            temperature: 温度参数，控制随机性 (0-2)
            max_tokens: 最大生成 token 数
            stream: 是否使用流式输出
            **kwargs: 其他模型参数
            
        Returns:
            API 响应字典
        """
        url = f"{self.base_url}/{self.model}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=settings.request_timeout,
                stream=stream
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream_response(response)
            else:
                return response.json()
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 请求失败: {str(e)}")
    
    def _handle_stream_response(self, response: requests.Response) -> Iterator[Dict]:
        """
        处理流式响应
        
        Args:
            response: requests 响应对象
            
        Yields:
            每个数据块的字典
        """
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # 去掉 'data: ' 前缀
                    if data_str.strip() == '[DONE]':
                        break
                    try:
                        yield json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
    
    def simple_chat(self, user_message: str, system_message: Optional[str] = None) -> str:
        """
        简单的单轮对话方法
        
        Args:
            user_message: 用户消息
            system_message: 系统提示词（可选）
            
        Returns:
            模型回复的文本内容
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": user_message})
        
        response = self.chat_completion(messages=messages)
        
        return response["choices"][0]["message"]["content"]
    
    def get_embedding(self, text: str) -> List[float]:
        """
        获取文本的向量表示（如果模型支持）
        
        Args:
            text: 输入文本
            
        Returns:
            向量列表
        """
        # 注意：需要根据实际支持的向量化模型调整
        # 这里仅作为接口示例
        url = f"{self.base_url}/embeddings"
        
        payload = {
            "model": "text-embedding-ada-002",  # 示例模型名
            "input": text
        }
        
        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=settings.request_timeout
            )
            response.raise_for_status()
            result = response.json()
            return result["data"][0]["embedding"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取 embedding 失败: {str(e)}")

