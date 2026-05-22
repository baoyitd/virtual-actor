"""测试运行服务 — 知识平台检索 + 角色产品自有 LLM"""
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_run import TestRunRecord
from app.services.role_service import RoleService
from app.services.llm_service import llm_service, PromptBuilder
from app.services.knowledge_platform import knowledge_platform


class TestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_service = RoleService(db)

    async def run_test(self, role_id: str, test_input: str) -> TestRunRecord | None:
        """运行角色测试：
        1. 知识平台检索知识
        2. 拼接知识到 prompt
        3. 角色产品自有 LLM 执行
        """
        role = await self.role_service.get(role_id)
        if not role:
            return None
        if not role.knowledge_refs:
            raise ValueError("测试前至少需要绑定 1 条知识")
        if not await knowledge_platform.health():
            raise ValueError("知识平台不可达，无法运行角色测试")

        version_fields = {}
        if role.current_version_id:
            version_fields = await self.role_service.get_version_fields(role.current_version_id)

        # 角色自有 model_binding
        model_binding = version_fields.get("model_binding", {})
        if isinstance(model_binding, dict):
            model_name = model_binding.get("model_name", "deepseek-v4-pro")
            temperature = model_binding.get("temperature", 0.7)
            max_tokens = model_binding.get("max_tokens", 4096)
        else:
            model_name, temperature, max_tokens = "deepseek-v4-pro", 0.7, 4096

        system_prompt = PromptBuilder.build(role.name, role.bio, version_fields)
        sources = []

        # 步骤1：知识平台检索知识。当前检索仍按知识库 collection 执行，文件级绑定只用于展示与追溯。
        collection_names = sorted(
            {
                ref.kb_id or knowledge_platform.kb_eve_id
                for ref in role.knowledge_refs
            }
        ) or [knowledge_platform.kb_eve_id]
        chunks = await knowledge_platform.retrieve(collection_names, test_input)
        if chunks and chunks[0].get("error"):
            raise ValueError("知识平台检索失败，无法运行角色测试")
        if chunks:
            sources = [{"source": c["source"], "score": c["score"]} for c in chunks]
            system_prompt = knowledge_platform.build_prompt_with_knowledge(system_prompt, chunks)

        # 步骤2：角色产品自有 LLM 执行
        test_output = await llm_service.chat(
            system_prompt=system_prompt,
            user_message=test_input,
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if test_output.startswith("[LLM 调用失败"):
            test_output = f"⚠️ LLM 不可达，请检查 .env 中 LLM_API_KEY 配置。\n{test_output}"

        record = TestRunRecord(
            role_id=role_id,
            version_id=role.current_version_id,
            test_input=test_input,
            test_output=test_output,
            knowledge_retrieved=sources,
            tested_at=datetime.now(timezone.utc),
        )
        self.db.add(record)
        await self.db.flush()
        return record

    async def get_test_history(self, role_id: str) -> list[TestRunRecord]:
        stmt = (
            select(TestRunRecord)
            .where(TestRunRecord.role_id == role_id)
            .order_by(TestRunRecord.tested_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def rate_test(self, test_id: str, rating: int) -> TestRunRecord | None:
        stmt = (
            update(TestRunRecord)
            .where(TestRunRecord.id == test_id)
            .values(human_rating=rating)
        )
        await self.db.execute(stmt)
        await self.db.flush()

        result = await self.db.execute(
            select(TestRunRecord).where(TestRunRecord.id == test_id)
        )
        return result.scalar_one_or_none()
