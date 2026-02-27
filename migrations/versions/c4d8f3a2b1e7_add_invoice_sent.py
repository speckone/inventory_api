"""add invoice sent column

Revision ID: c4d8f3a2b1e7
Revises: b3c7e2f1a045
Create Date: 2026-02-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4d8f3a2b1e7'
down_revision = 'b3c7e2f1a045'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('invoice', sa.Column('sent', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('invoice', 'sent')
