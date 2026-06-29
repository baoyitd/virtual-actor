"""应用配置，从环境变量读取"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """全局配置单例"""

    # MySQL
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_NAME: str = os.getenv("DB_NAME", "virtual_actor")

    @property
    def database_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset=utf8mb4"
        )

    # 知识平台（Knowledge Workbench 公共契约接口）
    KNOWLEDGE_API_BASE: str = os.getenv("KNOWLEDGE_API_BASE", "http://localhost:3099")
    KNOWLEDGE_DEFAULT_PACKAGE_ID: str = os.getenv("KNOWLEDGE_DEFAULT_PACKAGE_ID", "eve")

    # LLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "")

    # AI 推荐链路模型配置
    AI_RECOMMEND_MODEL: str = os.getenv("AI_RECOMMEND_MODEL", "deepseek-v4-pro")
    AI_RECOMMEND_TEMPERATURE: float = float(os.getenv("AI_RECOMMEND_TEMPERATURE", "0.3"))
    AI_RECOMMEND_MAX_TOKENS: int = int(os.getenv("AI_RECOMMEND_MAX_TOKENS", "4096"))

    # AI 创建草案链路模型配置
    AI_CREATE_MODEL: str = os.getenv("AI_CREATE_MODEL", "deepseek-v4-pro")
    AI_CREATE_TEMPERATURE: float = float(os.getenv("AI_CREATE_TEMPERATURE", "0.7"))
    AI_CREATE_MAX_TOKENS: int = int(os.getenv("AI_CREATE_MAX_TOKENS", "4096"))

    # 内部商业试用基础账号
    AUTH_USERNAME: str = os.getenv("AUTH_USERNAME", "admin")
    AUTH_PASSWORD: str = os.getenv("AUTH_PASSWORD", "admin123")
    AUTH_SECRET: str = os.getenv("AUTH_SECRET", "virtual-actor-dev-secret")
    AUTH_TOKEN_TTL_HOURS: int = int(os.getenv("AUTH_TOKEN_TTL_HOURS", "12"))


settings = Settings()
