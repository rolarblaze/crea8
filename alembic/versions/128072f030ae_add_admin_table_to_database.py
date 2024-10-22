"""Add Admin Table to Database

Revision ID: 128072f030ae
Revises: 6f50d95c2330
Create Date: 2024-07-12 16:49:26.967990

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '128072f030ae'
down_revision: Union[str, None] = '6f50d95c2330'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'administrators',
        sa.Column('email', sa.String(), primary_key=True, nullable=False, unique=True),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('is_master', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=True),
    )


def downgrade() -> None:
     op.drop_table('administrators')
   

