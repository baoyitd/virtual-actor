"""v0.5 role workbench foundation

Revision ID: v05_role_workbench_foundation
Revises: dd13_ops_signal
Create Date: 2026-06-10

"""
from alembic import op
import sqlalchemy as sa


revision = "v05_role_workbench_foundation"
down_revision = "dd13_ops_signal"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "role_assets",
        sa.Column("enterprise_role_mapping", sa.JSON(), nullable=True),
    )
    op.execute(
        """
        UPDATE role_assets
        SET enterprise_role_mapping = JSON_ARRAY()
        WHERE enterprise_role_mapping IS NULL
        """
    )
    op.alter_column(
        "role_assets",
        "enterprise_role_mapping",
        existing_type=sa.JSON(),
        nullable=False,
    )

    op.add_column("knowledge_refs", sa.Column("version_id", sa.String(length=36), nullable=True))
    op.create_index(op.f("ix_knowledge_refs_version_id"), "knowledge_refs", ["version_id"], unique=False)
    op.create_foreign_key(
        "fk_knowledge_refs_version_id_role_versions",
        "knowledge_refs",
        "role_versions",
        ["version_id"],
        ["id"],
    )
    op.execute(
        """
        UPDATE knowledge_refs kr
        JOIN role_assets ra ON ra.id = kr.role_id
        SET kr.version_id = ra.current_version_id
        WHERE kr.version_id IS NULL
        """
    )

    op.create_table(
        "data_assets",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("datasource_ref", sa.String(length=128), nullable=False),
        sa.Column("database_name", sa.String(length=128), nullable=False),
        sa.Column("table_name", sa.String(length=128), nullable=False),
        sa.Column("scope_summary", sa.String(length=512), nullable=False),
        sa.Column("freshness", sa.String(length=64), nullable=True),
        sa.Column("owner_team", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_data_assets_status"), "data_assets", ["status"], unique=False)

    op.create_table(
        "role_briefings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("version_id", sa.String(length=36), sa.ForeignKey("role_versions.id"), nullable=False, unique=True),
        sa.Column("applicable_scenarios", sa.JSON(), nullable=True),
        sa.Column("usage_notes", sa.Text(), nullable=False),
        sa.Column("support_basis_summary", sa.Text(), nullable=False),
        sa.Column("source_hash", sa.String(length=64), nullable=False),
        sa.Column("last_generated_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_role_briefings_source_hash"), "role_briefings", ["source_hash"], unique=False)
    op.create_index(op.f("ix_role_briefings_version_id"), "role_briefings", ["version_id"], unique=True)

    op.create_table(
        "role_export_packages",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("role_id", sa.String(length=36), sa.ForeignKey("role_assets.id"), nullable=False),
        sa.Column("role_version_id", sa.String(length=36), sa.ForeignKey("role_versions.id"), nullable=False),
        sa.Column("package_type", sa.String(length=16), nullable=False),
        sa.Column("generation_source_hash", sa.String(length=64), nullable=False),
        sa.Column("files", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_role_export_packages_role_id"), "role_export_packages", ["role_id"], unique=False)
    op.create_index(
        op.f("ix_role_export_packages_role_version_id"),
        "role_export_packages",
        ["role_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_role_export_packages_package_type"),
        "role_export_packages",
        ["package_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_role_export_packages_package_type"), table_name="role_export_packages")
    op.drop_index(op.f("ix_role_export_packages_role_version_id"), table_name="role_export_packages")
    op.drop_index(op.f("ix_role_export_packages_role_id"), table_name="role_export_packages")
    op.drop_table("role_export_packages")

    op.drop_index(op.f("ix_role_briefings_version_id"), table_name="role_briefings")
    op.drop_index(op.f("ix_role_briefings_source_hash"), table_name="role_briefings")
    op.drop_table("role_briefings")

    op.drop_index(op.f("ix_data_assets_status"), table_name="data_assets")
    op.drop_table("data_assets")

    op.drop_constraint("fk_knowledge_refs_version_id_role_versions", "knowledge_refs", type_="foreignkey")
    op.drop_index(op.f("ix_knowledge_refs_version_id"), table_name="knowledge_refs")
    op.drop_column("knowledge_refs", "version_id")

    op.drop_column("role_assets", "enterprise_role_mapping")
