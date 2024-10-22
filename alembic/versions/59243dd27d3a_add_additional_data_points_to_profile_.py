"""Add additional data points to profile table

Revision ID: 59243dd27d3a
Revises: 9d5c8d737af7
Create Date: 2024-08-02 00:14:16.579974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59243dd27d3a'
down_revision: Union[str, None] = '9d5c8d737af7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('profiles', sa.Column('phone_number', sa.String(), nullable=True))
    op.add_column('profiles', sa.Column('country', sa.String(), nullable=True))
    op.add_column('profiles', sa.Column('state', sa.String(), nullable=True))
    op.add_column('profiles', sa.Column('address', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('profiles', 'phone_number')
    op.drop_column('profiles', 'country')
    op.drop_column('profiles', 'state')
    op.drop_column('profiles', 'address')