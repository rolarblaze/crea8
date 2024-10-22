"""Add meeting code column to package tracking table

Revision ID: 58d03e62dc0b
Revises: 9e538f2fbd2e
Create Date: 2024-08-10 12:53:03.169540

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '58d03e62dc0b'
down_revision: Union[str, None] = '9e538f2fbd2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add the 'meeting_code' column to the 'package_tracking' table
    op.add_column('package_tracking', sa.Column('meeting_code', sa.String(), nullable=True))


def downgrade():
    # Remove the 'meeting_code' column from the 'package_tracking' table
    op.drop_column('package_tracking', 'meeting_code')
