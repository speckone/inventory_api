"""add short_code columns to customer and invoice_item_template

Revision ID: d5e9f4a3b2c8
Revises: c4d8f3a2b1e7
Create Date: 2026-03-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'd5e9f4a3b2c8'
down_revision = 'c4d8f3a2b1e7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('customer', sa.Column('short_code', sa.String(), nullable=True))
    op.create_unique_constraint('uq_customer_short_code', 'customer', ['short_code'])
    op.add_column('invoice_item_template', sa.Column('short_code', sa.String(), nullable=True))
    op.create_unique_constraint('uq_invoice_item_template_short_code', 'invoice_item_template', ['short_code'])


def downgrade():
    op.drop_constraint('uq_invoice_item_template_short_code', 'invoice_item_template', type_='unique')
    op.drop_column('invoice_item_template', 'short_code')
    op.drop_constraint('uq_customer_short_code', 'customer', type_='unique')
    op.drop_column('customer', 'short_code')
