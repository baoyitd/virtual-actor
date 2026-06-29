import pytest

from app.services.knowledge_platform import (
    KnowledgePlatformError,
    KnowledgePlatformRefusalError,
    KnowledgePlatformService,
)


@pytest.mark.asyncio
async def test_list_documents_returns_manifest(monkeypatch):
    service = KnowledgePlatformService()

    class FakeResponse:
        status_code = 200

        @staticmethod
        def json():
            return {
                "package_id": "eve",
                "documents": [
                    {"knowledge_object_id": "docs/p1.md", "title": "P1文档", "tier": "P1", "doc_role": "master_doc"},
                    {"knowledge_object_id": "docs/p2.md", "title": "P2文档", "tier": "P2", "doc_role": "supporting_doc"},
                ],
            }

    async def fake_request(method, path, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(service, "_request", fake_request)

    docs = await service.list_documents("eve")
    assert len(docs) == 2
    assert docs[0]["tier"] == "P1"


@pytest.mark.asyncio
async def test_list_packages_sorts_default_first(monkeypatch):
    service = KnowledgePlatformService()

    class FakeResponse:
        status_code = 200

        @staticmethod
        def json():
            return [
                {"package_id": "other", "name": "其他知识包"},
                {"package_id": "eve", "name": "主知识包"},
            ]

    async def fake_request(method, path, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(service, "_request", fake_request)

    items = await service.list_packages()
    normalized = [service.normalize_knowledge_base(item) for item in items]
    assert normalized[0]["kb_id"] == "eve"


@pytest.mark.asyncio
async def test_health_checks_packages_endpoint(monkeypatch):
    service = KnowledgePlatformService()

    class FakeResponse:
        def __init__(self, status_code):
            self.status_code = status_code

    async def fake_request(method, path, **kwargs):
        assert path == "/api/public/packages"
        return FakeResponse(200)

    monkeypatch.setattr(service, "_request", fake_request)
    assert await service.health() is True


@pytest.mark.asyncio
async def test_retrieve_returns_chunks_with_tier(monkeypatch):
    service = KnowledgePlatformService()

    class FakeResponse:
        status_code = 200

        @staticmethod
        def json():
            return {
                "route": {"question_type": "Q1", "allowed_tiers": ["P1"]},
                "hits": [
                    {
                        "title": "制度文档",
                        "knowledge_object_id": "docs/policy.md",
                        "tier": "P1",
                        "doc_role": "master_doc",
                        "evidence_type": "policy",
                        "score": 41.6,
                        "snippet": "关键制度片段",
                        "source_reference": "docs/policy.md#L100",
                    }
                ],
            }

    async def fake_request(method, path, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(service, "_request", fake_request)
    chunks = await service.retrieve(["eve"], "制度依据")
    assert len(chunks) == 1
    assert chunks[0]["tier"] == "P1"
    assert chunks[0]["source"] == "docs/policy.md#L100"
    assert chunks[0]["knowledge_object_id"] == "docs/policy.md"


@pytest.mark.asyncio
async def test_retrieve_raises_refusal_on_q0(monkeypatch):
    service = KnowledgePlatformService()

    class FakeResponse:
        status_code = 200

        @staticmethod
        def json():
            return {
                "route": {"question_type": "Q0", "allowed_tiers": []},
                "refused": True,
                "refusal_reason": "越界问题",
                "hits": [],
            }

    async def fake_request(method, path, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(service, "_request", fake_request)
    with pytest.raises(KnowledgePlatformRefusalError):
        await service.retrieve(["eve"], "无关问题")


@pytest.mark.asyncio
async def test_retrieve_raises_runtime_error_on_unreachable(monkeypatch):
    service = KnowledgePlatformService()

    async def fake_request(method, path, **kwargs):
        return None

    monkeypatch.setattr(service, "_request", fake_request)

    with pytest.raises(KnowledgePlatformError):
        await service.retrieve(["eve"], "测试问题")


@pytest.mark.asyncio
async def test_current_version_id_from_status(monkeypatch):
    service = KnowledgePlatformService()

    class FakeResponse:
        status_code = 200

        @staticmethod
        def json():
            return {
                "package_id": "eve",
                "version_id": "abc123def456",
            }

    async def fake_request(method, path, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(service, "_request", fake_request)
    version_id = await service.current_version_id()
    assert version_id == "abc123def456"
