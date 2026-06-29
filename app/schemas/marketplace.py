"""资产市场推荐 Schema — DD-13 推荐链路升级

4 类结果区分:
  matched       — 业务意图匹配到角色，返回推荐列表
  no_match      — 意象在业务范围内但当前角色池无覆盖，记录 OpsSignal
  out_of_scope  — 需求超出企业正常业务决策场景范围，不记录 OpsSignal
  service_error — 推荐服务自身故障，不记录 OpsSignal
"""
from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    """AI 推荐请求 — 用户业务意图"""
    intent: str = Field(min_length=1, max_length=2048, description="业务意图描述")
    category: str | None = None
    business_domain: str | None = None


class RecommendItem(BaseModel):
    """单条推荐结果"""
    role_id: str
    role_version_id: str | None = None
    role_name: str
    bio: str
    recommendation_reason: str
    reason_summary: str
    reason_evidence: list[str] = Field(default_factory=list)
    matched_dimensions: list[str] = Field(default_factory=list)
    caution: str | None = None
    applicable_problems: list[str] = Field(default_factory=list)
    applicable_scenarios_label: str
    output_type: str | None = None
    knowledge_boundary: str | None = None
    capability_level: str | None = None
    version_number: int | None = None
    version_status: str | None = None
    tags: list[str] = Field(default_factory=list)
    match_score: float | None = None


class RecommendResponse(BaseModel):
    """AI 推荐结果 — 4 类结果区分

    result_type:
      matched       — matched=true, recommendations 非空
      no_match      — matched=false, 意象在业务范围但角色池无覆盖，记录 OpsSignal
      out_of_scope  — matched=false, 需求超出企业业务场景范围，不记录 OpsSignal
      service_error — matched=false, 推荐服务自身故障，不记录 OpsSignal
    """
    matched: bool
    result_type: str = "matched"  # matched | no_match | out_of_scope | service_error
    recommendations: list[RecommendItem] = Field(default_factory=list)
    unmatched_intent_summary: str | None = None
    service_error_message: str | None = None
