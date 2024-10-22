"""add google sso to users table alter business and individual users tables password nullable

Revision ID: 6cb3c0979476
Revises: 3b9d1589cfb2
Create Date: 2024-08-20 17:12:04.260261

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6cb3c0979476'
down_revision: Union[str, None] = '3b9d1589cfb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add google_sso column to 'users' table
    op.add_column('users', sa.Column('google_sso', sa.Boolean(), nullable=True))
    
    # change password column in 'business_users' table to be nullable
    op.alter_column('business_users', 'password', existing_type=sa.String(), nullable=True)
    
    # change password column in 'individual_users' table to be nullable
    op.alter_column('individual_users', 'password', existing_type=sa.String(), nullable=True)

def downgrade() -> None:
    # Drop google_sso column in 'users' table
    op.drop_column('users', 'google_sso')
    
    # change password column in 'business_users' table to not be nullable
    op.alter_column('business_users', 'password', existing_type=sa.String(), nullable=False)
    
    # change password column in 'individual_users' table to not be nullable
    op.alter_column('individual_users', 'password', existing_type=sa.String(), nullable=False)

