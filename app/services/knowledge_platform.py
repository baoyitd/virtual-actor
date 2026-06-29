"""知识平台 API 调用服务 — Knowledge Workbench 公共契约接口"""
import urllib.parse

import httpx
from app.config import settings


class KnowledgePlatformError(RuntimeError):
    """知识平台运行错误。"""


class KnowledgePlatformRefusalError(KnowledgePlatformError):
    """知识平台路由判定越界（Q0），拒答。"""


class KnowledgePlatformService:
    def __init__(self):
        self.base_url = getattr(settings, "KNOWLEDGE_API_BASE", "http://localhost:3099").rstrip("/")
        self.default_package_id = getattr(settings, "KNOWLEDGE_DEFAULT_PACKAGE_ID", "eve")

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response | None:
        async with httpx.AsyncClient(timeout=kwargs.pop("timeout", 30.0)) as client:
            try:
                return await client.request(method, f"{self.base_url}{path}", **kwargs)
            except Exception:
                return None

    async def list_packages(self) -> list[dict]:
        resp = await self._request("GET", "/api/public/packages", timeout=10.0)
        if not resp or resp.status_code >= 400:
            return []
        items = resp.json()
        return sorted(items, key=self._knowledge_base_sort_key)

    async def list_knowledge_bases(self) -> list[dict]:
        return await self.list_packages()

    async def list_documents(self, package_id: str | None = None) -> list[dict]:
        pid = urllib.parse.quote(str(package_id or self.default_package_id), safe="")
        resp = await self._request("GET", f"/api/public/packages/{pid}/manifest", timeout=10.0)
        if not resp or resp.status_code >= 400:
            return []
        return resp.json().get("documents", [])

    async def list_files(self, kb_id: str | None = None) -> list[dict]:
        return await self.list_documents(kb_id)

    async def get_manifest(self, package_id: str | None = None) -> dict | None:
        pid = urllib.parse.quote(str(package_id or self.default_package_id), safe="")
        resp = await self._request("GET", f"/api/public/packages/{pid}/manifest", timeout=10.0)
        if not resp or resp.status_code >= 400:
            return None
        return resp.json()

    async def retrieve(
        self,
        kb_ids: list[str],
        query: str,
        k: int = 3,
        knowledge_object_ids: list[str] | None = None,
    ) -> list[dict]:
        resp = await self._request(
            "POST",
            "/api/public/retrieve",
            json={"question": query, "knowledge_object_ids": knowledge_object_ids},
            timeout=30.0,
        )
        if not resp:
            raise KnowledgePlatformError("知识平台不可达")
        if resp.status_code >= 400:
            raise KnowledgePlatformError(f"知识检索失败（HTTP {resp.status_code}）")

        data = resp.json()

        if data.get("refused"):
            raise KnowledgePlatformRefusalError(
                data.get("refusal_reason", "知识平台判定当前问题越界，拒答。")
            )

        hits = data.get("hits", [])
        chunks: list[dict] = []
        for hit in hits:
            knowledge_object_id = hit.get("knowledge_object_id", "")
            chunks.append(
                {
                    "chunk": hit.get("snippet", ""),
                    "source": hit.get("source_reference") or hit.get("title", ""),
                    "title": hit.get("title", ""),
                    "score": hit.get("score", 0),
                    "tier": hit.get("tier", ""),
                    "doc_role": hit.get("doc_role", ""),
                    "evidence_type": hit.get("evidence_type", ""),
                    "relative_path": knowledge_object_id,
                    "knowledge_object_id": knowledge_object_id,
                }
            )
        return chunks

    async def get_package_status(self, package_id: str | None = None) -> dict | None:
        pid = urllib.parse.quote(str(package_id or self.default_package_id), safe="")
        resp = await self._request("GET", f"/api/public/packages/{pid}/status", timeout=10.0)
        if not resp or resp.status_code >= 400:
            return None
        return resp.json()

    async def get_version(self) -> dict:
        status = await self.get_package_status()
        if status is None:
            return {"error": "知识平台版本接口不可达"}
        return status

    async def current_version_id(self) -> str | None:
        data = await self.get_version()
        if data.get("error"):
            return None
        for key in ("version_id", "commit_hash", "version", "id"):
            value = data.get(key)
            if value:
                return str(value)
        return None

    async def route(self, query: str, knowledge_object_ids: list[str] | None = None) -> dict | None:
        resp = await self._request(
            "POST",
            "/api/public/route",
            json={"question": query, "knowledge_object_ids": knowledge_object_ids},
            timeout=10.0,
        )
        if not resp or resp.status_code >= 400:
            return None
        return resp.json()

    @staticmethod
    def build_prompt_with_knowledge(system_prompt: str, chunks: list[dict]) -> str:
        valid = [c for c in chunks if not c.get("error")]
        if not valid:
            return system_prompt
        knowledge = "\n\n".join(
            f"[参考知识 {i+1}，来源: {c.get('source', '?')}，权威层级: {c.get('tier', '未知')}]\n{c.get('chunk', '')[:500]}"
            for i, c in enumerate(valid)
        )
        return f"{system_prompt}\n\n请基于以下参考知识回答用户问题。若知识不足请说明。\n\n{knowledge}"

    @staticmethod
    def normalize_file(item: dict, kb_id: str, default_version_id: str | None = None) -> dict:
        knowledge_object_id = str(
            item.get("knowledge_object_id") or item.get("relative_path") or item.get("doc_id") or ""
        )
        title = str(
            item.get("title") or item.get("relative_path") or knowledge_object_id
        )
        return {
            "kb_id": str(kb_id),
            "knowledge_object_id": knowledge_object_id,
            "knowledge_version_id": str(default_version_id or ""),
            "title": title,
            "type": item.get("evidence_type") or item.get("type"),
            "tags": [],
            "summary": str(item.get("title", "")),
            "source_id": knowledge_object_id or None,
            "tier": item.get("tier", ""),
            "doc_role": item.get("doc_role", ""),
            "evidence_type": item.get("evidence_type", ""),
            "canonical": item.get("canonical_default"),
            "use_for": item.get("use_for", []),
            "not_for": item.get("not_for", []),
        }

    @staticmethod
    def normalize_knowledge_base(item: dict) -> dict:
        return {
            "kb_id": str(item.get("package_id") or item.get("id") or item.get("kb_id") or ""),
            "name": str(item.get("name") or item.get("package_id") or item.get("title") or ""),
        }

    def preferred_knowledge_base(self, items: list[dict]) -> dict | None:
        normalized = [self.normalize_knowledge_base(item) for item in items]
        for item in normalized:
            if item["kb_id"] == self.default_package_id:
                return item
        return normalized[0] if normalized else None

    def resolve_runtime_kb_id_from_bases(
        self,
        kb_id: str | None,
        knowledge_object_id: str | None = None,
        knowledge_bases: list[dict] | None = None,
    ) -> str | None:
        raw = str(kb_id or "").strip()
        normalized = [self.normalize_knowledge_base(item) for item in (knowledge_bases or [])]
        if not normalized:
            return raw or self.default_package_id

        by_id = {item["kb_id"]: item for item in normalized if item["kb_id"]}
        by_name = {item["name"]: item for item in normalized if item["name"]}

        # 1. 精确匹配 package_id
        if raw in by_id:
            return raw

        # 2. 按 name 匹配（如传入 "10-Areas/eve" 匹配到 package_id="eve"）
        if raw in by_name:
            return by_name[raw]["kb_id"]

        # 3. 从 knowledge_object_id 路径反推所属包
        if knowledge_object_id:
            resolved = self._resolve_kb_id_from_object_id(knowledge_object_id, normalized)
            if resolved:
                return resolved

        # 4. 仍无法解析时优先返回默认包（如果存在），否则保留原值
        if self.default_package_id in by_id:
            return self.default_package_id

        return raw or self.default_package_id

    @staticmethod
    def _resolve_kb_id_from_object_id(knowledge_object_id: str, normalized: list[dict]) -> str | None:
        """从 knowledge_object_id 的路径前缀反推所属知识包。

        知识平台的 package_id 通常是 Vault 的一级目录名（如 eve、ai、togaf、快消品行业知识），
        而 knowledge_object_id 是 Vault 相对路径（如 30-Resources/快消品行业知识/44-xxx.md）。
        通过比对路径段来匹配。
        """
        oid = str(knowledge_object_id or "").strip()
        if not oid:
            return None

        for item in normalized:
            pid = item.get("kb_id", "")
            name = item.get("name", "")
            if not pid:
                continue
            # 尝试 package_id 作为路径段
            if f"/{pid}/" in f"/{oid}/" or oid.startswith(f"{pid}/"):
                return pid
            # 尝试 name 作为路径段（如 name="30-Resources/快消品行业知识"）
            if name and (f"/{name}/" in f"/{oid}/" or oid.startswith(f"{name}/")):
                return pid
            # 尝试 name 的最后一段
            if name:
                last_segment = name.rstrip("/").rsplit("/", 1)[-1]
                if last_segment and f"/{last_segment}/" in f"/{oid}/":
                    return pid
        return None

    async def resolve_runtime_kb_id(
        self,
        kb_id: str | None,
        knowledge_object_id: str | None = None,
        knowledge_bases: list[dict] | None = None,
    ) -> str | None:
        bases = knowledge_bases if knowledge_bases is not None else await self.list_knowledge_bases()
        return self.resolve_runtime_kb_id_from_bases(kb_id, knowledge_object_id, bases)

    def _knowledge_base_sort_key(self, item: dict) -> tuple[int, str]:
        normalized = self.normalize_knowledge_base(item)
        is_default = normalized["kb_id"] == self.default_package_id
        return (0 if is_default else 1, normalized["name"].casefold())

    async def health(self) -> bool:
        resp = await self._request("GET", "/api/public/packages", timeout=5.0)
        return bool(resp and resp.status_code < 400)

    async def get_tier_distribution(self, knowledge_refs: list) -> dict[str, int]:
        if not knowledge_refs:
            return {}
        # 按 kb_id 分组，分别取对应包的 manifest
        kb_ids = sorted({ref.kb_id for ref in knowledge_refs if ref.kb_id})
        docs_by_path: dict[str, dict] = {}
        for kb_id in kb_ids:
            manifest = await self.get_manifest(kb_id)
            if not manifest:
                continue
            for doc in manifest.get("documents", []):
                path = doc.get("knowledge_object_id") or doc.get("relative_path") or doc.get("doc_id") or ""
                if path:
                    docs_by_path[path] = doc
        # 也尝试默认包
        default_manifest = await self.get_manifest()
        if default_manifest:
            for doc in default_manifest.get("documents", []):
                path = doc.get("knowledge_object_id") or doc.get("relative_path") or doc.get("doc_id") or ""
                if path and path not in docs_by_path:
                    docs_by_path[path] = doc
        tier_counts: dict[str, int] = {}
        for ref in knowledge_refs:
            doc = docs_by_path.get(ref.knowledge_object_id)
            if doc:
                tier = doc.get("tier", "unknown")
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
        return tier_counts


knowledge_platform = KnowledgePlatformService()
