"""add archived columns to customer and product

Revision ID: e6f0a5b3c9d1
Revises: d5e9f4a3b2c8
Create Date: 2026-03-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'e6f0a5b3c9d1'
down_revision = 'd5e9f4a3b2c8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('customer', sa.Column('archived', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('product', sa.Column('archived', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('product', 'archived')
    op.drop_column('customer', 'archived')
