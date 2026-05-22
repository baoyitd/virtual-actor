"""知识相关 Pydantic Schema"""
from datetime import datetime
from pydantic import BaseModel, Field


class KnowledgeBaseItem(BaseModel):
    kb_id: str
    name: str


class KnowledgeRefOut(BaseModel):
    id: str
    role_id: str
    kb_id: str
    knowledge_object_id: str
    knowledge_version_id: str | None = None
    title: str | None = None
    type: str | None = None
    knowledge_source: str = "knowledge-platform"
    bound_at: datetime | None = None

    class Config:
        from_attributes = True


class KnowledgeRefPublicOut(BaseModel):
    id: str
    role_id: str
    knowledge_object_id: str
    knowledge_version_id: str | None = None
    title: str | None = None
    type: str | None = None
    knowledge_source: str = "knowledge-platform"
    bound_at: datetime | None = None

    class Config:
        from_attributes = True


class KnowledgeVersionOut(BaseModel):
    """validated_knowledge_versions — 上位裁决后的最小追溯结构"""
    knowledge_object_id: str
    knowledge_version_id: str

    class Config:
        from_attributes = True


class KnowledgeRefCreate(BaseModel):
    kb_id: str | None = None
    knowledge_object_id: str = Field(min_length=1)
    knowledge_version_id: str | None = None
    title: str | None = None
    type: str | None = None


class KnowledgeCatalogItem(BaseModel):
    kb_id: str
    knowledge_object_id: str
    knowledge_version_id: str | None = None
    title: str
    type: str | None = None
    tags: list[str] = []
    summary: str = ""
    source_id: str | None = None
