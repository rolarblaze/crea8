"""Add availability column to provisions table

Revision ID: 58629afe4a0a
Revises: 632f696e6917
Create Date: 2024-07-16 16:51:05.366599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '58629afe4a0a'
down_revision: Union[str, None] = '632f696e6917'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('provisions', sa.Column('availability', sa.Boolean(), server_default='true', nullable=False))


def downgrade():
    op.drop_column('provisions', 'availability')