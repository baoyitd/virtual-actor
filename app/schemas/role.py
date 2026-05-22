"""角色相关 Pydantic Schema"""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class RoleStatus(str, Enum):
    DRAFT = "draft"
    TEST = "test"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Layer(str, Enum):
    L1_IDENTITY = "L1"
    L2_MIND = "L2"
    L3_KNOWLEDGE = "L3"
    L4_CAPABILITY = "L4"
    L5_CONFIG = "L5"


# ── 模型绑定 ──

class ModelBinding(BaseModel):
    model_provider: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    temperature: float = Field(default=0.7, ge=0, le=2.0)
    max_tokens: int = Field(default=4096, gt=0)
    fallback_enabled: bool = False


# ── 角色创建/更新 ──

class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    bio: str = Field(min_length=1, max_length=512)
    tags: list[str] = []
    # L2 可选项
    identity_background: str | None = None
    point_of_view: str | None = None
    decision_style: str | None = None
    responsibility_boundary: str | None = None
    speaking_style: str | None = None
    # L4 可选项
    collaboration_mode: str | None = None
    capability_boundary: str | None = None
    # L5 必填
    model_binding: ModelBinding


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    bio: str | None = Field(default=None, min_length=1, max_length=512)
    tags: list[str] | None = None
    # L2
    identity_background: str | None = None
    point_of_view: str | None = None
    decision_style: str | None = None
    responsibility_boundary: str | None = None
    speaking_style: str | None = None
    # L4
    collaboration_mode: str | None = None
    capability_boundary: str | None = None
    # L5
    model_binding: ModelBinding | None = None

    class Config:
        # 允许 partial update，只更新传入的字段
        pass


# ── 角色列表（公开） ──

class RoleListItem(BaseModel):
    """GET /role-assets?status=published 返回"""
    role_id: str
    role_version_id: str | None = None
    role_name: str
    bio: str
    tags: list[str] = []
    status: RoleStatus
    summary: str = ""
    model_binding: ModelBinding | None = None
    has_test_record: bool = False
    latest_test_rating: int | None = None
    latest_tested_at: datetime | None = None
    test_run_count: int = 0
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


# ── 角色详情（完整） ──

class RoleDetail(BaseModel):
    """角色完整信息（内部使用）"""
    role_id: str
    role_version_id: str | None = None
    name: str
    bio: str
    tags: list[str] = []
    status: RoleStatus
    # L2
    identity_background: str | None = None
    point_of_view: str | None = None
    decision_style: str | None = None
    responsibility_boundary: str | None = None
    speaking_style: str | None = None
    # L4
    collaboration_mode: str | None = None
    capability_boundary: str | None = None
    # L5
    model_binding: ModelBinding | None = None
    # 知识
    knowledge_refs: list["KnowledgeRefOut"] = []
    validated_knowledge_versions: list["KnowledgeVersionOut"] = []
    # 质量信号
    has_test_record: bool = False
    latest_test_rating: int | None = None
    latest_tested_at: datetime | None = None
    test_run_count: int = 0
    publish_confirmed_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


# ── 版本详情（对决策产品暴露） ──

class RoleVersionPublicResponse(BaseModel):
    """GET /role-versions/{role_version_id} 返回"""
    # 必需
    role_id: str
    role_version_id: str
    summary: str
    model_binding: ModelBinding | None = None
    # 可选
    identity_background: str | None = None
    point_of_view: str | None = None
    decision_style: str | None = None
    responsibility_boundary: str | None = None
    speaking_style: str | None = None
    knowledge_refs: list["KnowledgeRefPublicOut"] = []
    validated_knowledge_versions: list["KnowledgeVersionOut"] = []
    # 局部扩展
    has_test_record: bool = False
    latest_test_rating: int | None = None
    latest_tested_at: datetime | None = None
    test_run_count: int = 0
    publish_confirmed_by: str | None = None

from app.schemas.knowledge import KnowledgeRefOut, KnowledgeRefPublicOut, KnowledgeVersionOut  # noqa: E402
