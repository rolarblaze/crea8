"""Set up tables properly

Revision ID: 6f50d95c2330
Revises: 42e6aa0f6edf
Create Date: 2024-07-10 22:22:44.297553

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f50d95c2330'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create the users table
    op.create_table(
        'users',
        sa.Column('email', sa.String(), nullable=False, unique=True, primary_key=True),
        sa.Column('password', sa.String(), nullable=True),
        sa.Column('is_individual', sa.Boolean(), server_default='FALSE'),
        sa.Column('is_business', sa.Boolean(), server_default='FALSE'),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('otp_value', sa.String(), nullable=True),
        sa.Column('otp_value_created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('password_reset_code', sa.String(), nullable=True),
        sa.Column('password_reset_code_timer', sa.String(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=True),
    )

    # Create the individual_users table
    op.create_table(
        'individual_users',
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False, unique=True, primary_key=True),
        sa.Column('password', sa.String(), nullable=False),
    )

    # Create the business_users table
    op.create_table(
        'business_users',
        sa.Column('business_name', sa.String(), nullable=False, unique=True),
        sa.Column('email', sa.String(), nullable=False, unique=True, primary_key=True),
        sa.Column('password', sa.String(), nullable=False),
    )

    # Create the subscribers table
    op.create_table(
        'subscribers',
        sa.Column('email', sa.String(), nullable=False, unique=True, primary_key=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

def downgrade():
    # Drop the subscribers table
    op.drop_table('subscribers')

    # Drop the business_users table
    op.drop_table('business_users')

    # Drop the individual_users table
    op.drop_table('individual_users')

    # Drop the users table
    op.drop_table('users')