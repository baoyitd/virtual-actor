"""知识平台 API 调用服务 — 纯知识供应 + Token 自动刷新"""
import httpx
from app.config import settings


class KnowledgePlatformService:
    def __init__(self):
        self.base_url = getattr(settings, 'KNOWLEDGE_API_BASE', 'http://localhost:3000')
        self.health_url = getattr(settings, 'KNOWLEDGE_HEALTH_URL', 'http://localhost:3099/api/health')
        self.token = getattr(settings, 'KNOWLEDGE_API_TOKEN', '')
        self.kb_eve_id = getattr(settings, 'KNOWLEDGE_DEFAULT_KB_ID', '41cee65b-7f9c-4820-ba0d-bb865e0b1e41')
        self._auth_email = getattr(settings, 'KNOWLEDGE_AUTH_EMAIL', '')
        self._auth_password = getattr(settings, 'KNOWLEDGE_AUTH_PASSWORD', '')

    @property
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    async def _refresh_token(self) -> bool:
        if not self._auth_email or not self._auth_password:
            return False
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{self.base_url}/api/v1/auths/signin",
                    json={"email": self._auth_email, "password": self._auth_password},
                )
                resp.raise_for_status()
                self.token = resp.json().get("token", "")
                return bool(self.token)
        except Exception:
            return False

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response | None:
        async with httpx.AsyncClient(timeout=kwargs.pop("timeout", 30.0)) as client:
            try:
                resp = await client.request(method, f"{self.base_url}{path}", headers=self._headers, **kwargs)
                if resp.status_code == 401 and await self._refresh_token():
                    resp = await client.request(method, f"{self.base_url}{path}", headers=self._headers, **kwargs)
                return resp
            except Exception:
                return None

    # ── 接口 1 ──
    async def list_files(self, kb_id: str = None, page_size: int = 50) -> list[dict]:
        kid = kb_id or self.kb_eve_id
        files: list[dict] = []
        page = 1
        seen_ids: set[str] = set()

        while True:
            resp = await self._request(
                "GET",
                f"/api/v1/knowledge/{kid}/files?limit={page_size}&page={page}",
                timeout=10.0,
            )
            if not resp or resp.status_code >= 400:
                return files

            items_page = resp.json().get("items", [])
            if not items_page:
                break

            for item in items_page:
                source_id = str(item.get("id") or item.get("file_id") or item.get("knowledge_object_id") or "")
                if source_id and source_id in seen_ids:
                    continue
                if source_id:
                    seen_ids.add(source_id)
                files.append(item)

            if len(items_page) < page_size:
                break
            page += 1

        return files

    async def list_knowledge_bases(self) -> list[dict]:
        resp = await self._request("GET", "/api/v1/knowledge/", timeout=10.0)
        return resp.json().get("items", []) if resp and resp.status_code < 400 else []

    # ── 接口 3 ──
    async def retrieve(self, kb_ids: list[str], query: str, k: int = 3) -> list[dict]:
        resp = await self._request("POST", "/api/v1/retrieval/query/collection",
            json={"collection_names": kb_ids, "query": query, "k": k}, timeout=30.0)
        if not resp or resp.status_code >= 400:
            return [{"chunk": "[检索失败]", "source": "", "score": 0, "error": str(resp.status_code) if resp else "?"}]
        data = resp.json()
        chunks = []
        for gi, group in enumerate(data.get("documents", [])):
            for ci, chunk in enumerate(group):
                metas = data.get("metadatas", [])
                dists = data.get("distances", [])
                src = metas[gi][ci].get("name", "?") if gi < len(metas) and ci < len(metas[gi]) else "?"
                score = dists[gi][ci] if gi < len(dists) and ci < len(dists[gi]) else 0
                chunks.append({"chunk": chunk, "source": src, "score": round(score, 3)})
        return chunks

    @staticmethod
    def build_prompt_with_knowledge(system_prompt: str, chunks: list[dict]) -> str:
        valid = [c for c in chunks if not c.get("error")]
        if not valid:
            return system_prompt
        knowledge = "\n\n".join(
            f"[参考知识 {i+1}，来源: {c['source']}]\n{c['chunk'][:500]}"
            for i, c in enumerate(valid)
        )
        return f"{system_prompt}\n\n请基于以下参考知识回答用户问题。若知识不足请说明。\n\n{knowledge}"

    # ── 接口 4 ──
    async def get_version(self) -> dict:
        url = f"{self.base_url}/api/v1/version"
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return {"error": str(e)}

    async def current_version_id(self) -> str | None:
        data = await self.get_version()
        if data.get("error"):
            return None
        for key in ("commit_hash", "version", "version_id", "id"):
            value = data.get(key)
            if value:
                return str(value)
        return None

    @staticmethod
    def normalize_file(item: dict, kb_id: str, default_version_id: str | None = None) -> dict:
        meta = item.get("meta") or item.get("metadata") or {}
        source_id = str(item.get("id") or item.get("file_id") or item.get("name") or "")
        # 上游已明确：消费侧正式真源字段为顶层 knowledge_object_id。
        knowledge_object_id = item.get("knowledge_object_id") or meta.get("knowledge_object_id") or source_id
        title = meta.get("title") or item.get("title") or item.get("filename") or item.get("name") or knowledge_object_id
        tags = meta.get("tags") or item.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        return {
            "kb_id": str(kb_id),
            "knowledge_object_id": str(knowledge_object_id),
            "knowledge_version_id": str(meta.get("knowledge_version_id") or item.get("knowledge_version_id") or default_version_id or ""),
            "title": str(title),
            "type": meta.get("type") or item.get("type"),
            "tags": tags,
            "summary": str(meta.get("summary") or item.get("summary") or ""),
            "source_id": source_id or None,
        }

    @staticmethod
    def normalize_knowledge_base(item: dict) -> dict:
        return {
            "kb_id": str(item.get("id") or item.get("kb_id") or item.get("collection_name") or ""),
            "name": str(item.get("name") or item.get("title") or item.get("id") or item.get("kb_id") or ""),
        }

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(self.health_url)
                return resp.status_code < 500
        except Exception:
            return False


knowledge_platform = KnowledgePlatformService()
