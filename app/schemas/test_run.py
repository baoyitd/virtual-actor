"""测试记录 Pydantic Schema"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TestRunCreate(BaseModel):
    test_input: str = Field(min_length=1)


class TestRunOut(BaseModel):
    id: str
    role_id: str
    version_id: str | None = None
    test_input: str
    test_output: str
    knowledge_retrieved: list[dict] | None = None
    human_rating: int | None = None
    tested_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TestRunRating(BaseModel):
    human_rating: int = Field(ge=1, le=5)
