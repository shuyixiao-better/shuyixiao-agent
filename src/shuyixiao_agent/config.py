"""
配置管理模块

使用 pydantic-settings 管理环境变量和配置
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    
    # 码云 AI API 配置
    gitee_ai_api_key: str = ""
    gitee_ai_base_url: str = "https://ai.gitee.com/api/serverless"
    gitee_ai_model: str = "Qwen/Qwen2.5-7B-Instruct"
    
    # Agent 配置
    agent_max_iterations: int = 10
    agent_verbose: bool = True
    
    # 请求配置
    request_timeout: int = 60
    max_retries: int = 3
    
    # 故障转移
    enable_failover: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# 全局配置实例
settings = Settings()

