"""Add foreign keys to individual_users and business_users

Revision ID: ed5c5a388b23
Revises: 7a4c94c3f841
Create Date: 2024-08-06 21:17:31.278123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed5c5a388b23'
down_revision: Union[str, None] = '7a4c94c3f841'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add foreign key to individual_users table
    op.create_foreign_key(
        'fk_individual_users_email_users',
        'individual_users', 'users',
        ['email'], ['email'],
        ondelete='CASCADE'
    )
    
    # Add foreign key to business_users table
    op.create_foreign_key(
        'fk_business_users_email_users',
        'business_users', 'users',
        ['email'], ['email'],
        ondelete='CASCADE'
    )


def downgrade():
    # Drop foreign key from individual_users table
    op.drop_constraint('fk_individual_users_email_users', 'individual_users', type_='foreignkey')
    
    # Drop foreign key from business_users table
    op.drop_constraint('fk_business_users_email_users', 'business_users', type_='foreignkey')