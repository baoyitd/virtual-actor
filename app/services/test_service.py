"""兼容测试运行服务"""
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_run import TestRunRecord
from app.schemas.role import CallerType
from app.services.consume_service import ConsumeService
from app.services.role_service import RoleService


class TestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_service = RoleService(db)
        self.consume_service = ConsumeService(db)

    async def run_test(self, role_id: str, test_input: str) -> TestRunRecord | None:
        role = await self.role_service.get(role_id)
        if not role or not role.current_version_id:
            return None
        result = await self.consume_service._execute(
            role_id=role.id,
            role_name=role.name,
            role_bio=role.bio,
            version_id=role.current_version_id,
            query=test_input,
            context=None,
            caller_type=CallerType.HUMAN.value,
            caller_id="legacy-test",
            output_type_override=None,
        )
        record = TestRunRecord(
            role_id=role_id,
            version_id=role.current_version_id,
            test_input=test_input,
            test_output=result["answer"],
            knowledge_retrieved=result["sources"],
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
        await self.db.execute(
            update(TestRunRecord).where(TestRunRecord.id == test_id).values(human_rating=rating)
        )
        await self.db.flush()
        result = await self.db.execute(select(TestRunRecord).where(TestRunRecord.id == test_id))
        return result.scalar_one_or_none()
