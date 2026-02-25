"""add language to telecom_numbers

Revision ID: 345fe0813ef7
Revises: ee9d106d6ad3
Create Date: 2026-02-22 08:14:53.527694

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '345fe0813ef7'
down_revision: Union[str, None] = 'ee9d106d6ad3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('telecom_numbers', sa.Column('language', sa.String(length=20), server_default='en-US', nullable=False))


def downgrade() -> None:
    pass
