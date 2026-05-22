import pytest

from app.services.knowledge_platform import KnowledgePlatformService


@pytest.mark.asyncio
async def test_list_files_paginates_until_all_pages(monkeypatch):
    service = KnowledgePlatformService()
    seen_paths = []

    class FakeResponse:
        def __init__(self, items):
            self.status_code = 200
            self._items = items

        def json(self):
            return {"items": self._items}

    async def fake_request(method, path, **kwargs):
        seen_paths.append(path)
        if "page=1" in path:
            return FakeResponse(
                [
                    {"id": f"file-{index}", "knowledge_object_id": f"docs/{index}.md"}
                    for index in range(50)
                ]
            )
        if "page=2" in path:
            return FakeResponse(
                [
                    {"id": f"file-{index}", "knowledge_object_id": f"docs/{index}.md"}
                    for index in range(50, 63)
                ]
            )
        return FakeResponse([])

    monkeypatch.setattr(service, "_request", fake_request)

    items = await service.list_files("kb-eve", page_size=50)
    assert len(items) == 63
    assert seen_paths == [
        "/api/v1/knowledge/kb-eve/files?limit=50&page=1",
        "/api/v1/knowledge/kb-eve/files?limit=50&page=2",
    ]
