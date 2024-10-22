"""Create contact_messages table

Revision ID: fb9cce0e747c
Revises: 6607786ba6fa
Create Date: 2024-08-26 11:28:30.709988

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fb9cce0e747c'
down_revision: Union[str, None] = '6607786ba6fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # create contact_messages table
    op.create_table('contact_messages',
    sa.Column('contact_message_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=False),
    sa.Column('message', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'),onupdate=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('contact_message_id')
    )
    # create an index on the contact_message_id column
    op.create_index(op.f('ix_contact_message_id'), 'contact_messages', ['contact_message_id'], unique=True)


def downgrade() -> None:
    # drop index on the contact_message_id column
    op.drop_index(op.f('ix_contact_message_id'), 'contact_messages', ['contact_message_id'], unique=True)
    # drop contact_messages table
    op.drop_table('contact_messages')
