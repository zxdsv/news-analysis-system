"""
全局配置文件
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用全局设置"""

    # 应用基础配置
    app_name: str = "News Analysis System"
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # DeepSeek API 配置
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_api_url: str = os.getenv(
        "DEEPSEEK_API_URL", "https://api.deepseek.com/v1"
    )
    deepseek_model: str = "deepseek-chat"
    deepseek_temperature: float = 0.7
    deepseek_max_tokens: int = 2000

    # Chroma 向量库配置
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
    chroma_collection_name: str = os.getenv(
        "CHROMA_COLLECTION_NAME", "news_articles"
    )

    # SQLite 数据库配置
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/news.db")

    # Redis 缓存配置
    redis_url: Optional[str] = os.getenv("REDIS_URL", None)
    redis_ttl: int = 3600  # 秒

    # 新闻源配置
    fetch_interval: int = int(os.getenv("FETCH_INTERVAL", 3600))  # 秒
    max_articles_per_fetch: int = 50

    # API 服务器配置
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", 8000))

    # 模型参数
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 500
    chunk_overlap: int = 100

    # RAG 配置
    top_k_retrieval: int = 5  # 检索前K条相似文档
    similarity_threshold: float = 0.5

    # Agent 配置
    agent_timeout: int = 30  # 秒
    agent_max_retries: int = 3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
