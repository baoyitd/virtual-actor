#!/usr/bin/env python3
"""启动 v0.5 浏览器烟测专用运行态。

特性：
1. 使用独立 SQLite 文件库，避免依赖本地 MySQL / Docker。
2. 替换知识平台与 LLM 为确定性替身，保证烟测可重复。
3. 复用正式 FastAPI + React 入口，便于 Playwright 直接走真实页面。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

ROOT = Path(__file__).resolve().parents[1]
TMP_DIR = ROOT / "tmp"
DEFAULT_DB_PATH = TMP_DIR / "v05-smoke.sqlite3"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ["DB_TESTING"] = "1"

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


def register_models() -> None:
    """确保 SQLite 建表时已经加载全部 ORM 模型。"""

    from app.models.data_asset import DataAsset  # noqa: F401
    from app.models.export_package import RoleExportPackage  # noqa: F401
    from app.models.knowledge_ref import KnowledgeRef, ValidatedKnowledgeVersion  # noqa: F401
    from app.models.ops_signal import OpsSignal  # noqa: F401
    from app.models.role_asset import RoleAsset  # noqa: F401
    from app.models.role_briefing import RoleBriefing  # noqa: F401
    from app.models.role_version import RoleVersion, RoleVersionField  # noqa: F401
    from app.models.test_run import TestRunRecord  # noqa: F401
    from app.models.test_validation_record import TestValidationRecord  # noqa: F401
    from app.models.usage_record import UsageRecord  # noqa: F401


def patch_external_services() -> None:
    from app.services.knowledge_platform import knowledge_platform
    from app.services.llm_service import llm_service

    knowledge_platform.default_package_id = "eve"

    async def fake_health() -> bool:
        return True

    async def fake_current_version_id() -> str:
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
                        "summary": "用于烟测的治理知识条目",
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
                        "summary": "用于烟测的经营分析知识条目",
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
                        "summary": "用于烟测的流程知识条目",
                    },
                }
            ],
        }
        return fixtures.get(kid, fixtures["kb-eve"])

    async def fake_retrieve(kb_ids, query, k=3):
        query_hint = "预算" if "预算" in query else "经营" if "经营" in query or "复盘" in query else "治理"
        return [
            {
                "chunk": f"{query_hint}测试知识片段：{query}",
                "source": "治理测试知识.md",
                "score": 0.91,
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
                    "output_schema": {
                        "position": "",
                        "key_reasons": [],
                        "major_risks": [],
                        "suggested_actions": [],
                        "references": [],
                    },
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
                        "reason_summary": f"该角色更贴近“{intent}”所描述的业务任务。",
                    }
                )
            return json.dumps({"is_out_of_scope": False, "role_judgments": judgments}, ensure_ascii=False)

        if "JSON 结构固定为" in system_prompt:
            structured = {
                "position": "建议继续推进，但需补充关键前提",
                "key_reasons": ["已结合当前知识与数据依据。"],
                "major_risks": [{"risk": "上下文仍不完整", "level": "medium", "mitigation": "补充目标与约束"}],
                "suggested_actions": ["确认业务目标", "补充缺失资料"],
                "references": [{"source": "治理测试知识.md", "type": "knowledge"}],
            }
            return json.dumps(
                {
                    "answer": "这是基于角色配置、知识与数据能力生成的测试回答。",
                    "structured_result": structured,
                },
                ensure_ascii=False,
            )

        question_line = user_message.splitlines()[0]
        return f"基于测试知识回答：{question_line}"

    knowledge_platform.health = fake_health
    knowledge_platform.current_version_id = fake_current_version_id
    knowledge_platform.list_knowledge_bases = fake_list_knowledge_bases
    knowledge_platform.list_files = fake_list_files
    knowledge_platform.retrieve = fake_retrieve
    llm_service.chat = fake_chat


async def configure_runtime() -> None:
    register_models()
    patch_external_services()

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    db_path = Path(os.getenv("VIRTUAL_ACTOR_SMOKE_DB", str(DEFAULT_DB_PATH))).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db


async def main() -> None:
    await configure_runtime()
    host = os.getenv("VIRTUAL_ACTOR_SMOKE_HOST", "127.0.0.1")
    port = int(os.getenv("VIRTUAL_ACTOR_SMOKE_PORT", "18080"))
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
