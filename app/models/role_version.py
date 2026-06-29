"""角色版本表 ORM"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class RoleVersion(Base):
    __tablename__ = "role_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role_id: Mapped[str] = mapped_column(String(36), ForeignKey("role_assets.id"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    published_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_deprecated: Mapped[bool] = mapped_column(Boolean, default=False)
    change_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    role: Mapped["RoleAsset"] = relationship(back_populates="versions")
    fields: Mapped[list["RoleVersionField"]] = relationship(
        back_populates="version", cascade="all, delete-orphan"
    )
    knowledge_refs: Mapped[list["KnowledgeRef"]] = relationship(
        back_populates="version", cascade="all, delete-orphan"
    )
    validated_knowledge: Mapped[list["ValidatedKnowledgeVersion"]] = relationship(
        back_populates="version", cascade="all, delete-orphan"
    )
    briefing: Mapped["RoleBriefing | None"] = relationship(
        back_populates="version", cascade="all, delete-orphan", uselist=False
    )
    export_packages: Mapped[list["RoleExportPackage"]] = relationship(
        back_populates="version", cascade="all, delete-orphan"
    )


class RoleVersionField(Base):
    """版本字段快照（EAV 模式）"""
    __tablename__ = "role_version_fields"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id: Mapped[str] = mapped_column(String(36), ForeignKey("role_versions.id"), nullable=False, index=True)
    layer: Mapped[str] = mapped_column(String(4), nullable=False)
    field_name: Mapped[str] = mapped_column(String(64), nullable=False)
    field_value: Mapped[dict] = mapped_column(JSON, nullable=False)

    version: Mapped["RoleVersion"] = relationship(back_populates="fields")
