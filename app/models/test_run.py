"""测试记录表 ORM"""
import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class TestRunRecord(Base):
    __tablename__ = "test_run_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role_id: Mapped[str] = mapped_column(String(36), ForeignKey("role_assets.id"), index=True)
    version_id: Mapped[str] = mapped_column(String(36), ForeignKey("role_versions.id"), nullable=True)
    test_input: Mapped[str] = mapped_column(Text, nullable=False)
    test_output: Mapped[str] = mapped_column(Text, nullable=False)
    knowledge_retrieved: Mapped[list | None] = mapped_column(JSON, nullable=True)
    human_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tested_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    role: Mapped["RoleAsset"] = relationship(back_populates="test_runs")