"""v0.5 pytest 配置：测试环境使用独立 SQLite 文件库，并替换外部依赖为确定性替身。"""
import json
import os
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ["DB_TESTING"] = "1"


@pytest_asyncio.fixture(scope="session")
def test_db_path(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("db") / "virtual_actor_test.sqlite3"


@pytest_asyncio.fixture(scope="session")
async def test_engine(test_db_path: Path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{test_db_path}", echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def setup_db(test_engine, monkeypatch):
    from app.database import Base, get_db
    from app.main import app

    # 注册全部 ORM 模型
    from app.models.role_asset import RoleAsset  # noqa: F401
    from app.models.role_version import RoleVersion, RoleVersionField  # noqa: F401
    from app.models.knowledge_ref import KnowledgeRef, ValidatedKnowledgeVersion  # noqa: F401
    from app.models.test_run import TestRunRecord  # noqa: F401
    from app.models.usage_record import UsageRecord  # noqa: F401
    from app.models.test_validation_record import TestValidationRecord  # noqa: F401
    from app.models.ops_signal import OpsSignal  # noqa: F401
    from app.models.data_asset import DataAsset  # noqa: F401
    from app.models.role_briefing import RoleBriefing  # noqa: F401
    from app.models.export_package import RoleExportPackage  # noqa: F401

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    from app.services.knowledge_platform import knowledge_platform
    from app.services.llm_service import llm_service

    monkeypatch.setattr(knowledge_platform, "default_package_id", "eve")

    async def fake_health():
        return True

    async def fake_current_version_id():
        return "test-knowledge-version"

    async def fake_list_knowledge_bases():
        return [
            {"package_id": "eve", "name": "eve AI迁移知识体系"},
        ]

    async def fake_list_files(kb_id=None, page_size=50):
        return [
            {
                "knowledge_object_id": "10-Areas/eve/test.md",
                "title": "治理测试知识",
                "tier": "P1",
                "doc_role": "master_doc",
                "evidence_type": "policy",
                "canonical_default": True,
                "use_for": ["经营复盘"],
                "not_for": [],
            },
            {
                "knowledge_object_id": "10-Areas/eve/finance/report.md",
                "title": "经营分析知识",
                "tier": "P2",
                "doc_role": "supporting_doc",
                "evidence_type": "report",
                "canonical_default": False,
                "use_for": ["经营分析"],
                "not_for": [],
            },
        ]

    async def fake_get_manifest(package_id=None):
        return {
            "package_id": "eve",
            "version_id": "test-knowledge-version",
            "documents": await fake_list_files(),
        }

    async def fake_get_tier_distribution(knowledge_refs):
        return {"P1": 1, "P2": 1}

    async def fake_retrieve(kb_ids, query, k=3, knowledge_object_ids=None):
        query_hint = "预算" if "预算" in query else "经营" if "经营" in query or "复盘" in query else "治理"
        return [
            {
                "chunk": f"{query_hint}测试知识片段：{query}",
                "source": "治理测试知识.md",
                "title": "治理测试知识",
                "score": 0.91,
                "tier": "P1",
                "doc_role": "master_doc",
                "evidence_type": "policy",
                "knowledge_object_id": "10-Areas/eve/test.md",
            }
        ]

    async def fake_chat(system_prompt, user_message, model="gpt-4o", temperature=0.7, max_tokens=4096):
        if "角色设计助手" in system_prompt:
            return json.dumps(
                {
                    "name": "经营复盘顾问",
                    "bio": "面向经营复盘与管理判断场景，输出结论、依据与建议。",
                    "tags": ["经营", "复盘"],
                    "main_duty_cluster": "围绕经营复盘任务，负责识别关键问题、解释原因，并输出建议与风险提示。",
                    "point_of_view": "优先从目标、约束、指标变化三个维度判断。",
                    "decision_style": "balanced",
                    "identity_background": "具备经营分析与跨部门协同经验。",
                    "speaking_style": "先给结论，再给依据和限制。",
                    "knowledge_boundary": "基于已绑定知识回答，暂不覆盖未授权外部事实。",
                    "output_mode": "structured",
                    "output_type": "decision_advice",
                    "output_schema": {"position": "", "key_reasons": [], "major_risks": [], "suggested_actions": [], "references": []},
                    "category": "职能助手",
                    "business_domain": "经营管理",
                    "applicable_scenarios": ["经营复盘", "管理层判断"],
                    "usage_notes": "请提供经营背景、关键指标和目标。",
                    "support_basis_summary": "基于角色定义、知识状态和测试结果形成说明。",
                },
                ensure_ascii=False,
            )

        if "推荐裁决器" in system_prompt:
            payload = json.loads(user_message)
            intent = payload["intent"]
            if "火星" in intent:
                return json.dumps({"is_out_of_scope": True, "role_judgments": []}, ensure_ascii=False)
            judgments = []
            for item in payload["candidates"]:
                matched_signals = set(item.get("matched_signals") or [])
                match = bool({"business_domain", "domain", "scenario", "role_text"} & matched_signals) and float(item.get("recall_score") or 0) >= 0.5
                judgments.append(
                    {
                        "role_id": item["role_id"],
                        "match": match,
                        "score": 0.82 if match else 0.18,
                        "reason_summary": f"该角色更贴近“{intent}”所描述的业务任务。"
                    }
                )
            return json.dumps({"is_out_of_scope": False, "role_judgments": judgments}, ensure_ascii=False)

        if "结构化提取器" in system_prompt:
            output_type = "decision_advice"
            for candidate in ("decision_advice", "risk_analysis", "policy_explanation", "review_findings"):
                if candidate in system_prompt:
                    output_type = candidate
                    break
            if output_type == "risk_analysis":
                structured = {
                    "key_findings": ["已识别输入前提和关键风险。"],
                    "risk_items": [{"item": "资料仍不完整", "severity": "medium", "impact": "影响可信度", "mitigation": "补充上下文"}],
                    "overall_risk_level": "medium",
                    "impact_scope": "影响本次业务判断",
                    "suggested_mitigations": ["补充资料", "人工复核"],
                    "references": [{"source": "治理测试知识.md", "type": "knowledge"}],
                }
            elif output_type == "policy_explanation":
                structured = {
                    "applicable_clauses": [{"clause": "平台消费契约", "content": "必须如实表达边界"}],
                    "clause_explanation": "当前回答基于已绑定知识和数据能力。",
                    "allowed_actions": ["继续分析"],
                    "prohibited_actions": ["直接执行动作"],
                    "references": [{"source": "治理测试知识.md", "type": "knowledge"}],
                }
            elif output_type == "review_findings":
                structured = {
                    "issues": [{"title": "输入前提不足", "severity": "medium", "description": "当前材料不足以完成正式审查。", "suggestion": "补充资料后复核。"}],
                    "overall_severity": "medium",
                    "references": [{"source": "治理测试知识.md", "type": "knowledge"}],
                }
            else:
                structured = {
                    "position": "建议继续推进，但需补充关键前提",
                    "key_reasons": ["已结合当前知识与数据依据。"],
                    "major_risks": [{"risk": "上下文仍不完整", "level": "medium", "mitigation": "补充目标与约束"}],
                    "suggested_actions": ["确认业务目标", "补充缺失资料"],
                    "references": [{"source": "治理测试知识.md", "type": "knowledge"}],
                }
            return json.dumps(structured, ensure_ascii=False)

        question_line = user_message.splitlines()[0]
        return "这是基于角色配置、知识与数据能力生成的测试回答。"

    monkeypatch.setattr(knowledge_platform, "health", fake_health)
    monkeypatch.setattr(knowledge_platform, "current_version_id", fake_current_version_id)
    monkeypatch.setattr(knowledge_platform, "list_knowledge_bases", fake_list_knowledge_bases)
    monkeypatch.setattr(knowledge_platform, "list_files", fake_list_files)
    monkeypatch.setattr(knowledge_platform, "get_manifest", fake_get_manifest)
    monkeypatch.setattr(knowledge_platform, "get_tier_distribution", fake_get_tier_distribution)
    monkeypatch.setattr(knowledge_platform, "retrieve", fake_retrieve)
    monkeypatch.setattr(llm_service, "chat", fake_chat)

    yield

    app.dependency_overrides.clear()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login = await ac.post("/auth/login", json={"username": "admin", "password": "admin123"})
        assert login.status_code == 200
        ac.headers.update({"Authorization": f"Bearer {login.json()['access_token']}"})
        yield ac
