"""Change price field to be optional

Revision ID: 632f696e6917
Revises: 143fbe38cd03
Create Date: 2024-07-16 15:50:40.476725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '632f696e6917'
down_revision: Union[str, None] = '143fbe38cd03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('packages', 'price',
               existing_type=sa.Float(),
               nullable=True)

def downgrade():
    op.alter_column('packages', 'price',
               existing_type=sa.Float(),
               nullable=False)
