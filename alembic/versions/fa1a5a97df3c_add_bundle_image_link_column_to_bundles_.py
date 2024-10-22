"""Add bundle image link column to bundles table

Revision ID: fa1a5a97df3c
Revises: c2fbcfc019ef
Create Date: 2024-08-14 01:43:47.645316

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa1a5a97df3c'
down_revision: Union[str, None] = 'c2fbcfc019ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add bundle_image_link column to bundles table
    op.add_column('bundles', sa.Column('bundle_image_link', sa.String(), nullable=True))

def downgrade():
    # Remove bundle_image_link column from bundles table
    op.drop_column('bundles', 'bundle_image_link')