"""Add cascade delete to profiles.user_email

Revision ID: ee4cc55b31ad
Revises: 107953cfa1a1
Create Date: 2024-08-02 04:44:51.573251

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee4cc55b31ad'
down_revision: Union[str, None] = '107953cfa1a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add your foreign key constraint with ON DELETE CASCADE
    op.drop_constraint('fk_profiles_user_email_users', 'profiles', type_='foreignkey')
    op.create_foreign_key(
        'fk_profiles_user_email_users',
        'profiles',
        'users',
        ['user_email'],
        ['email'],
        ondelete='CASCADE'
    )

def downgrade():
    # Remove the constraint or revert to the previous state
    op.drop_constraint('fk_profiles_user_email_users', 'profiles', type_='foreignkey')
    op.create_foreign_key(
        'fk_profiles_user_email_users',
        'profiles',
        'users',
        ['user_email'],
        ['email']
    )

