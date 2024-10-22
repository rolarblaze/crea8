"""rename google_sso column on the users to google_oauth

Revision ID: 6607786ba6fa
Revises: 6cb3c0979476
Create Date: 2024-08-20 23:09:24.179013

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6607786ba6fa'
down_revision: Union[str, None] = '6cb3c0979476'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Alter only the column name
    op.alter_column('users', 'google_sso', new_column_name='google_oauth')


def downgrade() -> None:
    # Restore column
    op.alter_column('users', 'google_oauth', new_column_name='google_sso')
