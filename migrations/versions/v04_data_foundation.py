"""v0.4 data foundation: role_assets governance columns + usage_records + test_validation_records

Revision ID: v04_data_foundation
Revises: 7d6b4f4bfe22
Create Date: 2026-05-26

"""
from alembic import op
import sqlalchemy as sa


revision = 'v04_data_foundation'
down_revision = '7d6b4f4bfe22'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. role_assets: add 6 governance columns
    op.add_column('role_assets', sa.Column('category', sa.String(32), nullable=False, server_default='自定义'))
    op.add_column('role_assets', sa.Column('owner', sa.String(64), nullable=False, server_default='system'))
    op.add_column('role_assets', sa.Column('maintainer', sa.String(64), nullable=True))
    op.add_column('role_assets', sa.Column('business_domain', sa.String(64), nullable=True))
    op.add_column('role_assets', sa.Column('visibility', sa.String(16), nullable=False, server_default='内部'))
    op.add_column('role_assets', sa.Column('creation_source', sa.String(16), nullable=False, server_default='manual'))

    # Backfill owner for existing rows
    op.execute("UPDATE role_assets SET owner = 'system' WHERE owner IS NULL OR owner = ''")

    # 2. usage_records table (consume API formal consumption records)
    op.create_table(
        'usage_records',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('role_asset_id', sa.String(36), sa.ForeignKey('role_assets.id'), nullable=False, index=True),
        sa.Column('role_version_id', sa.String(36), sa.ForeignKey('role_versions.id'), nullable=False),
        sa.Column('caller_id', sa.String(128), nullable=True),
        sa.Column('caller_type', sa.String(32), nullable=False, server_default='human'),
        sa.Column('query', sa.Text, nullable=False),
        sa.Column('context', sa.Text, nullable=True),
        sa.Column('answer', sa.Text, nullable=False),
        sa.Column('structured_result', sa.JSON, nullable=True),
        sa.Column('output_type', sa.String(64), nullable=True),
        sa.Column('status', sa.String(32), nullable=False),
        sa.Column('status_reason', sa.String(512), nullable=True),
        sa.Column('boundary_status', sa.JSON, nullable=True),
        sa.Column('sources', sa.JSON, nullable=True),
        sa.Column('knowledge_snapshot', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), index=True),
    )
    op.create_index('ix_usage_records_status', 'usage_records', ['status'])

    # 3. test_validation_records table (test-consume internal verification records)
    op.create_table(
        'test_validation_records',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('role_asset_id', sa.String(36), sa.ForeignKey('role_assets.id'), nullable=False, index=True),
        sa.Column('role_version_id', sa.String(36), sa.ForeignKey('role_versions.id'), nullable=False),
        sa.Column('caller_id', sa.String(128), nullable=True),
        sa.Column('caller_type', sa.String(32), nullable=False, server_default='human'),
        sa.Column('query', sa.Text, nullable=False),
        sa.Column('context', sa.Text, nullable=True),
        sa.Column('answer', sa.Text, nullable=False),
        sa.Column('structured_result', sa.JSON, nullable=True),
        sa.Column('output_type', sa.String(64), nullable=True),
        sa.Column('status', sa.String(32), nullable=False),
        sa.Column('status_reason', sa.String(512), nullable=True),
        sa.Column('boundary_status', sa.JSON, nullable=True),
        sa.Column('sources', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('test_validation_records')
    op.drop_index('ix_usage_records_status', 'usage_records')
    op.drop_table('usage_records')
    op.drop_column('role_assets', 'creation_source')
    op.drop_column('role_assets', 'visibility')
    op.drop_column('role_assets', 'business_domain')
    op.drop_column('role_assets', 'maintainer')
    op.drop_column('role_assets', 'owner')
    op.drop_column('role_assets', 'category')