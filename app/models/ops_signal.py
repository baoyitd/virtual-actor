"""运营信号 ORM — 记录无匹配推荐意图"""
import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class OpsSignal(Base):
    __tablename__ = "ops_signals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    intent: Mapped[str] = mapped_column(Text, nullable=False)
    intent_summary: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(32), nullable=True)
    business_domain: Mapped[str | None] = mapped_column(String(64), nullable=True)
    matched_output_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    signal_type: Mapped[str] = mapped_column(String(32), nullable=False, default="no_role_match")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())