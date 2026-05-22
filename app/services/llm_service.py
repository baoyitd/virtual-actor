"""LLM 调用服务 — 构建 prompt 并调用大模型"""
import httpx
from app.config import settings


class LLMService:
    """通用 LLM 调用服务，支持 OpenAI 兼容 API"""

    def __init__(self):
        base_url = settings.LLM_BASE_URL or (
            "https://api.openai.com" if settings.LLM_PROVIDER == "openai" else ""
        )
        self.base_url = base_url.rstrip("/")
        self.api_key = settings.LLM_API_KEY
        self.provider = settings.LLM_PROVIDER

    def _configuration_error(self) -> str | None:
        if not self.base_url:
            return "LLM_BASE_URL 未配置"
        if not self.base_url.startswith(("http://", "https://")):
            return f"LLM_BASE_URL 缺少协议头: {self.base_url}"
        if not self.api_key:
            return "LLM_API_KEY 未配置"
        return None

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """调用 LLM 获取角色回复"""
        config_error = self._configuration_error()
        if config_error:
            return f"[LLM 调用失败: {config_error}]"

        url = f"{self.base_url}/v1/chat/completions" if self.base_url else ""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                return f"[LLM 调用失败: {e}]"


class PromptBuilder:
    """角色 System Prompt 构建器"""

    @staticmethod
    def build(role_name: str, bio: str, fields: dict, knowledge_chunks: list[str] | None = None) -> str:
        """基于角色5层模型构建 system prompt"""
        parts = []

        # L1 身份
        parts.append(f"你是{role_name}。")
        if bio:
            parts.append(f"简介：{bio}")
        parts.append("请始终以这个角色的身份和立场来回答问题。")

        # L2 心智
        mind_fields = [
            ("identity_background", "背景"),
            ("point_of_view", "核心立场"),
            ("decision_style", "决策风格"),
            ("responsibility_boundary", "职责边界"),
            ("speaking_style", "表达风格"),
        ]
        for key, label in mind_fields:
            if key in fields:
                parts.append(f"{label}：{fields[key]}")

        # L3 知识
        if knowledge_chunks:
            parts.append("\n请基于以下知识内容回答：")
            for i, chunk in enumerate(knowledge_chunks, 1):
                parts.append(f"[知识{i}] {chunk}")

        return "\n\n".join(parts)


# 单例
llm_service = LLMService()
