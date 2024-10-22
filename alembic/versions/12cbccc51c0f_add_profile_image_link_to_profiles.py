"""Add profile_image_link to profiles

Revision ID: 12cbccc51c0f
Revises: ed5c5a388b23
Create Date: 2024-08-06 22:42:24.310472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12cbccc51c0f'
down_revision: Union[str, None] = 'ed5c5a388b23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('profiles', sa.Column('profile_image_link', sa.String(), nullable=True))

def downgrade():
    op.drop_column('profiles', 'profile_image_link')
