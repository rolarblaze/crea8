"""Add tags column to provisions table

Revision ID: 7a4c94c3f841
Revises: 2c53a40310d7
Create Date: 2024-08-04 23:31:48.388879

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a4c94c3f841'
down_revision: Union[str, None] = '2c53a40310d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add the tags column to the provisions table
    op.add_column('provisions', sa.Column('tags', sa.String(), nullable=True))

def downgrade():
    # Remove the tags column from the provisions table
    op.drop_column('provisions', 'tags')