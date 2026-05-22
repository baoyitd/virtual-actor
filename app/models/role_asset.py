"""角色主表 ORM"""
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, JSON, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class RoleAsset(Base):
    __tablename__ = "role_assets"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    bio: Mapped[str] = mapped_column(String(512), nullable=False)
    tags: Mapped[list | None] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="draft"
    )
    current_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # relationships
    versions: Mapped[list["RoleVersion"]] = relationship(back_populates="role", cascade="all, delete-orphan")
    knowledge_refs: Mapped[list["KnowledgeRef"]] = relationship(back_populates="role", cascade="all, delete-orphan")
    test_runs: Mapped[list["TestRunRecord"]] = relationship(back_populates="role", cascade="all, delete-orphan")