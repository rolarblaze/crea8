"""Remove discovery_call_booked and discovery_call_link from package tracking table

Revision ID: 366a3e2d6606
Revises: 1f87b8c94798
Create Date: 2024-08-10 13:35:31.224772

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '366a3e2d6606'
down_revision: Union[str, None] = '1f87b8c94798'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Remove 'discovery_call_booked' and 'discovery_call_link' columns from 'PackageTracking' table
    op.drop_column('package_tracking', 'discovery_call_booked')
    op.drop_column('package_tracking', 'discovery_call_link')


def downgrade():
    # Add 'discovery_call_booked' and 'discovery_call_link' columns back to 'PackageTracking' table
    op.add_column('package_tracking', sa.Column('discovery_call_booked', sa.Boolean(), nullable=True))
    op.add_column('package_tracking', sa.Column('discovery_call_link', sa.String(), nullable=True))