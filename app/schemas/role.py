"""v0.5 角色相关 Pydantic Schema"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class RoleStatus(str, Enum):
    DRAFT = "draft"
    TEST = "test"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Layer(str, Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"


class ConsumeStatus(str, Enum):
    SUCCESS = "success"
    INSUFFICIENT_CONTEXT = "insufficient_context"
    INSUFFICIENT_KNOWLEDGE = "insufficient_knowledge"
    BOUNDARY_BLOCKED = "boundary_blocked"
    SYSTEM_FAILED = "system_failed"
    UNDEFINED = "undefined"


class CallerType(str, Enum):
    HUMAN = "human"
    AGENT_PLATFORM = "agent_platform"
    DECISION_PRODUCT = "decision_product"
    SYSTEM = "system"
    EXTERNAL_TOOL = "external_tool"
    EXTERNAL_SKILL = "external_skill"


class OutputMode(str, Enum):
    FREEFORM = "freeform"
    STRUCTURED = "structured"


class Visibility(str, Enum):
    INTERNAL = "内部"
    DEPARTMENT = "部门"
    PUBLIC = "公开"


class Category(str, Enum):
    INDUSTRY_EXPERT = "行业专家"
    FUNCTION_ASSISTANT = "职能助手"
    POLICY_ADVISOR = "制度顾问"
    PROJECT_GOVERNANCE = "项目管理"
    CUSTOM = "自定义"


class BoundaryDimension(str, Enum):
    WITHIN_BOUNDARY = "within_boundary"
    NEAR_BOUNDARY = "near_boundary"
    OUT_OF_SCOPE = "out_of_scope"
    NOT_APPLICABLE = "not_applicable"


class BriefingStatus(str, Enum):
    MISSING = "missing"
    FRESH = "fresh"
    STALE = "stale"


class ModelBinding(BaseModel):
    model_provider: str | None = Field(default=None)
    model_name: str | None = Field(default=None)
    temperature: float = Field(default=0.3, ge=0, le=2.0)
    max_tokens: int = Field(default=4096, gt=0)
    fallback_enabled: bool = False
    inherited: bool = True


class DataAssetBindingSummary(BaseModel):
    id: str
    display_name: str
    datasource_ref: str
    database_name: str
    table_name: str
    scope_summary: str
    freshness: str | None = None
    owner_team: str | None = None
    status: str


class KnowledgeStatusSummary(BaseModel):
    state: str
    label: str
    detail: str
    tier_summary: dict[str, int] | None = None


class DataCapabilitySummary(BaseModel):
    state: str
    label: str
    detail: str


class ValidationSummary(BaseModel):
    has_record: bool = False
    latest_status: str | None = None
    latest_tested_at: datetime | None = None
    total_count: int = 0


class OutputPreview(BaseModel):
    output_mode: OutputMode
    output_type: str | None = None
    summary: str
    schema_preview: dict | None = None


class ProgressItem(BaseModel):
    key: str
    label: str
    state: str
    detail: str


class RequirementItem(BaseModel):
    key: str
    label: str
    status: str
    message: str
    route_screen: str | None = None
    route_step: str | None = None


class ReadinessPanel(BaseModel):
    stage: str
    ready: bool
    hard_requirements: list[RequirementItem] = Field(default_factory=list)
    soft_hints: list[RequirementItem] = Field(default_factory=list)


class LegacyInfo(BaseModel):
    is_legacy: bool = False
    missing_requirements: list[str] = Field(default_factory=list)
    legacy_fields: dict[str, object] = Field(default_factory=dict)


class KnowledgeBindingInput(BaseModel):
    kb_id: str | None = None
    knowledge_object_id: str = Field(min_length=1)
    knowledge_version_id: str | None = None
    title: str | None = None
    type: str | None = None


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    bio: str = Field(min_length=1, max_length=512)
    tags: list[str] = Field(default_factory=list)

    category: str = Field(default=Category.CUSTOM.value)
    owner: str = Field(default="", max_length=64)
    maintainer: str | None = Field(default=None, max_length=64)
    business_domain: str | None = Field(default=None, max_length=64)
    visibility: str = Field(default=Visibility.INTERNAL.value)
    enterprise_role_mapping: list[str] = Field(default_factory=list)

    main_duty_cluster: str | None = Field(default=None, max_length=1024)
    point_of_view: str | None = Field(default=None, max_length=512)
    decision_style: str | None = Field(default=None, max_length=64)
    identity_background: str | None = Field(default=None, max_length=1024)
    speaking_style: str | None = Field(default=None, max_length=1024)

    knowledge_boundary: str | None = Field(default=None, max_length=1024)
    knowledge_bindings: list[KnowledgeBindingInput] = Field(default_factory=list)
    data_asset_binding_ids: list[str] = Field(default_factory=list)

    output_mode: OutputMode = OutputMode.FREEFORM
    output_type: str | None = Field(default=None, max_length=64)
    output_schema: dict | None = None
    model_binding: ModelBinding | None = None

    applicable_scenarios: list[str] | None = None
    usage_notes: str | None = None
    support_basis_summary: str | None = None


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    bio: str | None = Field(default=None, min_length=1, max_length=512)
    tags: list[str] | None = None

    category: str | None = None
    owner: str | None = None
    maintainer: str | None = None
    business_domain: str | None = None
    visibility: str | None = None
    enterprise_role_mapping: list[str] | None = None

    main_duty_cluster: str | None = None
    point_of_view: str | None = None
    decision_style: str | None = None
    identity_background: str | None = None
    speaking_style: str | None = None

    knowledge_boundary: str | None = None
    knowledge_bindings: list[KnowledgeBindingInput] | None = None
    data_asset_binding_ids: list[str] | None = None

    output_mode: OutputMode | None = None
    output_type: str | None = None
    output_schema: dict | None = None
    model_binding: ModelBinding | None = None


class BriefingSaveRequest(BaseModel):
    applicable_scenarios: list[str] | None = None
    usage_notes: str | None = None
    support_basis_summary: str | None = None
    confirm_current: bool = False


class RoleListItem(BaseModel):
    role_id: str
    role_version_id: str | None = None
    published_version_id: str | None = None
    role_name: str
    bio: str
    tags: list[str] = Field(default_factory=list)
    status: RoleStatus
    summary: str = ""
    model_binding: ModelBinding | None = None
    has_test_record: bool = False
    latest_test_rating: int | None = None
    latest_tested_at: datetime | None = None
    test_run_count: int = 0
    updated_at: datetime | None = None
    category: str = Category.CUSTOM.value
    owner: str = ""
    visibility: str = Visibility.INTERNAL.value
    business_domain: str | None = None
    creation_source: str = "manual"
    output_mode: OutputMode = OutputMode.FREEFORM
    output_type: str | None = None
    briefing_status: BriefingStatus = BriefingStatus.MISSING
    recommend_pool_eligible: bool = False
    legacy_incomplete: bool = False

    model_config = ConfigDict(from_attributes=True)


class RoleBriefingView(BaseModel):
    status: BriefingStatus
    applicable_scenarios: list[str] = Field(default_factory=list)
    usage_notes: str = ""
    support_basis_summary: str = ""
    knowledge_status: KnowledgeStatusSummary
    data_capability_status: DataCapabilitySummary
    validation_summary: ValidationSummary
    output_preview: OutputPreview
    source_hint: str
    source_changed: bool = False
    saved_at: datetime | None = None


class RoleDetail(BaseModel):
    role_id: str
    role_version_id: str | None = None
    published_version_id: str | None = None
    name: str
    bio: str
    tags: list[str] = Field(default_factory=list)
    status: RoleStatus

    category: str = Category.CUSTOM.value
    owner: str = ""
    maintainer: str | None = None
    business_domain: str | None = None
    visibility: str = Visibility.INTERNAL.value
    creation_source: str = "manual"
    enterprise_role_mapping: list[str] = Field(default_factory=list)

    main_duty_cluster: str | None = None
    point_of_view: str | None = None
    decision_style: str | None = None
    identity_background: str | None = None
    speaking_style: str | None = None

    knowledge_boundary: str | None = None
    output_mode: OutputMode = OutputMode.FREEFORM
    output_type: str | None = None
    output_schema: dict | None = None
    model_binding: ModelBinding | None = None

    knowledge_refs: list["KnowledgeRefOut"] = Field(default_factory=list)
    validated_knowledge_versions: list["KnowledgeVersionOut"] = Field(default_factory=list)
    data_asset_bindings: list[DataAssetBindingSummary] = Field(default_factory=list)

    briefing: RoleBriefingView

    definition_progress: list[ProgressItem] = Field(default_factory=list)
    share_readiness: ReadinessPanel
    publish_readiness: ReadinessPanel
    legacy: LegacyInfo = Field(default_factory=LegacyInfo)

    has_test_record: bool = False
    latest_test_rating: int | None = None
    latest_tested_at: datetime | None = None
    latest_validation_status: str | None = None
    test_run_count: int = 0

    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class RoleWorkspaceSummary(BaseModel):
    role_id: str
    role_version_id: str | None = None
    status: RoleStatus
    definition_progress: list[ProgressItem] = Field(default_factory=list)
    share_readiness: ReadinessPanel
    publish_readiness: ReadinessPanel
    legacy: LegacyInfo = Field(default_factory=LegacyInfo)


class RoleVersionPublicResponse(BaseModel):
    role_id: str
    role_version_id: str
    name: str
    summary: str
    business_domain: str | None = None
    main_duty_cluster: str | None = None
    point_of_view: str | None = None
    knowledge_boundary: str | None = None
    output_mode: OutputMode = OutputMode.FREEFORM
    output_type: str | None = None
    output_schema: dict | None = None
    model_binding: ModelBinding | None = None
    data_asset_bindings: list[DataAssetBindingSummary] = Field(default_factory=list)
    briefing: RoleBriefingView
    knowledge_refs: list["KnowledgeRefPublicOut"] = Field(default_factory=list)
    validated_knowledge_versions: list["KnowledgeVersionOut"] = Field(default_factory=list)
    has_test_record: bool = False
    latest_tested_at: datetime | None = None
    test_run_count: int = 0


from app.schemas.knowledge import (  # noqa: E402
    KnowledgeRefOut,
    KnowledgeRefPublicOut,
    KnowledgeVersionOut,
)
