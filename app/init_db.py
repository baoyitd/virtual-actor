"""数据库初始化脚本：创建数据库和表"""
import asyncio
from app.database import engine, Base

# 导入所有模型，确保注册到 Base.metadata
from app.models.role_asset import RoleAsset  # noqa
from app.models.role_version import RoleVersion, RoleVersionField  # noqa
from app.models.knowledge_ref import KnowledgeRef, ValidatedKnowledgeVersion  # noqa
from app.models.test_run import TestRunRecord  # noqa


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表创建完成")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())