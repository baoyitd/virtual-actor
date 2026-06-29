"""v0.5 API 主链路测试。"""
import json
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.knowledge_ref import KnowledgeRef
from app.models.role_version import RoleVersionField
from app.config import settings
from app.services.knowledge_platform import knowledge_platform


BASE_ROLE = {
    "name": "经营分析顾问",
    "bio": "面向经营管理场景，提供分析、判断与建议。",
}

STRUCTURED_SCHEMA = {
    "position": "",
    "key_reasons": [],
    "major_risks": [],
    "suggested_actions": [],
    "references": [],
}


async def create_role(client, **overrides):
    payload = {**BASE_ROLE, **overrides}
    response = await client.post("/role-assets", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


async def create_data_asset(client, table_name="fact_project_budget", **overrides):
    payload = {
        "display_name": "项目预算事实表",
        "datasource_ref": "warehouse.main",
        "database_name": "dw",
        "table_name": table_name,
        "scope_summary": "可读取预算执行与偏差数据，不包含未授权明细。",
        **overrides,
    }
    response = await client.post("/data-assets", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


async def save_briefing(client, role_id, **overrides):
    response = await client.patch(
        f"/role-assets/{role_id}/briefing",
        json={
            "applicable_scenarios": ["经营复盘", "预算偏差分析"],
            "usage_notes": "请提供任务背景、关键指标、目标对象和约束，再调用该角色。",
            "support_basis_summary": "基于角色定义、已绑定知识 / 数据状态与测试记录形成可信说明。",
            **overrides,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


async def confirm_briefing_current(client, role_id):
    response = await client.patch(
        f"/role-assets/{role_id}/briefing",
        json={"confirm_current": True},
    )
    assert response.status_code == 200, response.text
    return response.json()


async def enter_test_stage(client, role_id, **overrides):
    return await save_briefing(client, role_id, **overrides)


async def run_test_consume(client, role_id, **overrides):
    payload = {"query": "请基于当前信息给出经营判断。", **overrides}
    response = await client.post(f"/role-assets/{role_id}/test-consume", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


async def prepare_publishable_role(
    client,
    *,
    structured=True,
    with_knowledge=True,
    with_data=False,
    briefing_overrides=None,
    **role_overrides,
):
    asset_ids = []
    if with_data:
        asset = await create_data_asset(client)
        asset_ids = [asset["id"]]

    role = await create_role(
        client,
        **{
            "owner": "strategy-owner",
            "business_domain": "经营管理",
            "category": "职能助手",
            "main_duty_cluster": "围绕经营复盘与投资前置分析，负责识别关键问题、解释原因，并输出建议与风险提示。",
            "point_of_view": "优先从目标、约束和关键指标变化看问题。",
            "output_mode": "structured" if structured else "freeform",
            "output_type": "decision_advice" if structured else None,
            "output_schema": STRUCTURED_SCHEMA if structured else None,
            "data_asset_binding_ids": asset_ids,
            **role_overrides,
        },
    )
    role_id = role["role_id"]

    if with_knowledge:
        bind = await client.post(
            f"/role-assets/{role_id}/knowledge",
            json={"knowledge_object_id": "10-Areas/eve/test.md", "title": "治理测试知识"},
        )
        assert bind.status_code == 201, bind.text

    await enter_test_stage(client, role_id, **(briefing_overrides or {}))
    query = "请基于预算和经营制度给出判断。" if with_knowledge else "请给出当前业务判断。"
    await run_test_consume(client, role_id, query=query)
    await confirm_briefing_current(client, role_id)
    publish = await client.post(f"/role-assets/{role_id}/publish")
    assert publish.status_code == 200, publish.text
    return publish.json()


@pytest.mark.asyncio
async def test_v05_create_role_defaults_to_freeform_and_workspace(client):
    created = await create_role(client)
    assert created["status"] == "draft"
    assert created["output_mode"] == "freeform"
    assert created["briefing"]["status"] == "missing"

    workspace = await client.get(f"/role-assets/{created['role_id']}/workspace")
    assert workspace.status_code == 200
    assert workspace.json()["role_version_id"] == created["role_version_id"]
    assert any(item["key"] == "l1" for item in workspace.json()["definition_progress"])


@pytest.mark.asyncio
async def test_v05_ai_draft_returns_structured_draft_without_persisting(client):
    before = await client.get("/role-assets")
    draft = await client.post("/role-assets/ai-draft", json={"description": "我要一个能做经营复盘和预算判断的角色"})
    after = await client.get("/role-assets")
    assert draft.status_code == 200
    payload = draft.json()
    assert payload["name"] == "经营复盘顾问"
    assert payload["output_mode"] == "structured"
    assert payload["output_type"] == "decision_advice"
    assert len(after.json()) == len(before.json())


@pytest.mark.asyncio
async def test_v05_data_asset_crud_and_binding_roundtrip(client):
    asset = await create_data_asset(client, freshness="T+1", owner_team="经营数据中台")
    updated = await client.patch(f"/data-assets/{asset['id']}", json={"status": "inactive"})
    assert updated.status_code == 200
    filtered = await client.get("/data-assets?status=inactive")
    assert filtered.status_code == 200
    assert filtered.json()[0]["id"] == asset["id"]

    role = await create_role(
        client,
        owner="ops-owner",
        main_duty_cluster="负责解释预算偏差并给出建议。",
        data_asset_binding_ids=[asset["id"]],
    )
    assert role["data_asset_bindings"][0]["id"] == asset["id"]
    assert role["briefing"]["data_capability_status"]["state"] == "bound"


@pytest.mark.asyncio
async def test_v05_knowledge_catalog_and_bind_roundtrip(client):
    bases = await client.get("/knowledge/bases")
    catalog = await client.get("/knowledge/catalog?kb_id=master")
    assert bases.status_code == 200
    assert catalog.status_code == 200
    assert bases.json()[0]["kb_id"] == "eve"
    assert bases.json()[0]["name"] == "eve AI迁移知识体系"
    assert catalog.json()[0]["knowledge_object_id"] == "10-Areas/eve/test.md"

    role = await create_role(client, owner="role-owner", main_duty_cluster="负责解释制度与依据。")
    bind = await client.post(
        f"/role-assets/{role['role_id']}/knowledge",
        json={"kb_id": "eve", "knowledge_object_id": "10-Areas/eve/test.md", "title": "治理测试知识"},
    )
    assert bind.status_code == 201
    detail = await client.get(f"/role-assets/{role['role_id']}")
    assert detail.json()["knowledge_refs"][0]["knowledge_version_id"] == "test-knowledge-version"


@pytest.mark.asyncio
async def test_v05_create_role_with_knowledge_bindings_persists_refs(client):
    created = await create_role(
        client,
        knowledge_bindings=[
            {
                "kb_id": "eve",
                "knowledge_object_id": "10-Areas/eve/test.md",
                "title": "治理测试知识",
                "type": "policy",
            }
        ],
        knowledge_boundary="基于已绑定知识回答，暂不覆盖外部未授权事实。",
    )
    assert created["knowledge_boundary"] == "基于已绑定知识回答，暂不覆盖外部未授权事实。"
    assert len(created["knowledge_refs"]) == 1
    assert created["knowledge_refs"][0]["knowledge_object_id"] == "10-Areas/eve/test.md"
    assert created["knowledge_refs"][0]["knowledge_version_id"] == "test-knowledge-version"


@pytest.mark.asyncio
async def test_v05_update_role_with_knowledge_bindings_replaces_current_refs(client):
    created = await create_role(
        client,
        knowledge_bindings=[
            {
                "kb_id": "eve",
                "knowledge_object_id": "10-Areas/eve/test.md",
                "title": "治理测试知识",
            }
        ],
        knowledge_boundary="基于治理制度回答。",
    )

    updated = await client.patch(
        f"/role-assets/{created['role_id']}",
        json={
            "knowledge_bindings": [
                {
                    "kb_id": "eve",
                    "knowledge_object_id": "10-Areas/eve/finance/report.md",
                    "title": "经营分析知识",
                    "type": "report",
                }
            ],
            "knowledge_boundary": "基于经营分析知识回答。",
        },
    )
    assert updated.status_code == 200, updated.text
    payload = updated.json()
    assert payload["knowledge_boundary"] == "基于经营分析知识回答。"
    assert [item["knowledge_object_id"] for item in payload["knowledge_refs"]] == ["10-Areas/eve/finance/report.md"]
    assert payload["knowledge_refs"][0]["knowledge_version_id"] == "test-knowledge-version"


@pytest.mark.asyncio
async def test_v05_create_role_without_knowledge_bindings_forces_boundary_to_null(client):
    created = await create_role(
        client,
        knowledge_boundary="即使暂未绑定知识，也先写一段边界说明。",
    )
    assert created["knowledge_refs"] == []
    assert created["knowledge_boundary"] is None


@pytest.mark.asyncio
async def test_v05_update_role_with_empty_knowledge_bindings_clears_boundary(client):
    created = await create_role(
        client,
        knowledge_bindings=[
            {
                "kb_id": "eve",
                "knowledge_object_id": "10-Areas/eve/test.md",
                "title": "治理测试知识",
            }
        ],
        knowledge_boundary="基于治理制度回答。",
    )

    updated = await client.patch(
        f"/role-assets/{created['role_id']}",
        json={
            "knowledge_bindings": [],
            "knowledge_boundary": "这段说明应在保存时被清空。",
        },
    )
    assert updated.status_code == 200, updated.text
    payload = updated.json()
    assert payload["knowledge_refs"] == []
    assert payload["knowledge_boundary"] is None


@pytest.mark.asyncio
async def test_v05_create_role_with_knowledge_bindings_fails_atomically_when_platform_unavailable(client, monkeypatch):
    before = await client.get("/role-assets")

    async def fake_health():
        return False

    monkeypatch.setattr(knowledge_platform, "health", fake_health)

    response = await client.post(
        "/role-assets",
        json={
            **BASE_ROLE,
            "knowledge_bindings": [
                {
                    "kb_id": "eve",
                    "knowledge_object_id": "10-Areas/eve/test.md",
                    "title": "治理测试知识",
                }
            ],
        },
    )
    assert response.status_code == 503

    after = await client.get("/role-assets")
    assert len(after.json()) == len(before.json())


@pytest.mark.asyncio
async def test_v05_update_role_with_knowledge_bindings_fails_atomically_when_platform_unavailable(client, monkeypatch):
    created = await create_role(client)

    async def fake_health():
        return False

    monkeypatch.setattr(knowledge_platform, "health", fake_health)

    response = await client.patch(
        f"/role-assets/{created['role_id']}",
        json={
            "name": "失败时不应写入的新名字",
            "knowledge_bindings": [
                {
                    "kb_id": "eve",
                    "knowledge_object_id": "10-Areas/eve/test.md",
                    "title": "治理测试知识",
                }
            ],
        },
    )
    assert response.status_code == 503

    detail = await client.get(f"/role-assets/{created['role_id']}")
    assert detail.status_code == 200
    assert detail.json()["name"] == BASE_ROLE["name"]
    assert detail.json()["knowledge_refs"] == []


@pytest.mark.asyncio
async def test_v05_existing_legacy_resource_binding_migrates_by_path(client, test_engine):
    role = await create_role(client, owner="role-owner", main_duty_cluster="负责解释快消行业知识。")
    session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        session.add(
            KnowledgeRef(
                role_id=role["role_id"],
                version_id=role["role_version_id"],
                kb_id="legacy-resource-id",
                knowledge_object_id="30-Resources/快消品行业知识/44-消费者行为与FMOT.md",
                knowledge_version_id="test-knowledge-version",
                title="消费者行为与FMOT",
                type="note",
                knowledge_source="knowledge-platform",
                bound_at=datetime.now(timezone.utc),
            )
        )
        await session.commit()

    detail = await client.get(f"/role-assets/{role['role_id']}")
    assert detail.status_code == 200
    assert detail.json()["knowledge_refs"][0]["kb_id"] == "eve"


@pytest.mark.asyncio
async def test_v05_briefing_lifecycle_turns_stale_after_source_change(client):
    role = await create_role(
        client,
        owner="role-owner",
        main_duty_cluster="围绕经营复盘任务，输出判断与建议。",
    )
    role_id = role["role_id"]

    saved = await save_briefing(client, role_id)
    assert saved["briefing"]["status"] == "fresh"

    updated = await client.patch(f"/role-assets/{role_id}", json={"main_duty_cluster": "围绕经营复盘和预算偏差任务，输出判断与建议。"})
    assert updated.status_code == 200
    assert updated.json()["briefing"]["status"] == "stale"

    refreshed = await client.patch(f"/role-assets/{role_id}/briefing", json={"confirm_current": True})
    assert refreshed.status_code == 200
    assert refreshed.json()["briefing"]["status"] == "fresh"


@pytest.mark.asyncio
async def test_v05_save_briefing_promotes_to_test_without_owner_but_requires_main_duty_cluster(client):
    role = await create_role(client)
    blocked = await client.patch(
        f"/role-assets/{role['role_id']}/briefing",
        json={
            "applicable_scenarios": ["经营复盘"],
            "usage_notes": "请补充背景与关键约束。",
            "support_basis_summary": "基于角色定义和当前运行状态生成。",
        },
    )
    assert blocked.status_code == 400
    assert "核心职责" in blocked.json()["detail"]

    ready = await client.patch(
        f"/role-assets/{role['role_id']}",
        json={"main_duty_cluster": "负责输出业务判断和建议。"},
    )
    assert ready.status_code == 200
    moved = await save_briefing(client, role["role_id"])
    assert moved["status"] == "test"
    assert moved["owner"] == ""


@pytest.mark.asyncio
async def test_v05_publish_requires_governance_briefing_and_validation(client):
    role = await create_role(
        client,
        owner="role-owner",
        main_duty_cluster="负责输出业务判断和建议。",
    )
    blocked = await client.post(f"/role-assets/{role['role_id']}/publish")
    assert blocked.status_code == 400
    assert "业务域" in blocked.json()["detail"]


@pytest.mark.asyncio
async def test_v05_test_consume_requires_test_status(client):
    role = await create_role(
        client,
        owner="role-owner",
        main_duty_cluster="负责输出业务判断和建议。",
    )
    response = await client.post(
        f"/role-assets/{role['role_id']}/test-consume",
        json={"query": "请给出判断。"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_v05_test_consume_records_validation_and_freeform_answer(client):
    role = await create_role(
        client,
        owner="role-owner",
        main_duty_cluster="负责输出业务判断和建议。",
    )
    await enter_test_stage(client, role["role_id"])
    result = await run_test_consume(client, role["role_id"], query="请给出当前业务判断。")
    assert result["validation_record_id"]
    assert result["status"] == "success"
    assert result["answer"].startswith("这是基于角色配置")


@pytest.mark.asyncio
async def test_v05_test_validation_history_returns_latest_first_for_current_version(client):
    role = await create_role(
        client,
        owner="role-owner",
        main_duty_cluster="负责输出业务判断和建议。",
    )
    await enter_test_stage(client, role["role_id"])
    first = await run_test_consume(client, role["role_id"], query="第一次测试问题")
    second = await run_test_consume(client, role["role_id"], query="第二次测试问题")

    response = await client.get(
        f"/role-assets/{role['role_id']}/test-validations",
        params={"version_id": role["role_version_id"]},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(payload) >= 2
    assert payload[0]["validation_record_id"] == second["validation_record_id"]
    assert payload[0]["query"] == "第二次测试问题"
    assert payload[0]["role_version_id"] == role["role_version_id"]
    assert payload[1]["validation_record_id"] == first["validation_record_id"]


@pytest.mark.asyncio
async def test_v05_grounding_query_without_knowledge_returns_insufficient_knowledge(client):
    role = await create_role(
        client,
        owner="role-owner",
        main_duty_cluster="负责解释制度与依据。",
    )
    await enter_test_stage(client, role["role_id"])
    response = await client.post(
        f"/role-assets/{role['role_id']}/test-consume",
        json={"query": "请根据制度依据解释当前要求。"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "insufficient_knowledge"


@pytest.mark.asyncio
async def test_v05_knowledge_binding_affects_runtime_and_boundary(client):
    role = await create_role(
        client,
        owner="role-owner",
        main_duty_cluster="负责解释制度与依据。",
        knowledge_bindings=[
            {
                "kb_id": "eve",
                "knowledge_object_id": "10-Areas/eve/test.md",
                "title": "治理测试知识",
            }
        ],
        knowledge_boundary="基于集团制度回答，暂不覆盖税务筹划。",
    )
    await enter_test_stage(client, role["role_id"])

    success = await client.post(
        f"/role-assets/{role['role_id']}/test-consume",
        json={"query": "请根据经营制度解释当前要求。"},
    )
    assert success.status_code == 200
    assert success.json()["sources"][0]["type"] == "knowledge"

    blocked = await client.post(
        f"/role-assets/{role['role_id']}/test-consume",
        json={"query": "请根据税务筹划要求给出建议。"},
    )
    assert blocked.status_code == 200
    assert blocked.json()["status"] == "boundary_blocked"


@pytest.mark.asyncio
async def test_v05_knowledge_retrieval_failure_returns_system_failed_instead_of_fake_success(client, monkeypatch):
    role = await create_role(
        client,
        owner="role-owner",
        main_duty_cluster="负责解释快消行业分析知识。",
        knowledge_bindings=[
            {
                "kb_id": "eve",
                "knowledge_object_id": "30-Resources/快消品行业知识/44-消费者行为与FMOT.md",
                "title": "消费者行为与FMOT",
            }
        ],
    )
    await enter_test_stage(client, role["role_id"])

    async def fake_retrieve(kb_ids, query, k=3):
        raise RuntimeError("401 Unauthorized")

    monkeypatch.setattr(knowledge_platform, "retrieve", fake_retrieve)

    response = await client.post(
        f"/role-assets/{role['role_id']}/test-consume",
        json={"query": "当我有一个新产品计划进入市场的时候，应该如何评估销售可行性和利润可行性呢"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "system_failed"
    assert payload["sources"] == []
    assert "知识检索" in payload["answer"] or "知识平台认证" in payload["answer"]


@pytest.mark.asyncio
async def test_v05_data_assets_affect_runtime_observations(client):
    asset = await create_data_asset(client, table_name="fact_project_budget")
    role = await create_role(
        client,
        owner="role-owner",
        main_duty_cluster="负责解释预算偏差并给出建议。",
        data_asset_binding_ids=[asset["id"]],
    )
    await enter_test_stage(client, role["role_id"])
    result = await client.post(
        f"/role-assets/{role['role_id']}/test-consume",
        json={"query": "请分析本月预算偏差。"},
    )
    assert result.status_code == 200
    assert any(source["type"] == "data" for source in result.json()["sources"])
    assert any("预算" in source.get("source", "") for source in result.json()["sources"] if source["type"] == "data")


@pytest.mark.asyncio
async def test_v05_structured_output_contract_returns_structured_result(client):
    role = await create_role(
        client,
        owner="role-owner",
        main_duty_cluster="围绕经营复盘任务输出决策建议。",
        output_mode="structured",
        output_type="decision_advice",
        output_schema=STRUCTURED_SCHEMA,
    )
    await enter_test_stage(client, role["role_id"])
    result = await client.post(
        f"/role-assets/{role['role_id']}/test-consume",
        json={"query": "请给出经营判断。"},
    )
    assert result.status_code == 200
    payload = result.json()
    assert payload["output_type"] == "decision_advice"
    assert payload["structured_result"]["position"]
    assert payload["structured_result"]["references"]


@pytest.mark.asyncio
async def test_v05_default_model_binding_sentinel_resolves_to_system_model(client, monkeypatch):
    role = await create_role(
        client,
        owner="role-owner",
        main_duty_cluster="围绕经营复盘任务输出决策建议。",
        output_mode="structured",
        output_type="decision_advice",
        output_schema=STRUCTURED_SCHEMA,
        model_binding={
            "model_provider": "system",
            "model_name": "default",
            "temperature": 0.4,
            "max_tokens": 2048,
            "fallback_enabled": False,
            "inherited": False,
        },
    )
    await enter_test_stage(client, role["role_id"])

    from app.services.consume_service import llm_service

    captured: dict[str, object] = {}

    async def fake_chat(system_prompt, user_message, model="gpt-4o", temperature=0.7, max_tokens=4096):
        if "结构化提取器" not in system_prompt:
            captured["model"] = model
            captured["temperature"] = temperature
            captured["max_tokens"] = max_tokens
        if "结构化提取器" in system_prompt:
            return json.dumps(
                {
                    "position": "建议推进",
                    "key_reasons": ["模型绑定已正确解析。"],
                    "major_risks": [],
                    "suggested_actions": ["继续验证"],
                    "references": [{"source": "治理测试知识.md", "type": "knowledge"}],
                },
                ensure_ascii=False,
            )
        return "基于模型生成的结构化回答。"

    monkeypatch.setattr(llm_service, "chat", fake_chat)

    response = await client.post(
        f"/role-assets/{role['role_id']}/test-consume",
        json={"query": "请给出经营判断。"},
    )
    assert response.status_code == 200, response.text
    assert captured["model"] == settings.AI_CREATE_MODEL
    assert captured["temperature"] == 0.4
    assert captured["max_tokens"] == 2048


@pytest.mark.asyncio
async def test_v05_model_binding_storage_omits_sentinel_and_role_provider_override(client, test_engine):
    created = await create_role(
        client,
        owner="role-owner",
        main_duty_cluster="围绕经营复盘任务输出决策建议。",
        model_binding={
            "model_provider": "openai",
            "model_name": "default",
            "temperature": 0.5,
            "max_tokens": 3072,
            "fallback_enabled": True,
            "inherited": False,
        },
    )
    assert created["model_binding"]["model_provider"] == settings.LLM_PROVIDER
    assert created["model_binding"]["model_name"] == settings.AI_CREATE_MODEL
    assert created["model_binding"]["inherited"] is True

    session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        stored = (
            await session.execute(
                select(RoleVersionField).where(
                    RoleVersionField.version_id == created["role_version_id"],
                    RoleVersionField.field_name == "model_binding",
                )
            )
        )
        record = stored.scalar_one()
        payload = record.field_value
        assert payload["inherited"] is True
        assert payload["temperature"] == 0.5
        assert payload["max_tokens"] == 3072
        assert payload["fallback_enabled"] is True
        assert "model_name" not in payload
        assert "model_provider" not in payload


@pytest.mark.asyncio
async def test_v05_publishable_role_can_publish_and_generate_export_package(client):
    published = await prepare_publishable_role(client, structured=True, with_knowledge=True, with_data=True)
    package = await client.post(f"/role-assets/{published['role_id']}/export-packages/tool")
    assert package.status_code == 200, package.text
    files = {item["path"]: item["content"] for item in package.json()["files"]}
    for required in (
        "package-manifest.json",
        "role-brief.md",
        "consume-contract.json",
        "output-contract.json",
        "writeback-policy.md",
        "tool-manifest.json",
        "dify-openapi.json",
        "dify-provider-template.json",
    ):
        assert required in files
    assert "使用说明" in files["role-brief.md"]
    assert "current-effective-config" in files["package-manifest.json"]

    dify_openapi = json.loads(files["dify-openapi.json"])
    post_spec = dify_openapi["paths"][f"/role-assets/{published['role_id']}/consume"]["post"]
    request_props = post_spec["requestBody"]["content"]["application/json"]["schema"]["properties"]
    assert dify_openapi["servers"][0]["url"] == "{{VIRTUAL_ACTOR_BASE_URL}}"
    assert post_spec["operationId"] == "consumePublishedRole"
    assert post_spec["requestBody"]["content"]["application/json"]["schema"]["required"] == ["query"]
    assert request_props["caller_type"]["default"] == "external_tool"
    assert request_props["role_version_id"]["default"] == published["published_version_id"]
    assert request_props["role_version_id"]["enum"] == [published["published_version_id"]]

    dify_provider_template = json.loads(files["dify-provider-template.json"])
    nested_schema = json.loads(dify_provider_template["schema"])
    assert dify_provider_template["provider"] == (
        f"virtual_actor_role_{published['role_id'][:8]}_{published['published_version_id'][:8]}"
    )
    assert dify_provider_template["credentials"]["api_key_header"] == "Authorization"
    assert dify_provider_template["credentials"]["api_key_value"] == "Bearer {{VIRTUAL_ACTOR_TOKEN}}"
    assert dify_provider_template["metadata"]["role_version_id"] == published["published_version_id"]
    assert nested_schema["servers"][0]["url"] == "{{VIRTUAL_ACTOR_BASE_URL}}"


@pytest.mark.asyncio
async def test_v05_skill_export_package_emits_valid_codex_skill_markdown(client):
    published = await prepare_publishable_role(
        client,
        structured=False,
        with_knowledge=True,
        name="经营分析顾问: 投资复盘",
    )
    role_id = published["role_id"]

    package = await client.post(f"/role-assets/{role_id}/export-packages/skill")
    assert package.status_code == 200, package.text
    files = {item["path"]: item["content"] for item in package.json()["files"]}

    for required in (
        "package-manifest.json",
        "role-brief.md",
        "consume-contract.json",
        "output-contract.json",
        "writeback-policy.md",
        "SKILL.md",
    ):
        assert required in files

    consume_contract = json.loads(files["consume-contract.json"])
    assert consume_contract["auth"]["env"] == "VIRTUAL_ACTOR_TOKEN"
    assert consume_contract["input_boundary"]["required_fields"]["query"]
    assert consume_contract["input_boundary"]["fixed_fields"]["caller_type"] == "external_skill"
    assert consume_contract["input_boundary"]["example_body"]["query"] == "<end-user request>"
    assert "usage_record_id" in consume_contract["output_boundary"]["success_body_fields"]

    skill_markdown = files["SKILL.md"]
    assert skill_markdown.startswith("---\nname: \"virtual-actor-role-")
    assert 'description: "Use when the user asks to use the exported 经营分析顾问: 投资复盘 role.' in skill_markdown
    assert "## Required Files" in skill_markdown
    assert "## Required Environment" in skill_markdown
    assert "## Execution Rules" in skill_markdown
    assert "Read the sibling contract files before responding." in skill_markdown
    assert "Build the JSON request body from `consume-contract.json`" in skill_markdown
    assert f"- role_id: `{role_id}`" in skill_markdown
    assert f"- role_version_id: `{published['published_version_id']}`" in skill_markdown


@pytest.mark.asyncio
async def test_v05_external_consume_creates_usage_record_with_version_and_status(client):
    published = await prepare_publishable_role(client, structured=False, with_knowledge=True)
    response = await client.post(
        f"/role-assets/{published['role_id']}/consume",
        json={
            "query": "请根据经营制度给出判断。",
            "caller_type": "external_tool",
            "caller_id": "simulated-dify-tool",
            "role_version_id": published["published_version_id"],
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["usage_record_id"]
    assert payload["role_version_id"] == published["published_version_id"]

    records = await client.get(f"/role-assets/{published['role_id']}/consume-records")
    assert records.status_code == 200
    assert records.json()[0]["caller_type"] == "external_tool"


@pytest.mark.asyncio
async def test_v05_marketplace_list_and_recommend(client):
    published = await prepare_publishable_role(client, structured=True, with_knowledge=False)
    listing = await client.get("/marketplace")
    assert listing.status_code == 200
    assert listing.json()[0]["role_id"] == published["role_id"]

    recommend = await client.post(
        "/marketplace/recommend",
        json={"intent": "我需要一个帮经营管理层做预算偏差复盘的角色"},
    )
    assert recommend.status_code == 200
    payload = recommend.json()
    assert payload["matched"] is True
    assert payload["recommendations"][0]["role_id"] == published["role_id"]
    assert payload["recommendations"][0]["reason_summary"]
    assert payload["recommendations"][0]["reason_evidence"]
    assert "适用场景" in "".join(payload["recommendations"][0]["reason_evidence"])


@pytest.mark.asyncio
async def test_v05_marketplace_business_intent_without_matching_role_returns_no_match(client):
    await prepare_publishable_role(client, structured=True, with_knowledge=False)

    recommend = await client.post(
        "/marketplace/recommend",
        json={"intent": "我需要一个数据治理的专家，帮我做数据架构"},
    )
    assert recommend.status_code == 200
    payload = recommend.json()
    assert payload["matched"] is False
    assert payload["result_type"] == "no_match"
    assert payload["recommendations"] == []
    assert "数据治理 / 数据架构" in payload["unmatched_intent_summary"]


@pytest.mark.asyncio
async def test_v05_marketplace_investment_intent_matches_investment_role(client):
    published = await prepare_publishable_role(
        client,
        structured=True,
        with_knowledge=False,
        name="投资决策顾问",
        bio="为企业投资项目提供投前评估、收益测算和决策建议。",
        tags=["投资", "投前", "项目评估"],
        business_domain="投资管理",
        main_duty_cluster="围绕项目投资评估和投决支持，负责识别收益、风险与关键假设，并输出决策建议。",
        briefing_overrides={
            "applicable_scenarios": ["投资项目评估", "投前决策支持"],
            "usage_notes": "请提供项目背景、投资目标、关键假设和现有测算资料。",
            "support_basis_summary": "基于角色定义、投资类适用场景与测试记录形成可信说明。",
        },
    )

    recommend = await client.post(
        "/marketplace/recommend",
        json={"intent": "我有一些投资项目，需要一些角色来帮我"},
    )
    assert recommend.status_code == 200
    payload = recommend.json()
    assert payload["matched"] is True
    assert payload["recommendations"][0]["role_id"] == published["role_id"]
    assert "投资项目" in payload["recommendations"][0]["reason_summary"]
    assert any("业务域：投资管理" in item for item in payload["recommendations"][0]["reason_evidence"])


@pytest.mark.asyncio
async def test_v05_marketplace_strong_direct_match_survives_llm_false_negative(client, monkeypatch):
    published = await prepare_publishable_role(
        client,
        structured=True,
        with_knowledge=False,
        name="投资决策顾问",
        bio="为企业投资项目提供投前评估、收益测算和决策建议。",
        business_domain="投资管理",
        main_duty_cluster="围绕项目投资评估和投决支持，负责识别收益、风险与关键假设，并输出决策建议。",
        briefing_overrides={
            "applicable_scenarios": ["投资项目评估", "投前决策支持"],
            "usage_notes": "请提供项目背景、投资目标、关键假设和现有测算资料。",
            "support_basis_summary": "基于角色定义、投资类适用场景与测试记录形成可信说明。",
        },
    )

    from app.services.recommend_service import llm_service

    async def fake_chat(**kwargs):
        return json.dumps(
            {
                "is_out_of_scope": False,
                "role_judgments": [
                    {
                        "role_id": published["role_id"],
                        "match": False,
                        "score": 0.12,
                        "reason_summary": "误判为不匹配。",
                    }
                ],
            },
            ensure_ascii=False,
        )

    monkeypatch.setattr(llm_service, "chat", fake_chat)

    recommend = await client.post(
        "/marketplace/recommend",
        json={"intent": "我有一些投资项目，需要一些角色来帮我"},
    )
    assert recommend.status_code == 200
    payload = recommend.json()
    assert payload["matched"] is True
    assert payload["recommendations"][0]["role_id"] == published["role_id"]
    assert payload["recommendations"][0]["match_score"] >= 1.0


@pytest.mark.asyncio
async def test_v05_marketplace_out_of_scope_request_is_rejected(client):
    recommend = await client.post(
        "/marketplace/recommend",
        json={"intent": "火星殖民地税务筹划和跨星际报关审查"},
    )
    assert recommend.status_code == 200
    assert recommend.json()["result_type"] == "out_of_scope"


@pytest.mark.asyncio
async def test_v05_editing_published_role_creates_new_draft_version(client):
    published = await prepare_publishable_role(client, structured=False, with_knowledge=True)
    published_version_id = published["published_version_id"]

    updated = await client.patch(
        f"/role-assets/{published['role_id']}",
        json={"point_of_view": "优先从目标、约束和经营指标变化判断。"},
    )
    assert updated.status_code == 200
    payload = updated.json()
    assert payload["status"] == "draft"
    assert payload["role_version_id"] != published_version_id
    assert payload["published_version_id"] == published_version_id


@pytest.mark.asyncio
async def test_v05_formal_consume_and_export_keep_using_last_published_version_while_new_draft_exists(client):
    published = await prepare_publishable_role(client, structured=False, with_knowledge=True)
    role_id = published["role_id"]
    published_version_id = published["published_version_id"]

    updated = await client.patch(
        f"/role-assets/{role_id}",
        json={"point_of_view": "优先从目标、约束和经营指标变化判断。"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "draft"

    consume = await client.post(
        f"/role-assets/{role_id}/consume",
        json={"query": "请给出经营判断。"},
    )
    assert consume.status_code == 200, consume.text
    assert consume.json()["role_version_id"] == published_version_id

    package = await client.post(f"/role-assets/{role_id}/export-packages/skill")
    assert package.status_code == 200, package.text
    assert package.json()["role_version_id"] == published_version_id


@pytest.mark.asyncio
async def test_v05_editing_archived_role_creates_new_draft_version(client):
    published = await prepare_publishable_role(client, structured=False, with_knowledge=True)
    role_id = published["role_id"]

    archived = await client.post(f"/role-assets/{role_id}/archive")
    assert archived.status_code == 200, archived.text
    archived_payload = archived.json()
    assert archived_payload["status"] == "archived"

    updated = await client.patch(
        f"/role-assets/{role_id}",
        json={"point_of_view": "重新启用后优先从目标和约束判断。"},
    )
    assert updated.status_code == 200, updated.text
    payload = updated.json()
    assert payload["status"] == "draft"
    assert payload["role_version_id"] != archived_payload["role_version_id"]


@pytest.mark.asyncio
async def test_v05_export_package_works_after_governance_only_change(client):
    """治理字段变更（如 business_domain）不再导致说明卡 stale，不影响已发布版本外供"""
    published = await prepare_publishable_role(client, structured=True, with_knowledge=True)
    role_id = published["role_id"]

    updated = await client.patch(
        f"/role-assets/{role_id}",
        json={"business_domain": "战略经营"},
    )
    assert updated.status_code == 200

    package = await client.post(f"/role-assets/{role_id}/export-packages/skill")
    assert package.status_code == 200


@pytest.mark.asyncio
async def test_v05_consume_validates_role_version_ownership(client):
    first = await prepare_publishable_role(client, structured=False, with_knowledge=True)
    second = await prepare_publishable_role(client, structured=False, with_knowledge=True)

    response = await client.post(
        f"/role-assets/{first['role_id']}/consume",
        json={
            "query": "请给出经营判断。",
            "role_version_id": second["published_version_id"],
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "指定的版本不属于该角色"
