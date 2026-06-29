"""知识绑定表 ORM"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class KnowledgeRef(Base):
    __tablename__ = "knowledge_refs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role_id: Mapped[str] = mapped_column(String(36), ForeignKey("role_assets.id"), index=True)
    version_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("role_versions.id"), nullable=True, index=True
    )
    kb_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    knowledge_object_id: Mapped[str] = mapped_column(String(512), nullable=False)
    knowledge_version_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    knowledge_source: Mapped[str] = mapped_column(String(32), default="knowledge-platform")
    bound_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    role: Mapped["RoleAsset"] = relationship(back_populates="knowledge_refs")
    version: Mapped["RoleVersion | None"] = relationship(back_populates="knowledge_refs")


class ValidatedKnowledgeVersion(Base):
    """知识版本溯源表（上位裁决后的最小追溯结构）"""
    __tablename__ = "validated_knowledge_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id: Mapped[str] = mapped_column(String(36), ForeignKey("role_versions.id"), index=True)
    knowledge_object_id: Mapped[str] = mapped_column(String(256), nullable=False)
    knowledge_version_id: Mapped[str] = mapped_column(String(128), nullable=False)

    version: Mapped["RoleVersion"] = relationship(back_populates="validated_knowledge")
