"""
配置管理模块

使用 pydantic-settings 管理环境变量和配置
支持从 .env 文件或 PyCharm 环境变量中读取配置
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置类
    
    在 PyCharm 中配置环境变量的方法：
    1. 打开 Run -> Edit Configurations
    2. 选择你的运行配置
    3. 在 Environment variables 中添加以下变量：
       - GITEE_AI_API_KEY=你的API密钥
       - GITEE_AI_BASE_URL=https://ai.gitee.com/v1
       - GITEE_AI_MODEL=DeepSeek-V3
       等等
    """
    
    # 码云 AI API 配置
    gitee_ai_api_key: str = Field(
        default="",
        description="Gitee AI API 密钥"
    )
    gitee_ai_base_url: str = Field(
        default="https://ai.gitee.com/v1",
        description="Gitee AI API 基础 URL"
    )
    gitee_ai_model: str = Field(
        default="DeepSeek-V3",
        description="默认使用的模型名称"
    )
    
    # Agent 配置
    agent_max_iterations: int = Field(
        default=10,
        description="Agent 最大迭代次数"
    )
    agent_verbose: bool = Field(
        default=True,
        description="是否输出详细日志"
    )
    
    # 请求配置
    request_timeout: int = Field(
        default=60,
        description="请求超时时间（秒）"
    )
    max_retries: int = Field(
        default=3,
        description="最大重试次数"
    )
    
    # 故障转移
    enable_failover: bool = Field(
        default=True,
        description="是否启用故障转移"
    )
    
    # SSL 配置
    ssl_verify: bool = Field(
        default=False,
        description="是否验证 SSL 证书（如遇到 SSL 错误可设为 False）"
    )
    
    model_config = SettingsConfigDict(
        # 优先从环境变量读取，然后从 .env 文件读取
        env_file=".env" if os.path.exists(".env") else None,
        env_file_encoding="utf-8",
        # 不区分大小写，这样 GITEE_AI_API_KEY 和 gitee_ai_api_key 都能识别
        case_sensitive=False,
        # 忽略额外的环境变量
        extra="ignore",
        # 支持从环境变量前缀读取（可选）
        # env_prefix="",
    )


# 全局配置实例
settings = Settings()

