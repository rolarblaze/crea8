"""Add created_at and updated_at to recommendation_briefs table

Revision ID: 61e8bdcf3ff4
Revises: dd8923211ba1
Create Date: 2024-08-14 16:01:15.159776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61e8bdcf3ff4'
down_revision: Union[str, None] = 'dd8923211ba1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add the created_at and updated_at columns to the recommendation_briefs table
    op.add_column('recommendation_briefs', 
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    op.add_column('recommendation_briefs', 
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False)
    )


def downgrade():
    # Remove the created_at and updated_at columns from the recommendation_briefs table
    op.drop_column('recommendation_briefs', 'created_at')
    op.drop_column('recommendation_briefs', 'updated_at')