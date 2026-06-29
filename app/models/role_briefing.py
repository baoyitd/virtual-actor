"""角色版本说明卡当前保存版 ORM"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class RoleBriefing(Base):
    __tablename__ = "role_briefings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("role_versions.id"), nullable=False, unique=True, index=True
    )
    applicable_scenarios: Mapped[list | None] = mapped_column(JSON, default=list)
    usage_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    support_basis_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    source_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    last_generated_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    version: Mapped["RoleVersion"] = relationship(back_populates="briefing")
