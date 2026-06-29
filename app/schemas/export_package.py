"""外供包相关 Schema"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ExportPackageType(str, Enum):
    TOOL = "tool"
    SKILL = "skill"


class ExportFileOut(BaseModel):
    path: str
    content: str


class ExportPackageOut(BaseModel):
    package_id: str
    package_type: ExportPackageType
    role_id: str
    role_version_id: str
    is_stale: bool
    created_at: datetime | None = None
    files: list[ExportFileOut] = Field(default_factory=list)
    stale_reason: str | None = None
