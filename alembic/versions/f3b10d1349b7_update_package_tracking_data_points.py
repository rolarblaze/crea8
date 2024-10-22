"""Update package tracking data points

Revision ID: f3b10d1349b7
Revises: b8175788e796
Create Date: 2024-08-12 17:45:46.443925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3b10d1349b7'
down_revision: Union[str, None] = 'b8175788e796'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Adding new columns to the package_tracking table
    op.add_column('package_tracking', sa.Column('off_boarding_meeting_code', sa.String(), nullable=True))
    op.add_column('package_tracking', sa.Column('off_boarding_meeting_start_time', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('package_tracking', sa.Column('off_boarding_meeting_end_time', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('package_tracking', sa.Column('zoho_project_is_available', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('package_tracking', sa.Column('zoho_project_status', sa.String(), nullable=True))

def downgrade():
    # Dropping the newly added columns if the migration is rolled back
    op.drop_column('package_tracking', 'off_boarding_meeting_code')
    op.drop_column('package_tracking', 'off_boarding_meeting_start_time')
    op.drop_column('package_tracking', 'off_boarding_meeting_end_time')
    op.drop_column('package_tracking', 'zoho_project_is_available')
    op.drop_column('package_tracking', 'zoho_project_status')