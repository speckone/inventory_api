"""rename description_template to invoice_item_template and add price_per_unit

Revision ID: b3c7e2f1a045
Revises: 69899b5f9a86
Create Date: 2026-02-23 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3c7e2f1a045'
down_revision = '69899b5f9a86'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('description_template', 'invoice_item_template')
    op.add_column('invoice_item_template', sa.Column('price_per_unit', sa.Float(), nullable=True))


def downgrade():
    op.drop_column('invoice_item_template', 'price_per_unit')
    op.rename_table('invoice_item_template', 'description_template')
