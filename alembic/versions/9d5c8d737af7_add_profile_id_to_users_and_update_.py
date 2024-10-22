"""Add profile_id to users and update profile table

Revision ID: 9d5c8d737af7
Revises: 781d007d2b56
Create Date: 2024-07-30 13:38:39.916163

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d5c8d737af7'
down_revision: Union[str, None] = '781d007d2b56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # Add profile_id column to the 'users' table
    op.add_column('users', sa.Column('profile_id', sa.Integer(), sa.ForeignKey('profiles.profile_id'), unique=True))

    # Remove ForeignKey constraint from 'profiles.user_email'
    op.drop_constraint('profiles_user_email_fkey', 'profiles', type_='foreignkey')

    # Change user_email in 'profiles' table to not be a foreign key
    op.alter_column('profiles', 'user_email', existing_type=sa.String(), nullable=False, unique=True)

def downgrade():
    # Remove profile_id column from 'users' table
    op.drop_column('users', 'profile_id')

    # Re-add ForeignKey constraint to 'profiles.user_email'
    op.create_foreign_key('profiles_user_email_fkey', 'profiles', 'users', ['user_email'], ['email'], ondelete='CASCADE')

    # Revert user_email column in 'profiles' table to be a foreign key
    op.alter_column('profiles', 'user_email', existing_type=sa.String(), nullable=False, unique=False)
