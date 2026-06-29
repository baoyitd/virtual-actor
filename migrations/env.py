"""Alembic 异步迁移环境"""
import asyncio
import os
import sys
from logging.config import fileConfig

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 加载 .env（Alembic 调用时默认不会自动加载）
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Alembic Config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.config import settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# 导入所有模型确保 Base.metadata 完整
from app.database import Base
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

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式：生成 SQL 不连接数据库"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """在线模式：异步连接数据库并运行迁移"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """在线模式入口"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
