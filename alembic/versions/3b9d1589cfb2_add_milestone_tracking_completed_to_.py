"""Add milestone_tracking_completed to package_tracking

Revision ID: 3b9d1589cfb2
Revises: 61e8bdcf3ff4
Create Date: 2024-08-22 17:08:23.518322

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b9d1589cfb2'
down_revision: Union[str, None] = '61e8bdcf3ff4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add the new column to the package_tracking table
    op.add_column('package_tracking', sa.Column('milestone_tracking_completed', sa.Boolean(), nullable=False,server_default='false'))


def downgrade():
    # Remove the milestone_tracking_completed column if downgrading
    op.drop_column('package_tracking', 'milestone_tracking_completed')
