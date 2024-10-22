"""Add first Admin to Administrators table

Revision ID: d22b7d8383ac
Revises: 128072f030ae
Create Date: 2024-07-12 17:09:53.606915

"""
from typing import Sequence, Union
from sqlalchemy import Transaction, Transaction, Table, Column, String
from alembic import op
import sqlalchemy as sa
from app.config import settings
from sqlalchemy import text
from app.utils import hash


# revision identifiers, used by Alembic.
revision: str = 'd22b7d8383ac'
down_revision: Union[str, None] = '128072f030ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.bulk_insert(
        sa.Table('administrators', sa.MetaData(), autoload_with=op.get_bind()),
        [
            {'email': f'{settings.admin_email}',
                'password': f'{hash(settings.admin_password)}', "is_master": True},
        ]
    )

def downgrade():
    op.execute(text("DELETE FROM administrators WHERE email = :email").bindparams(
        email=settings.admin_email))
