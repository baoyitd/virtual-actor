"""add_kb_id_to_knowledge_refs

Revision ID: 7d6b4f4bfe22
Revises: f46e333b3e81
Create Date: 2026-05-22 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.config import settings


# revision identifiers, used by Alembic.
revision: str = "7d6b4f4bfe22"
down_revision: Union[str, Sequence[str], None] = "f46e333b3e81"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("knowledge_refs", sa.Column("kb_id", sa.String(length=128), nullable=True))
    op.execute(
        sa.text("UPDATE knowledge_refs SET kb_id = :kb_id WHERE kb_id IS NULL").bindparams(
            kb_id=settings.KNOWLEDGE_DEFAULT_KB_ID
        )
    )
    op.alter_column("knowledge_refs", "kb_id", existing_type=sa.String(length=128), nullable=False)
    op.create_index(op.f("ix_knowledge_refs_kb_id"), "knowledge_refs", ["kb_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_knowledge_refs_kb_id"), table_name="knowledge_refs")
    op.drop_column("knowledge_refs", "kb_id")
