"""数据资产管理相关 Schema"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DataAssetCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=128)
    datasource_ref: str = Field(min_length=1, max_length=128)
    database_name: str = Field(min_length=1, max_length=128)
    table_name: str = Field(min_length=1, max_length=128)
    scope_summary: str = Field(min_length=1, max_length=512)
    freshness: str | None = Field(default=None, max_length=64)
    owner_team: str | None = Field(default=None, max_length=128)


class DataAssetUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=128)
    datasource_ref: str | None = Field(default=None, min_length=1, max_length=128)
    database_name: str | None = Field(default=None, min_length=1, max_length=128)
    table_name: str | None = Field(default=None, min_length=1, max_length=128)
    scope_summary: str | None = Field(default=None, min_length=1, max_length=512)
    freshness: str | None = Field(default=None, max_length=64)
    owner_team: str | None = Field(default=None, max_length=128)
    status: str | None = Field(default=None, max_length=16)


class DataAssetOut(BaseModel):
    id: str
    display_name: str
    datasource_ref: str
    database_name: str
    table_name: str
    scope_summary: str
    freshness: str | None = None
    owner_team: str | None = None
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
