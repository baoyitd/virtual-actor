"""使用记录 ORM — consume API 正式消费记录"""
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    role_asset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("role_assets.id"), nullable=False, index=True
    )
    role_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("role_versions.id"), nullable=False
    )
    caller_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    caller_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default="human"
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    structured_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    status_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    boundary_status: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sources: Mapped[list | None] = mapped_column(JSON, nullable=True)
    knowledge_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )

    role: Mapped["RoleAsset"] = relationship(back_populates="usage_records")