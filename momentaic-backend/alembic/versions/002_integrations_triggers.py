"""Add integrations and triggers tables

Revision ID: 002_integrations_triggers
Revises: 001_initial
Create Date: 2024-12-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002_integrations_triggers'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Integrations table
    op.create_table(
        'integrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('access_token', sa.Text, nullable=True),
        sa.Column('refresh_token', sa.Text, nullable=True),
        sa.Column('token_expires_at', sa.DateTime, nullable=True),
        sa.Column('api_key', sa.Text, nullable=True),
        sa.Column('api_secret', sa.Text, nullable=True),
        sa.Column('config', postgresql.JSONB, server_default='{}'),
        sa.Column('scopes', postgresql.JSONB, server_default='[]'),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('last_sync_at', sa.DateTime, nullable=True),
        sa.Column('last_error', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_integrations_startup', 'integrations', ['startup_id'])
    op.create_index('ix_integrations_provider', 'integrations', ['provider'])
    op.create_index('ix_integrations_status', 'integrations', ['status'])

    # Integration data table
    op.create_table(
        'integration_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('integration_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('integrations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('data_type', sa.String(100), nullable=False),
        sa.Column('data', postgresql.JSONB, server_default='{}'),
        sa.Column('metric_value', sa.Float, nullable=True),
        sa.Column('metric_date', sa.DateTime, nullable=True),
        sa.Column('external_id', sa.String(500), nullable=True),
        sa.Column('synced_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_integration_data_startup', 'integration_data', ['startup_id'])
    op.create_index('ix_integration_data_category', 'integration_data', ['category'])
    op.create_index('ix_integration_data_type', 'integration_data', ['data_type'])
    op.create_index('ix_integration_data_date', 'integration_data', ['metric_date'])

    # Trigger rules table
    op.create_table(
        'trigger_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('trigger_type', sa.String(20), nullable=False),
        sa.Column('condition', postgresql.JSONB, server_default='{}'),
        sa.Column('action', postgresql.JSONB, server_default='{}'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('is_paused', sa.Boolean, server_default='false'),
        sa.Column('last_evaluated_at', sa.DateTime, nullable=True),
        sa.Column('last_triggered_at', sa.DateTime, nullable=True),
        sa.Column('trigger_count', sa.Integer, server_default='0'),
        sa.Column('cooldown_minutes', sa.Integer, server_default='60'),
        sa.Column('max_triggers_per_day', sa.Integer, server_default='10'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_trigger_rules_startup', 'trigger_rules', ['startup_id'])
    op.create_index('ix_trigger_rules_type', 'trigger_rules', ['trigger_type'])
    op.create_index('ix_trigger_rules_active', 'trigger_rules', ['is_active'])

    # Trigger logs table
    op.create_table(
        'trigger_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('trigger_rules.id', ondelete='CASCADE'), nullable=False),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(30), server_default='triggered'),
        sa.Column('trigger_context', postgresql.JSONB, server_default='{}'),
        sa.Column('agent_response', postgresql.JSONB, nullable=True),
        sa.Column('requires_approval', sa.Boolean, server_default='false'),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime, nullable=True),
        sa.Column('approval_notes', sa.Text, nullable=True),
        sa.Column('error', sa.Text, nullable=True),
        sa.Column('triggered_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_trigger_logs_rule', 'trigger_logs', ['rule_id'])
    op.create_index('ix_trigger_logs_status', 'trigger_logs', ['status'])
    op.create_index('ix_trigger_logs_triggered', 'trigger_logs', ['triggered_at'])

    # Agent actions table
    op.create_table(
        'agent_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('trigger_log_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('trigger_logs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('agent_type', sa.String(50), nullable=False),
        sa.Column('action_type', sa.String(100), nullable=False),
        sa.Column('action_data', postgresql.JSONB, server_default='{}'),
        sa.Column('success', sa.Boolean, server_default='false'),
        sa.Column('result', postgresql.JSONB, nullable=True),
        sa.Column('error', sa.Text, nullable=True),
        sa.Column('requires_approval', sa.Boolean, server_default='false'),
        sa.Column('approved', sa.Boolean, nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('executed_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_agent_actions_startup', 'agent_actions', ['startup_id'])
    op.create_index('ix_agent_actions_type', 'agent_actions', ['action_type'])
    op.create_index('ix_agent_actions_pending', 'agent_actions', ['requires_approval', 'approved'])


def downgrade() -> None:
    op.drop_table('agent_actions')
    op.drop_table('trigger_logs')
    op.drop_table('trigger_rules')
    op.drop_table('integration_data')
    op.drop_table('integrations')
