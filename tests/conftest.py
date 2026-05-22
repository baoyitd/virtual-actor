"""pytest 配置：测试环境使用 SQLite 内存数据库"""
import os
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# 强制使用 SQLite 运行测试
os.environ["DB_TESTING"] = "1"

TEST_DB_URL = "sqlite+aiosqlite://"


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """创建测试专用 SQLite 引擎"""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def setup_db(test_engine, monkeypatch):
    """每个测试前：建表 + 注入测试数据库会话"""
    from app.database import Base
    from app import database as db_module

    # 导入所有模型
    from app.models.role_asset import RoleAsset  # noqa
    from app.models.role_version import RoleVersion, RoleVersionField  # noqa
    from app.models.knowledge_ref import KnowledgeRef, ValidatedKnowledgeVersion  # noqa
    from app.models.test_run import TestRunRecord  # noqa

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 覆盖数据库依赖
    test_sessionmaker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with test_sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    monkeypatch.setattr(db_module, "get_db", override_get_db)
    monkeypatch.setattr(db_module, "AsyncSessionLocal", test_sessionmaker)

    # 测试只验证角色产品行为，外部知识平台与 LLM 用确定性替身隔离网络。
    from app.services.knowledge_platform import knowledge_platform
    from app.services.llm_service import llm_service
    monkeypatch.setattr(knowledge_platform, "kb_eve_id", "kb-eve")

    async def fake_health():
        return True

    async def fake_current_version_id():
        return "test-knowledge-version"

    async def fake_list_knowledge_bases():
        return [
            {"id": "kb-eve", "name": "knowledge-eve"},
            {"id": "kb-ops", "name": "运营治理知识"},
        ]

    async def fake_list_files(kb_id=None, page_size=50):
        kid = kb_id or "kb-eve"
        fixtures = {
            "kb-eve": [
                {
                    "id": "file-1",
                    "filename": "治理测试知识.md",
                    "meta": {
                        "knowledge_object_id": "eve/test",
                        "knowledge_version_id": "test-knowledge-version",
                        "title": "治理测试知识",
                        "type": "policy",
                        "tags": ["治理"],
                        "summary": "用于测试的知识平台条目",
                    },
                },
                {
                    "id": "file-2",
                    "filename": "经营分析知识.md",
                    "meta": {
                        "knowledge_object_id": "eve/finance/report.md",
                        "knowledge_version_id": "test-knowledge-version",
                        "title": "经营分析知识",
                        "type": "report",
                        "tags": ["经营", "分析"],
                        "summary": "用于目录树和搜索的第二条测试知识",
                    },
                },
            ],
            "kb-ops": [
                {
                    "id": "file-3",
                    "filename": "运营流程知识.md",
                    "meta": {
                        "knowledge_object_id": "ops/playbook/start.md",
                        "knowledge_version_id": "test-knowledge-version",
                        "title": "运营流程知识",
                        "type": "playbook",
                        "tags": ["运营"],
                        "summary": "用于多知识库检索的知识条目",
                    },
                }
            ],
        }
        return fixtures.get(kid, fixtures["kb-eve"])

    async def fake_retrieve(kb_ids, query, k=3):
        return [{"chunk": "测试知识片段", "source": "治理测试知识.md", "score": 0.91}]

    async def fake_chat(system_prompt, user_message, model="gpt-4o", temperature=0.7, max_tokens=4096):
        return f"基于测试知识回答：{user_message}"

    monkeypatch.setattr(knowledge_platform, "health", fake_health)
    monkeypatch.setattr(knowledge_platform, "current_version_id", fake_current_version_id)
    monkeypatch.setattr(knowledge_platform, "list_knowledge_bases", fake_list_knowledge_bases)
    monkeypatch.setattr(knowledge_platform, "list_files", fake_list_files)
    monkeypatch.setattr(knowledge_platform, "retrieve", fake_retrieve)
    monkeypatch.setattr(llm_service, "chat", fake_chat)

    # 同时覆盖 lifespan 中的 Alembic 迁移（跳过）
    from app.main import app
    # 直接触发 startup 事件（pytest-asyncio 需要手动处理 lifespan）
    yield

    # 清理表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
