"""Add ViralAsset model

Revision ID: ee9d106d6ad3
Revises: 20260213_080000_char_factory
Create Date: 2026-02-21 17:15:31.241374

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ee9d106d6ad3'
down_revision: Union[str, None] = '20260213_080000_char_factory'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'viral_assets',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('campaign_topic', sa.String(), nullable=False),
        sa.Column('hook_text', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'POSTED', 'REJECTED', name='viralassetstatus', native_enum=False, create_constraint=True, length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_viral_assets_campaign_topic'), 'viral_assets', ['campaign_topic'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_viral_assets_campaign_topic'), table_name='viral_assets')
    op.drop_table('viral_assets')
