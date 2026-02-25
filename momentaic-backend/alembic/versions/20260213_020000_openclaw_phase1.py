"""Add heartbeat_ledger and agent_messages tables (OpenClaw Phase 1)

Revision ID: 20260213_020000_openclaw_phase1
Revises: 20260108_080000_28a1c68e1234_add_action_items
Create Date: 2026-02-13 02:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '20260213_020000_openclaw_phase1'
down_revision = 'bd78173abb1b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP TYPE IF EXISTS heartbeatresult, a2amessagetype, messagepriority, messagestatus CASCADE;")
    op.execute("DROP TABLE IF EXISTS heartbeat_ledger CASCADE;")
    op.execute("DROP TABLE IF EXISTS agent_messages CASCADE;")
    
    # === Heartbeat Ledger ===
    op.create_table(
        'heartbeat_ledger',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('agent_id', sa.String(100), nullable=False),
        sa.Column('heartbeat_timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('result_type', sa.String(50), nullable=False),
        sa.Column('checklist_item', sa.String(200), nullable=True),
        sa.Column('context_snapshot', JSONB, nullable=True),
        sa.Column('action_taken', sa.Text, nullable=True),
        sa.Column('action_result', JSONB, nullable=True),
        sa.Column('tokens_used', sa.Integer, server_default='0', nullable=False),
        sa.Column('cost_usd', sa.Float, server_default='0.0', nullable=False),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('latency_ms', sa.Integer, server_default='0', nullable=False),
        sa.Column('founder_notified', sa.Boolean, server_default='false', nullable=False),
        sa.Column('founder_response', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_hb_startup_agent', 'heartbeat_ledger', ['startup_id', 'agent_id'])
    op.create_index('ix_hb_result_type', 'heartbeat_ledger', ['result_type'])
    op.create_index('ix_hb_timestamp', 'heartbeat_ledger', ['heartbeat_timestamp'])
    op.create_index('ix_hb_startup_ts', 'heartbeat_ledger', ['startup_id', 'heartbeat_timestamp'])

    # === Agent Messages (A2A Protocol) ===
    op.create_table(
        'agent_messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('message_type', sa.String(50), nullable=False),
        sa.Column('from_agent', sa.String(100), nullable=False),
        sa.Column('to_agent', sa.String(100), nullable=True),
        sa.Column('topic', sa.String(200), nullable=False),
        sa.Column('priority', sa.String(50), nullable=False, server_default='medium'),
        sa.Column('payload', JSONB, nullable=False, server_default='{}'),
        sa.Column('thread_id', UUID(as_uuid=True), nullable=True),
        sa.Column('parent_message_id', UUID(as_uuid=True), sa.ForeignKey('agent_messages.id'), nullable=True),
        sa.Column('requires_response', sa.Boolean, server_default='false', nullable=False),
        sa.Column('response_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('response_received', sa.Boolean, server_default='false', nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('resolution', JSONB, nullable=True),
        sa.Column('escalated_to_founder', sa.Boolean, server_default='false', nullable=False),
        sa.Column('founder_decision', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_a2a_startup_to', 'agent_messages', ['startup_id', 'to_agent'])
    op.create_index('ix_a2a_startup_from', 'agent_messages', ['startup_id', 'from_agent'])
    op.create_index('ix_a2a_topic', 'agent_messages', ['topic'])
    op.create_index('ix_a2a_thread', 'agent_messages', ['thread_id'])
    op.create_index('ix_a2a_status', 'agent_messages', ['status'])
    op.create_index('ix_a2a_created', 'agent_messages', ['created_at'])


def downgrade() -> None:
    op.drop_table('agent_messages')
    op.drop_table('heartbeat_ledger')
    op.execute("DROP TYPE IF EXISTS heartbeatresult")
    op.execute("DROP TYPE IF EXISTS a2amessagetype")
    op.execute("DROP TYPE IF EXISTS messagepriority")
    op.execute("DROP TYPE IF EXISTS messagestatus")
