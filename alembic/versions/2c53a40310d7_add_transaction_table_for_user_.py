"""Add Transaction Table for user transactions

Revision ID: 2c53a40310d7
Revises: ee4cc55b31ad
Create Date: 2024-08-04 19:51:09.432828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c53a40310d7'
down_revision: Union[str, None] = 'ee4cc55b31ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'transactions',
        sa.Column('transaction_id', sa.Integer, primary_key=True, index=True),
        sa.Column('trans_ref', sa.String, unique=True, nullable=False),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('currency', sa.String, nullable=False),
        sa.Column('status', sa.String, nullable=False, default="pending"),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('user_email', sa.String, sa.ForeignKey('users.email', ondelete="SET NULL"), nullable=True),
        sa.Column('package_id', sa.Integer, sa.ForeignKey('packages.package_id', ondelete="SET NULL"), nullable=True),
        sa.Column('profile_id', sa.Integer, sa.ForeignKey('profiles.profile_id', ondelete="SET NULL"), nullable=True)
    )
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['transaction_id'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_table('transactions')
