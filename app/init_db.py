"""数据库初始化脚本：创建数据库和表"""
import asyncio
from app.database import engine, Base

# 导入所有模型，确保注册到 Base.metadata
from app.models.role_asset import RoleAsset  # noqa
from app.models.role_version import RoleVersion, RoleVersionField  # noqa
from app.models.knowledge_ref import KnowledgeRef, ValidatedKnowledgeVersion  # noqa
from app.models.test_run import TestRunRecord  # noqa
from app.models.usage_record import UsageRecord  # noqa
from app.models.test_validation_record import TestValidationRecord  # noqa
from app.models.ops_signal import OpsSignal  # noqa
from app.models.data_asset import DataAsset  # noqa
from app.models.role_briefing import RoleBriefing  # noqa
from app.models.export_package import RoleExportPackage  # noqa
from app.models.business_domain import BusinessDomain  # noqa
from app.models.enterprise_role import EnterpriseRole  # noqa
from app.models.staff_directory import StaffDirectory  # noqa


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表创建完成")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
