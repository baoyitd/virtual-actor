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

    # 知识平台（Open WebUI）
    KNOWLEDGE_API_BASE: str = os.getenv("KNOWLEDGE_API_BASE", "http://localhost:3000")
    KNOWLEDGE_HEALTH_URL: str = os.getenv("KNOWLEDGE_HEALTH_URL", "http://localhost:3099/api/health")
    KNOWLEDGE_API_TOKEN: str = os.getenv("KNOWLEDGE_API_TOKEN", "")
    KNOWLEDGE_AUTH_EMAIL: str = os.getenv("KNOWLEDGE_AUTH_EMAIL", "")
    KNOWLEDGE_AUTH_PASSWORD: str = os.getenv("KNOWLEDGE_AUTH_PASSWORD", "")
    KNOWLEDGE_DEFAULT_KB_ID: str = os.getenv(
        "KNOWLEDGE_DEFAULT_KB_ID",
        "41cee65b-7f9c-4820-ba0d-bb865e0b1e41",
    )

    # LLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "")

    # 内部商业试用基础账号
    AUTH_USERNAME: str = os.getenv("AUTH_USERNAME", "admin")
    AUTH_PASSWORD: str = os.getenv("AUTH_PASSWORD", "admin123")
    AUTH_SECRET: str = os.getenv("AUTH_SECRET", "virtual-actor-dev-secret")
    AUTH_TOKEN_TTL_HOURS: int = int(os.getenv("AUTH_TOKEN_TTL_HOURS", "12"))


settings = Settings()
