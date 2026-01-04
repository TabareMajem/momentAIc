"""add new agent types to enum

Revision ID: ba37d68a3704
Revises: 9ef90fa44811
Create Date: 2026-01-04 10:16:51.043939

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba37d68a3704'
down_revision: Union[str, None] = '9ef90fa44811'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new values to AgentType enum
    # We must commit before ALTER TYPE in some setups, but here we assume standard handling
    # If using transaction, must execute outside it? 
    # autocommit=True is usually specific to connection.
    # We try straightforward execution.
    op.execute("ALTER TYPE agenttype ADD VALUE IF NOT EXISTS 'onboarding_coach'")
    op.execute("ALTER TYPE agenttype ADD VALUE IF NOT EXISTS 'competitor_intel'")
    op.execute("ALTER TYPE agenttype ADD VALUE IF NOT EXISTS 'fundraising_coach'")


def downgrade() -> None:
    # Postgres ENUMs do not support removing values easily.
    pass
