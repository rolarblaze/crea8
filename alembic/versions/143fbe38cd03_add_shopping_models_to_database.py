"""Add shopping models to database

Revision ID: 143fbe38cd03
Revises: d22b7d8383ac
Create Date: 2024-07-13 01:04:53.505128

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '143fbe38cd03'
down_revision: Union[str, None] = 'd22b7d8383ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table('services',
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.Column('service_name', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('service_id'),
    sa.UniqueConstraint('service_name')
    )
    op.create_index(op.f('ix_services_service_id'), 'services', ['service_id'], unique=False)
    
    op.create_table('bundles',
    sa.Column('bundle_id', sa.Integer(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.Column('bundle_name', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['service_id'], ['services.service_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('bundle_id')
    )
    op.create_index(op.f('ix_bundles_bundle_id'), 'bundles', ['bundle_id'], unique=False)
    
    op.create_table('packages',
    sa.Column('package_id', sa.Integer(), nullable=False),
    sa.Column('bundle_id', sa.Integer(), nullable=False),
    sa.Column('package_name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['bundle_id'], ['bundles.bundle_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('package_id')
    )
    op.create_index(op.f('ix_packages_package_id'), 'packages', ['package_id'], unique=False)
    
    op.create_table('provisions',
    sa.Column('provision_id', sa.Integer(), nullable=False),
    sa.Column('package_id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['package_id'], ['packages.package_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('provision_id')
    )
    op.create_index(op.f('ix_provisions_provision_id'), 'provisions', ['provision_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_provisions_provision_id'), table_name='provisions')
    op.drop_table('provisions')
    op.drop_index(op.f('ix_packages_package_id'), table_name='packages')
    op.drop_table('packages')
    op.drop_index(op.f('ix_bundles_bundle_id'), table_name='bundles')
    op.drop_table('bundles')
    op.drop_index(op.f('ix_services_service_id'), table_name='services')
    op.drop_table('services')
