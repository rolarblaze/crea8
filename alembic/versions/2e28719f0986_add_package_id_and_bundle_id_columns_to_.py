"""Add package id and bundle id columns to briefs table

Revision ID: 2e28719f0986
Revises: c428a56da0e6
Create Date: 2024-07-19 09:57:07.260694

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e28719f0986'
down_revision: Union[str, None] = 'c428a56da0e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add new columns to the briefs table
    op.add_column('briefs', sa.Column('package_id', sa.Integer(), nullable=True))
    op.add_column('briefs', sa.Column('bundle_id', sa.Integer(), nullable=True))

def downgrade():
    # Remove the new columns from the briefs table
    op.drop_column('briefs', 'package_id')
    op.drop_column('briefs', 'bundle_id')