"""Drop purchases table

Revision ID: fae334151d1b
Revises: 12cbccc51c0f
Create Date: 2024-08-07 10:18:42.480743

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fae334151d1b'
down_revision: Union[str, None] = '12cbccc51c0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop the 'purchases' table
    op.drop_table('purchases')

def downgrade():
    # Recreate the 'purchases' table
    op.create_table(
        'purchases',
        sa.Column('purchase_id', sa.Integer(), nullable=False),
        sa.Column('package_id', sa.Integer(), nullable=False),
        sa.Column('profile_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('purchase_id'),
        sa.ForeignKeyConstraint(['package_id'], ['packages.package_id'], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.profile_id'], ondelete="CASCADE")
    )