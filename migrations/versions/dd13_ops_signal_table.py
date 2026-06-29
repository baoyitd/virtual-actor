"""DD-13 ops_signals table — 记录无匹配推荐意图作为运营信号

Revision ID: dd13_ops_signal
Revises: v04_data_foundation
Create Date: 2026-05-27

"""
from alembic import op
import sqlalchemy as sa


revision = 'dd13_ops_signal'
down_revision = 'v04_data_foundation'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'ops_signals',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('intent', sa.Text, nullable=False),
        sa.Column('intent_summary', sa.Text, nullable=False),
        sa.Column('category', sa.String(32), nullable=True),
        sa.Column('business_domain', sa.String(64), nullable=True),
        sa.Column('matched_output_type', sa.String(64), nullable=True),
        sa.Column('signal_type', sa.String(32), nullable=False, server_default='no_role_match'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('ops_signals')