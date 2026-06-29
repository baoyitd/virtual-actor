"""角色外供包记录 ORM"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class RoleExportPackage(Base):
    __tablename__ = "role_export_packages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("role_assets.id"), nullable=False, index=True
    )
    role_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("role_versions.id"), nullable=False, index=True
    )
    package_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    generation_source_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    files: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    role: Mapped["RoleAsset"] = relationship(back_populates="export_packages")
    version: Mapped["RoleVersion"] = relationship(back_populates="export_packages")
