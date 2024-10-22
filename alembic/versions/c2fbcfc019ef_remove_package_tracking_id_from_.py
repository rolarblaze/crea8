"""Remove package_tracking_id from transactions table

Revision ID: c2fbcfc019ef
Revises: f3b10d1349b7
Create Date: 2024-08-13 13:38:24.501737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2fbcfc019ef'
down_revision: Union[str, None] = 'f3b10d1349b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Dropping the package_tracking_id column from the transactions table
    op.drop_column('transactions', 'package_tracking_id')

def downgrade():
    # Adding the package_tracking_id column back to the transactions table in case of rollback
    op.add_column('transactions', sa.Column('package_tracking_id', sa.Integer(), nullable=True))