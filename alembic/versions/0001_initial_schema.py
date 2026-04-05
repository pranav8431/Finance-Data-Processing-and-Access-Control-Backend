"""Initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-04-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role = sa.Enum('viewer', 'analyst', 'admin', name='user_role')
    user_status = sa.Enum('active', 'inactive', name='user_status')
    record_type = sa.Enum('income', 'expense', name='record_type')

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', user_role, nullable=False),
        sa.Column('status', user_status, nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    op.create_table(
        'financial_records',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('amount', sa.Numeric(14, 2), nullable=False),
        sa.Column('type', record_type, nullable=False),
        sa.Column('category', sa.String(length=120), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_financial_records_category', 'financial_records', ['category'])
    op.create_index('ix_financial_records_created_by', 'financial_records', ['created_by'])
    op.create_index('ix_financial_records_date', 'financial_records', ['date'])
    op.create_index('ix_financial_records_type', 'financial_records', ['type'])


def downgrade() -> None:
    op.drop_index('ix_financial_records_type', table_name='financial_records')
    op.drop_index('ix_financial_records_date', table_name='financial_records')
    op.drop_index('ix_financial_records_created_by', table_name='financial_records')
    op.drop_index('ix_financial_records_category', table_name='financial_records')
    op.drop_table('financial_records')

    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
