"""Add brief_submission_date to package tracking table

Revision ID: b8175788e796
Revises: 3d194fedd8eb
Create Date: 2024-08-11 18:20:52.610056

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8175788e796'
down_revision: Union[str, None] = '366a3e2d6606'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.add_column('package_tracking', sa.Column('brief_submission_date', sa.TIMESTAMP(timezone=True), nullable=True))

def downgrade():
    op.drop_column('package_tracking', 'brief_submission_date')
