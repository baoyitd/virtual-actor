"""统一消费 API + test-consume 相关 Schema"""
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.role import ConsumeStatus, CallerType


# ── 消费请求 ──

class ConsumeRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2048)
    context: str | None = Field(default=None, max_length=4096)
    caller_type: CallerType | None = None
    caller_id: str | None = Field(default=None, max_length=128)
    role_version_id: str | None = None
    output_type: str | None = None


class TestConsumeRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2048)
    context: str | None = Field(default=None, max_length=4096)
    caller_id: str | None = Field(default=None, max_length=128)
    role_version_id: str | None = None
    output_type: str | None = None


# ── 消费响应（固定治理外壳） ──

class ConsumeResponse(BaseModel):
    status: ConsumeStatus
    status_reason: str
    answer: str
    boundary_status: dict
    structured_result: dict
    output_type: str | None
    sources: list[dict]
    role_id: str
    role_version_id: str
    usage_record_id: str
    created_at: datetime


class TestConsumeResponse(BaseModel):
    """test-consume 输出：字段对齐 consume API，但 usage_record_id 替换为 validation_record_id"""
    status: ConsumeStatus
    status_reason: str
    answer: str
    boundary_status: dict
    structured_result: dict
    output_type: str | None
    sources: list[dict]
    role_id: str
    role_version_id: str
    validation_record_id: str
    created_at: datetime


class TestValidationRecordOut(BaseModel):
    validation_record_id: str
    role_id: str
    role_version_id: str
    query: str
    context: str | None
    answer: str
    structured_result: dict | None
    output_type: str | None
    status: ConsumeStatus
    status_reason: str
    boundary_status: dict | None
    sources: list[dict]
    created_at: datetime | None


# ── 消费记录查询 ──

class ConsumeRecordOut(BaseModel):
    id: str
    role_asset_id: str
    role_version_id: str
    caller_id: str | None
    caller_type: str
    query: str
    context: str | None
    answer: str
    structured_result: dict | None
    output_type: str | None
    status: str
    status_reason: str | None
    boundary_status: dict | None
    sources: list | None
    created_at: datetime | None


class ConsumeRecordListQuery(BaseModel):
    status: ConsumeStatus | None = None
    caller_type: CallerType | None = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
