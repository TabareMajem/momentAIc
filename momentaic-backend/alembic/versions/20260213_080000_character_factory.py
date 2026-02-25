"""Add characters and character_content tables (AI Character Factory)

Revision ID: 20260213_080000_character_factory
Revises: 20260213_020000_openclaw_phase1
Create Date: 2026-02-13 08:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = '20260213_080000_char_factory'
down_revision = '20260213_020000_openclaw_phase1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS character_content CASCADE;")
    op.execute("DROP TABLE IF EXISTS characters CASCADE;")
    
    # === Characters ===
    op.create_table(
        'characters',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('handle', sa.String(100), nullable=True),
        sa.Column('tagline', sa.String(200), nullable=True),
        sa.Column('persona', JSONB, nullable=False, server_default='{}'),
        sa.Column('visual_identity', JSONB, nullable=False, server_default='{}'),
        sa.Column('voice_identity', JSONB, nullable=True),
        sa.Column('character_dna', sa.Text, nullable=True),
        sa.Column('platforms', JSONB, nullable=False, server_default='{}'),
        sa.Column('funnel_config', JSONB, nullable=True),
        sa.Column('content_rules', JSONB, nullable=True),
        sa.Column('performance_metrics', JSONB, nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('autonomy_level', sa.String(5), nullable=False, server_default='L2'),
        sa.Column('daily_budget_usd', sa.Float, nullable=True, server_default='10.0'),
        sa.Column('monthly_budget_usd', sa.Float, nullable=True, server_default='300.0'),
        sa.Column('total_spent_usd', sa.Float, nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_char_startup', 'characters', ['startup_id'])
    op.create_index('ix_char_status', 'characters', ['status'])
    op.create_index('ix_char_startup_status', 'characters', ['startup_id', 'status'])

    # === Character Content ===
    op.create_table(
        'character_content',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('character_id', UUID(as_uuid=True), sa.ForeignKey('characters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=False),
        sa.Column('content_data', JSONB, nullable=False, server_default='{}'),
        sa.Column('generation_pipeline', JSONB, nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('funnel_stage', sa.String(50), nullable=True),
        sa.Column('engagement_metrics', JSONB, nullable=True),
        sa.Column('conversion_events', JSONB, nullable=True),
        sa.Column('cost_usd', sa.Float, nullable=False, server_default='0.0'),
        sa.Column('variant_group', sa.String(50), nullable=True),
        sa.Column('variant_label', sa.String(50), nullable=True),
        sa.Column('virality_score', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_cc_character_platform', 'character_content', ['character_id', 'platform'])
    op.create_index('ix_cc_status', 'character_content', ['status'])
    op.create_index('ix_cc_funnel', 'character_content', ['funnel_stage'])
    op.create_index('ix_cc_created', 'character_content', ['created_at'])
    op.create_index('ix_cc_character_status', 'character_content', ['character_id', 'status'])

def downgrade() -> None:
    op.drop_table('character_content')
    op.drop_table('characters')
    op.execute("DROP TYPE IF EXISTS characterstatus")
    op.execute("DROP TYPE IF EXISTS charactercontenttype")
    op.execute("DROP TYPE IF EXISTS charactercontentstatus")
    op.execute("DROP TYPE IF EXISTS funnelstage")
    op.execute("DROP TYPE IF EXISTS characterplatform")
