"""Add meeting start time and end time to package tracking table

Revision ID: 1f87b8c94798
Revises: 58d03e62dc0b
Create Date: 2024-08-10 13:13:03.985607

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f87b8c94798'
down_revision: Union[str, None] = '58d03e62dc0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add 'start_time' and 'end_time' columns to the 'package_tracking' table
    op.add_column('package_tracking', sa.Column('meeting_start_time', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('package_tracking', sa.Column('meeting_end_time', sa.TIMESTAMP(timezone=True), nullable=True))


def downgrade():
    # Remove 'start_time' and 'end_time' columns from the 'package_tracking' table
    op.drop_column('package_tracking', 'meeting_start_time')
    op.drop_column('package_tracking', 'meeting_end_time')