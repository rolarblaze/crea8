"""Add temporary briefs table

Revision ID: c428a56da0e6
Revises: 58629afe4a0a
Create Date: 2024-07-19 02:30:38.759519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c428a56da0e6'
down_revision: Union[str, None] = '58629afe4a0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('briefs',
    sa.Column('brief_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('company_name', sa.String(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=False),
    sa.Column('work_email', sa.String(), nullable=False),
    sa.Column('industry_type', sa.String(), nullable=False),
    sa.Column('brief_objectives', sa.String(), nullable=False),
    sa.Column('brief_description', sa.String(), nullable=False),
    sa.Column('competitors', sa.String(), nullable=False),
    sa.Column('benchmarks', sa.String(), nullable=False),
    sa.Column('brief_attachment', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('brief_id')
    )
    op.create_index(op.f('ix_briefs_brief_id'), 'briefs', ['brief_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_briefs_brief_id'), table_name='briefs')
    op.drop_table('briefs')