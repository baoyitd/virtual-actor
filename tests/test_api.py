"""角色产品完整测试 — 27 用例"""
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login = await ac.post("/auth/login", json={"username": "admin", "password": "admin123"})
        assert login.status_code == 200
        ac.headers.update({"Authorization": f"Bearer {login.json()['access_token']}"})
        yield ac


ROLE = {"name": "测试", "bio": "test bio", "model_binding": {"model_provider": "openai", "model_name": "gpt-4o"}}


async def make_publishable(client):
    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    await client.post(f"/role-assets/{rid}/knowledge", json={"knowledge_object_id": "eve/test", "title": "T"})
    await client.post(f"/role-assets/{rid}/test", json={"test_input": "hi"})
    await client.post(f"/role-assets/{rid}/to-test")
    return rid


# ── API 基础 ──
@pytest.mark.asyncio
async def test_a01_health(client):
    r = await client.get("/health")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_a01b_auth_required():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/role-assets")
        assert r.status_code == 401


@pytest.mark.asyncio
async def test_a02_create_role(client):
    r = await client.post("/role-assets", json=ROLE)
    assert r.status_code == 201
    assert r.json()["name"] == "测试"


@pytest.mark.asyncio
async def test_a03_list_roles(client):
    r = await client.get("/role-assets")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_a04_get_role(client):
    cr = await client.post("/role-assets", json={"name": "详情测试", "bio": "test", "model_binding": {"model_provider": "openai", "model_name": "gpt-4o"}})
    rid = cr.json()["role_id"]
    r = await client.get(f"/role-assets/{rid}")
    assert r.status_code == 200
    assert r.json()["name"] == "详情测试"


@pytest.mark.asyncio
async def test_a05_update_role(client):
    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    r = await client.patch(f"/role-assets/{rid}", json={"point_of_view": "保守"})
    assert r.status_code == 200
    assert r.json()["point_of_view"] == "保守"


@pytest.mark.asyncio
async def test_a06_delete_role(client):
    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    r = await client.delete(f"/role-assets/{rid}")
    assert r.status_code == 204


# ── 状态迁移 ──
@pytest.mark.asyncio
async def test_a07_to_test(client):
    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    r = await client.post(f"/role-assets/{rid}/to-test")
    assert r.status_code == 200
    assert r.json()["status"] == "test"


@pytest.mark.asyncio
async def test_a08_publish(client):
    rid = await make_publishable(client)
    r = await client.post(f"/role-assets/{rid}/publish?published_by=admin")
    assert r.status_code == 200
    assert r.json()["status"] == "published"


@pytest.mark.asyncio
async def test_a09_archive(client):
    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    r = await client.post(f"/role-assets/{rid}/archive")
    assert r.status_code == 200
    assert r.json()["status"] == "archived"


# ── 版本 ──
@pytest.mark.asyncio
async def test_a10_published_version(client):
    rid = await make_publishable(client)
    await client.post(f"/role-assets/{rid}/publish?published_by=admin")
    r = await client.get(f"/role-assets/{rid}/published-version")
    assert r.status_code == 200
    assert "role_version_id" in r.json()


@pytest.mark.asyncio
async def test_a11_version_detail(client):
    cr = await client.post("/role-assets", json=ROLE)
    vid = cr.json()["role_version_id"]
    r = await client.get(f"/role-versions/{vid}")
    assert r.status_code == 200
    assert "model_binding" in r.json()


@pytest.mark.asyncio
async def test_a12_version_list(client):
    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    r = await client.get(f"/role-assets/{rid}/versions")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── 知识绑定 ──
@pytest.mark.asyncio
async def test_a13_bind_knowledge(client):
    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    r = await client.post(f"/role-assets/{rid}/knowledge", json={"knowledge_object_id": "eve/test", "title": "T"})
    assert r.status_code == 201
    assert r.json()["kb_id"] == "kb-eve"
    assert r.json()["knowledge_object_id"] == "eve/test"
    assert r.json()["knowledge_version_id"] == "test-knowledge-version"


@pytest.mark.asyncio
async def test_a13b_knowledge_catalog(client):
    r = await client.get("/knowledge/catalog")
    assert r.status_code == 200
    assert r.json()[0]["kb_id"] == "kb-eve"
    assert r.json()[0]["knowledge_object_id"] == "eve/test"


@pytest.mark.asyncio
async def test_a13ba_knowledge_bases(client):
    r = await client.get("/knowledge/bases")
    assert r.status_code == 200
    assert r.json() == [
        {"kb_id": "kb-eve", "name": "knowledge-eve"},
        {"kb_id": "kb-ops", "name": "运营治理知识"},
    ]


@pytest.mark.asyncio
async def test_a13c_knowledge_catalog_blocks_when_platform_unreachable(client, monkeypatch):
    from app.services.knowledge_platform import knowledge_platform

    async def fake_health():
        return False

    monkeypatch.setattr(knowledge_platform, "health", fake_health)
    r = await client.get("/knowledge/catalog")
    assert r.status_code == 503
    assert r.json()["detail"] == "知识平台不可达，无法浏览知识"


@pytest.mark.asyncio
async def test_a13d_bind_knowledge_blocks_when_platform_unreachable_even_with_manual_version(client, monkeypatch):
    from app.services.knowledge_platform import knowledge_platform

    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]

    async def fake_health():
        return False

    monkeypatch.setattr(knowledge_platform, "health", fake_health)
    r = await client.post(
        f"/role-assets/{rid}/knowledge",
        json={
            "knowledge_object_id": "eve/test",
            "knowledge_version_id": "manual-version",
            "title": "T",
        },
    )
    assert r.status_code == 503
    assert r.json()["detail"] == "知识平台不可达，无法绑定知识"


@pytest.mark.asyncio
async def test_a14_list_knowledge(client):
    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    await client.post(f"/role-assets/{rid}/knowledge", json={"knowledge_object_id": "eve/test"})
    r = await client.get(f"/role-assets/{rid}/knowledge")
    assert r.status_code == 200
    assert len(r.json()) >= 1
    assert r.json()[0]["kb_id"] == "kb-eve"


@pytest.mark.asyncio
async def test_a15_unbind_knowledge(client):
    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    kr = await client.post(f"/role-assets/{rid}/knowledge", json={"knowledge_object_id": "eve/test"})
    ref_id = kr.json()["id"]
    r = await client.delete(f"/role-assets/{rid}/knowledge/{ref_id}")
    assert r.status_code == 204


# ── 测试 ──
@pytest.mark.asyncio
async def test_a16_run_test(client):
    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    await client.post(f"/role-assets/{rid}/knowledge", json={"knowledge_object_id": "eve/test", "title": "T"})
    r = await client.post(f"/role-assets/{rid}/test", json={"test_input": "hi"})
    assert r.status_code == 200
    assert "test_output" in r.json()
    assert r.json()["knowledge_retrieved"][0]["source"] == "治理测试知识.md"


@pytest.mark.asyncio
async def test_a16b_run_test_uses_bound_kb_ids(client, monkeypatch):
    from app.services.knowledge_platform import knowledge_platform

    captured = {}

    async def fake_retrieve(kb_ids, query, k=3):
        captured["kb_ids"] = kb_ids
        return [{"chunk": "多知识库测试片段", "source": "运营流程知识.md", "score": 0.88}]

    monkeypatch.setattr(knowledge_platform, "retrieve", fake_retrieve)

    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    bind = await client.post(
        f"/role-assets/{rid}/knowledge",
        json={"kb_id": "kb-ops", "knowledge_object_id": "ops/playbook/start.md", "title": "运营流程知识"},
    )
    assert bind.status_code == 201

    r = await client.post(f"/role-assets/{rid}/test", json={"test_input": "hi"})
    assert r.status_code == 200
    assert captured["kb_ids"] == ["kb-ops"]


@pytest.mark.asyncio
async def test_a17_test_history(client):
    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    r = await client.get(f"/role-assets/{rid}/tests")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_a18_rate_test(client):
    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    await client.post(f"/role-assets/{rid}/knowledge", json={"knowledge_object_id": "eve/test", "title": "T"})
    tr = await client.post(f"/role-assets/{rid}/test", json={"test_input": "hi"})
    tid = tr.json()["id"]
    r = await client.post(f"/test-runs/{tid}/rate", json={"human_rating": 4})
    assert r.status_code == 200
    assert r.json()["human_rating"] == 4


@pytest.mark.asyncio
async def test_a18b_publish_requires_knowledge_and_test(client):
    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    r = await client.post(f"/role-assets/{rid}/publish")
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_a18c_test_requires_bound_knowledge(client):
    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    r = await client.post(f"/role-assets/{rid}/test", json={"test_input": "hi"})
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_a18d_run_test_blocks_when_platform_unreachable(client, monkeypatch):
    from app.services.knowledge_platform import knowledge_platform

    cr = await client.post("/role-assets", json=ROLE)
    rid = cr.json()["role_id"]
    await client.post(f"/role-assets/{rid}/knowledge", json={"knowledge_object_id": "eve/test", "title": "T"})

    async def fake_health():
        return False

    monkeypatch.setattr(knowledge_platform, "health", fake_health)
    r = await client.post(f"/role-assets/{rid}/test", json={"test_input": "hi"})
    assert r.status_code == 400
    assert r.json()["detail"] == "知识平台不可达，无法运行角色测试"


# ── 异常 ──
@pytest.mark.asyncio
async def test_a19_role_404(client):
    r = await client.get("/role-assets/nonexistent")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_a20_update_404(client):
    r = await client.patch("/role-assets/nonexistent", json={"name": "x"})
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_a21_create_empty_name(client):
    r = await client.post("/role-assets", json={"name": "", "bio": "x", "model_binding": {"model_provider": "o", "model_name": "g"}})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_a22_create_no_model(client):
    r = await client.post("/role-assets", json={"name": "x", "bio": "x"})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_a23_bind_knowledge_404_role(client):
    r = await client.post("/role-assets/nonexistent/knowledge", json={"knowledge_object_id": "x"})
    assert r.status_code == 404


# ── 筛选 ──
@pytest.mark.asyncio
async def test_a24_filter_published(client):
    r = await client.get("/role-assets?status=published")
    assert r.status_code == 200
    for item in r.json():
        assert item["status"] == "published"


@pytest.mark.asyncio
async def test_a24b_edit_published_creates_new_draft_version(client):
    rid = await make_publishable(client)
    pub = await client.post(f"/role-assets/{rid}/publish?published_by=admin")
    published_version = pub.json()["role_version_id"]

    updated = await client.patch(f"/role-assets/{rid}", json={"point_of_view": "新立场"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "draft"
    assert updated.json()["role_version_id"] != published_version

    old_version = await client.get(f"/role-versions/{published_version}")
    assert old_version.status_code == 200
    assert old_version.json()["role_version_id"] == published_version


@pytest.mark.asyncio
async def test_a25_filter_draft(client):
    r = await client.get("/role-assets?status=draft")
    assert r.status_code == 200
    for item in r.json():
        assert item["status"] in ("draft",)


# ── 依赖 ──
@pytest.mark.asyncio
async def test_a26_knowledge_health(client):
    r = await client.get("/health/knowledge-platform")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_a27_create_after_delete(client):
    """MySQL 持久性: 删除后创建同名字段不报错"""
    r1 = await client.post("/role-assets", json={"name": "持久测试", "bio": "t", "model_binding": {"model_provider": "o", "model_name": "g"}})
    rid = r1.json()["role_id"]
    await client.delete(f"/role-assets/{rid}")
    r2 = await client.post("/role-assets", json={"name": "持久测试", "bio": "t", "model_binding": {"model_provider": "o", "model_name": "g"}})
    assert r2.status_code == 201
