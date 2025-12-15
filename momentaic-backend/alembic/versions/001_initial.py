"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')
    
    # Create enum types
    op.execute("CREATE TYPE user_tier AS ENUM ('starter', 'growth', 'god_mode')")
    op.execute("CREATE TYPE startup_stage AS ENUM ('idea', 'mvp', 'pmf', 'scaling', 'mature')")
    op.execute("CREATE TYPE lead_status AS ENUM ('new', 'researching', 'outreach', 'replied', 'meeting', 'negotiation', 'won', 'lost')")
    op.execute("CREATE TYPE lead_source AS ENUM ('manual', 'linkedin', 'website', 'referral', 'conference', 'cold_outreach', 'inbound')")
    op.execute("CREATE TYPE content_platform AS ENUM ('linkedin', 'twitter', 'blog', 'newsletter', 'producthunt', 'hackernews')")
    op.execute("CREATE TYPE content_status AS ENUM ('idea', 'drafting', 'review', 'scheduled', 'published', 'archived')")
    op.execute("CREATE TYPE workflow_status AS ENUM ('draft', 'active', 'paused', 'archived')")
    op.execute("CREATE TYPE workflow_run_status AS ENUM ('pending', 'running', 'waiting_approval', 'completed', 'failed', 'cancelled')")
    op.execute("CREATE TYPE log_level AS ENUM ('debug', 'info', 'warning', 'error', 'success')")
    op.execute("CREATE TYPE approval_status AS ENUM ('pending', 'approved', 'rejected', 'expired')")
    op.execute("CREATE TYPE agent_type AS ENUM ('supervisor', 'sales_hunter', 'content_creator', 'tech_lead', 'finance_cfo', 'legal_counsel', 'growth_hacker', 'product_pm', 'general')")
    op.execute("CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system', 'tool')")
    op.execute("CREATE TYPE node_type AS ENUM ('trigger', 'ai', 'http', 'browser', 'code', 'human', 'condition', 'loop', 'transform', 'notification')")
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('tier', postgresql.ENUM('starter', 'growth', 'god_mode', name='user_tier', create_type=False), nullable=False, server_default='starter'),
        sa.Column('credits_balance', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('stripe_customer_id', sa.String(255)),
        sa.Column('stripe_subscription_id', sa.String(255)),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('github_token', sa.Text()),
        sa.Column('linkedin_token', sa.Text()),
        sa.Column('gmail_token', sa.Text()),
        sa.Column('preferences', postgresql.JSONB(), server_default='{}'),
        sa.Column('last_login_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Refresh tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Credit transactions table
    op.create_table(
        'credit_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('balance_after', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('reason', sa.String(255)),
        sa.Column('metadata', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_credit_transactions_user_created', 'credit_transactions', ['user_id', 'created_at'])
    
    # Startups table
    op.create_table(
        'startups',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('tagline', sa.String(500)),
        sa.Column('description', sa.Text()),
        sa.Column('industry', sa.String(100), index=True),
        sa.Column('stage', postgresql.ENUM('idea', 'mvp', 'pmf', 'scaling', 'mature', name='startup_stage', create_type=False), nullable=False, server_default='idea'),
        sa.Column('description_embedding', sa.dialects.postgresql.ARRAY(sa.Float())),
        sa.Column('metrics', postgresql.JSONB(), server_default='{}'),
        sa.Column('github_repo', sa.String(255)),
        sa.Column('website_url', sa.String(500)),
        sa.Column('settings', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Signals table
    op.create_table(
        'signals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tech_velocity', sa.Float(), server_default='50.0'),
        sa.Column('pmf_score', sa.Float(), server_default='50.0'),
        sa.Column('growth_momentum', sa.Float(), server_default='50.0'),
        sa.Column('runway_health', sa.Float(), server_default='50.0'),
        sa.Column('overall_score', sa.Float(), server_default='50.0'),
        sa.Column('raw_data', postgresql.JSONB(), server_default='{}'),
        sa.Column('ai_insights', sa.Text()),
        sa.Column('recommendations', postgresql.JSONB(), server_default='[]'),
        sa.Column('calculated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_signals_startup_calculated', 'signals', ['startup_id', 'calculated_at'])
    
    # Sprints table
    op.create_table(
        'sprints',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('goal', sa.Text(), nullable=False),
        sa.Column('key_results', postgresql.JSONB(), server_default='[]'),
        sa.Column('start_date', sa.Date()),
        sa.Column('end_date', sa.Date()),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('progress_percentage', sa.Integer(), server_default='0'),
        sa.Column('completed_results', postgresql.JSONB(), server_default='[]'),
        sa.Column('ai_feedback', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Standups table
    op.create_table(
        'standups',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('sprint_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sprints.id', ondelete='CASCADE'), nullable=False),
        sa.Column('yesterday', sa.Text()),
        sa.Column('today', sa.Text()),
        sa.Column('blockers', sa.Text()),
        sa.Column('mood', sa.String(20)),
        sa.Column('alignment_score', sa.Float()),
        sa.Column('ai_feedback', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Leads table
    op.create_table(
        'leads',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('company_name', sa.String(255), nullable=False),
        sa.Column('company_website', sa.String(500)),
        sa.Column('company_size', sa.String(50)),
        sa.Column('company_industry', sa.String(100)),
        sa.Column('contact_name', sa.String(255)),
        sa.Column('contact_title', sa.String(255)),
        sa.Column('contact_email', sa.String(255)),
        sa.Column('contact_linkedin', sa.String(500)),
        sa.Column('contact_phone', sa.String(50)),
        sa.Column('status', postgresql.ENUM('new', 'researching', 'outreach', 'replied', 'meeting', 'negotiation', 'won', 'lost', name='lead_status', create_type=False), nullable=False, server_default='new'),
        sa.Column('source', postgresql.ENUM('manual', 'linkedin', 'website', 'referral', 'conference', 'cold_outreach', 'inbound', name='lead_source', create_type=False), nullable=False, server_default='manual'),
        sa.Column('probability', sa.Integer(), server_default='0'),
        sa.Column('deal_value', sa.Float()),
        sa.Column('agent_state', postgresql.JSONB(), server_default='{}'),
        sa.Column('autopilot_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('research_data', postgresql.JSONB(), server_default='{}'),
        sa.Column('last_contacted_at', sa.DateTime()),
        sa.Column('next_followup_at', sa.DateTime()),
        sa.Column('notes', sa.Text()),
        sa.Column('tags', postgresql.JSONB(), server_default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_leads_startup_status', 'leads', ['startup_id', 'status'])
    op.create_index('ix_leads_autopilot', 'leads', ['autopilot_enabled'])
    
    # Outreach messages table
    op.create_table(
        'outreach_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('leads.id', ondelete='CASCADE'), nullable=False),
        sa.Column('channel', sa.String(50), nullable=False),
        sa.Column('subject', sa.String(500)),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('direction', sa.String(20), nullable=False, server_default='outbound'),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('ai_generated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('generation_prompt', sa.Text()),
        sa.Column('sent_at', sa.DateTime()),
        sa.Column('opened_at', sa.DateTime()),
        sa.Column('replied_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Content items table
    op.create_table(
        'content_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(500)),
        sa.Column('platform', postgresql.ENUM('linkedin', 'twitter', 'blog', 'newsletter', 'producthunt', 'hackernews', name='content_platform', create_type=False), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=False, server_default='post'),
        sa.Column('body', sa.Text()),
        sa.Column('hook', sa.Text()),
        sa.Column('cta', sa.Text()),
        sa.Column('hashtags', postgresql.JSONB(), server_default='[]'),
        sa.Column('media_urls', postgresql.JSONB(), server_default='[]'),
        sa.Column('status', postgresql.ENUM('idea', 'drafting', 'review', 'scheduled', 'published', 'archived', name='content_status', create_type=False), nullable=False, server_default='idea'),
        sa.Column('scheduled_for', sa.DateTime()),
        sa.Column('published_at', sa.DateTime()),
        sa.Column('published_url', sa.String(500)),
        sa.Column('ai_generated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('generation_context', postgresql.JSONB(), server_default='{}'),
        sa.Column('metrics', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_content_startup_platform', 'content_items', ['startup_id', 'platform'])
    op.create_index('ix_content_status', 'content_items', ['status'])
    op.create_index('ix_content_scheduled', 'content_items', ['scheduled_for'])
    
    # Workflows table
    op.create_table(
        'workflows',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('nodes', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('edges', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('trigger_type', sa.String(50), nullable=False, server_default='manual'),
        sa.Column('trigger_config', postgresql.JSONB(), server_default='{}'),
        sa.Column('webhook_url', sa.String(100), unique=True, index=True),
        sa.Column('status', postgresql.ENUM('draft', 'active', 'paused', 'archived', name='workflow_status', create_type=False), nullable=False, server_default='draft'),
        sa.Column('run_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('success_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Workflow runs table
    op.create_table(
        'workflow_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workflows.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'running', 'waiting_approval', 'completed', 'failed', 'cancelled', name='workflow_run_status', create_type=False), nullable=False, server_default='pending'),
        sa.Column('current_node_id', sa.String(100)),
        sa.Column('inputs', postgresql.JSONB(), server_default='{}'),
        sa.Column('outputs', postgresql.JSONB(), server_default='{}'),
        sa.Column('context', postgresql.JSONB(), server_default='{}'),
        sa.Column('error_message', sa.Text()),
        sa.Column('error_node_id', sa.String(100)),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_workflow_runs_workflow_status', 'workflow_runs', ['workflow_id', 'status'])
    
    # Workflow logs table
    op.create_table(
        'workflow_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workflow_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('node_id', sa.String(100)),
        sa.Column('level', postgresql.ENUM('debug', 'info', 'warning', 'error', 'success', name='log_level', create_type=False), nullable=False, server_default='info'),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), server_default='{}'),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_workflow_logs_run_timestamp', 'workflow_logs', ['run_id', 'timestamp'])
    
    # Workflow approvals table
    op.create_table(
        'workflow_approvals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workflow_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('node_id', sa.String(100), nullable=False),
        sa.Column('node_label', sa.String(255)),
        sa.Column('description', sa.Text()),
        sa.Column('content', postgresql.JSONB(), server_default='{}'),
        sa.Column('status', postgresql.ENUM('pending', 'approved', 'rejected', 'expired', name='approval_status', create_type=False), nullable=False, server_default='pending'),
        sa.Column('priority', sa.String(20), server_default='medium'),
        sa.Column('decision_by', postgresql.UUID(as_uuid=True)),
        sa.Column('decision_feedback', sa.Text()),
        sa.Column('decided_at', sa.DateTime()),
        sa.Column('expires_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_workflow_approvals_status', 'workflow_approvals', ['status'])
    
    # Conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255)),
        sa.Column('agent_type', postgresql.ENUM('supervisor', 'sales_hunter', 'content_creator', 'tech_lead', 'finance_cfo', 'legal_counsel', 'growth_hacker', 'product_pm', 'general', name='agent_type', create_type=False), nullable=False, server_default='supervisor'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('message_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('context', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_conversations_startup_user', 'conversations', ['startup_id', 'user_id'])
    op.create_index('ix_conversations_active', 'conversations', ['is_active'])
    
    # Messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', postgresql.ENUM('user', 'assistant', 'system', 'tool', name='message_role', create_type=False), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('agent_type', postgresql.ENUM('supervisor', 'sales_hunter', 'content_creator', 'tech_lead', 'finance_cfo', 'legal_counsel', 'growth_hacker', 'product_pm', 'general', name='agent_type', create_type=False)),
        sa.Column('tool_calls', postgresql.JSONB(), server_default='[]'),
        sa.Column('tool_results', postgresql.JSONB(), server_default='{}'),
        sa.Column('metadata', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])
    
    # Agent memory table
    op.create_table(
        'agent_memory',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('agent_type', postgresql.ENUM('supervisor', 'sales_hunter', 'content_creator', 'tech_lead', 'finance_cfo', 'legal_counsel', 'growth_hacker', 'product_pm', 'general', name='agent_type', create_type=False), nullable=False),
        sa.Column('memory_type', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('importance', sa.Integer(), server_default='5'),
        sa.Column('source_conversation_id', postgresql.UUID(as_uuid=True)),
        sa.Column('source_message_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_accessed_at', sa.DateTime()),
        sa.Column('access_count', sa.Integer(), server_default='0'),
    )
    op.create_index('ix_agent_memory_startup_agent', 'agent_memory', ['startup_id', 'agent_type'])
    op.create_index('ix_agent_memory_importance', 'agent_memory', ['importance'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('agent_memory')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('workflow_approvals')
    op.drop_table('workflow_logs')
    op.drop_table('workflow_runs')
    op.drop_table('workflows')
    op.drop_table('content_items')
    op.drop_table('outreach_messages')
    op.drop_table('leads')
    op.drop_table('standups')
    op.drop_table('sprints')
    op.drop_table('signals')
    op.drop_table('startups')
    op.drop_table('credit_transactions')
    op.drop_table('refresh_tokens')
    op.drop_table('users')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS node_type')
    op.execute('DROP TYPE IF EXISTS message_role')
    op.execute('DROP TYPE IF EXISTS agent_type')
    op.execute('DROP TYPE IF EXISTS approval_status')
    op.execute('DROP TYPE IF EXISTS log_level')
    op.execute('DROP TYPE IF EXISTS workflow_run_status')
    op.execute('DROP TYPE IF EXISTS workflow_status')
    op.execute('DROP TYPE IF EXISTS content_status')
    op.execute('DROP TYPE IF EXISTS content_platform')
    op.execute('DROP TYPE IF EXISTS lead_source')
    op.execute('DROP TYPE IF EXISTS lead_status')
    op.execute('DROP TYPE IF EXISTS startup_stage')
    op.execute('DROP TYPE IF EXISTS user_tier')
