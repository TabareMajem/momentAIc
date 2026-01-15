"""add action items table

Revision ID: 20260108_080000_28a1c68e1234
Revises: ba37d68a3704
Create Date: 2026-01-08 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260108_080000_28a1c68e1234'
down_revision = 'ba37d68a3704'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Action Status Enum
    # Types will be created automatically by sa.Enum(name=...)
    pass

    # Metrics table
    op.create_table('action_items',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('startup_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('source_agent', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='actionpriority'), nullable=True),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('status', sa.Enum('pending', 'approved', 'rejected', 'executed', 'failed', name='actionstatus'), nullable=True),
    sa.Column('execution_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['startup_id'], ['startups.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_action_items_created_at', 'action_items', ['created_at'], unique=False)
    op.create_index('ix_action_items_startup_status', 'action_items', ['startup_id', 'status'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_action_items_startup_status', table_name='action_items')
    op.drop_index('ix_action_items_created_at', table_name='action_items')
    op.drop_table('action_items')
    # Types are dropped automatically if script was generated correctly, or we can drop explicitly if needed.
    # But usually creating table with Enum(name) binds the type to table? 
    # Actually explicit drop is safer for Enums in Postgres. keep it but use execute.
    op.execute("DROP TYPE actionstatus")
    op.execute("DROP TYPE actionpriority")
