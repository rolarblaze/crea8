"""Add profile and purchase tables to database

Revision ID: 781d007d2b56
Revises: 2e28719f0986
Create Date: 2024-07-29 23:16:42.757683

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '781d007d2b56'
down_revision: Union[str, None] = '2e28719f0986'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('profiles',
        sa.Column('profile_id', sa.Integer(), nullable=False),
        sa.Column('user_email', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_email'], ['users.email'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('profile_id')
    )
    op.create_index(op.f('ix_profiles_profile_id'), 'profiles', ['profile_id'], unique=False)
    
    op.create_table('purchases',
        sa.Column('purchase_id', sa.Integer(), nullable=False),
        sa.Column('package_id', sa.Integer(), nullable=False),
        sa.Column('profile_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.profile_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['package_id'], ['packages.package_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('purchase_id')
    )
    op.create_index(op.f('ix_purchases_purchase_id'), 'purchases', ['purchase_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_purchases_purchase_id'), table_name='purchases')
    op.drop_table('purchases')
    
    op.drop_index(op.f('ix_profiles_profile_id'), table_name='profiles')
    op.drop_table('profiles')
    
