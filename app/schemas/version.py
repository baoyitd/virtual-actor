"""版本相关 Pydantic Schema"""
from datetime import datetime
from pydantic import BaseModel


class PublishedVersionOut(BaseModel):
    """GET /role-assets/{role_id}/published-version 返回"""
    role_id: str
    role_version_id: str
    published_at: datetime | None = None
    published_by: str | None = None


class VersionListItem(BaseModel):
    """GET /role-assets/{role_id}/versions 返回"""
    role_version_id: str
    version_number: int
    status: str
    published_at: datetime | None = None

    class Config:
        from_attributes = True