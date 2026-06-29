"""AI 协作创建相关 Schema"""
from pydantic import BaseModel, Field

from app.schemas.role import OutputMode


class AIDraftRequest(BaseModel):
    description: str = Field(min_length=10, max_length=2048, description="角色意图描述")
    category: str | None = None
    business_domain: str | None = None


class AIDraftResponse(BaseModel):
    name: str
    bio: str
    tags: list[str] = Field(default_factory=list)
    main_duty_cluster: str | None = None
    point_of_view: str | None = None
    decision_style: str | None = None
    identity_background: str | None = None
    speaking_style: str | None = None
    knowledge_boundary: str | None = None
    output_mode: OutputMode = OutputMode.FREEFORM
    output_type: str | None = None
    output_schema: dict | None = None
    category: str = "自定义"
    business_domain: str | None = None
    applicable_scenarios: list[str] = Field(default_factory=list)
    usage_notes: str | None = None
    support_basis_summary: str | None = None
    ai_generation_note: str | None = None
