"""add_empire_progress

Revision ID: 20260115_184500_ee1e12345678
Revises: 20260108_080000_28a1c68e1234
Create Date: 2026-01-15 18:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '20260115_184500_ee1e12345678'
down_revision = '20260108_080000_28a1c68e1234'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'empire_progress',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('current_step', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('step_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_empire_progress_user', 'empire_progress', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_empire_progress_user', table_name='empire_progress')
    op.drop_table('empire_progress')
