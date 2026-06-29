"""v051 governance config tables

Revision ID: v051_governance_config
Revises: v05_role_workbench_foundation
Create Date: 2026-06-22

"""
from alembic import op
import sqlalchemy as sa


revision = "v051_governance_config"
down_revision = "v05_role_workbench_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "business_domains",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False, unique=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "enterprise_roles",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("business_domain_id", sa.String(length=36), sa.ForeignKey("business_domains.id"), nullable=False, index=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "staff_directory",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("department", sa.String(length=200), nullable=True),
        sa.Column("email", sa.String(length=200), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("staff_directory")
    op.drop_table("enterprise_roles")
    op.drop_table("business_domains")
