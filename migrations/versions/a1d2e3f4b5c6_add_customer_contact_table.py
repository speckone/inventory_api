"""add customer_contact table and remove customer email

Revision ID: a1d2e3f4b5c6
Revises: 767c16525530
Create Date: 2026-02-26 23:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1d2e3f4b5c6'
down_revision = '767c16525530'
branch_labels = None
depends_on = None


def upgrade():
    # Create customer_contact table
    op.create_table(
        'customer_contact',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customer.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('primary', sa.Boolean(), nullable=False, server_default='false'),
    )
    op.create_index('ix_customer_contact_customer_id', 'customer_contact', ['customer_id'])

    # Migrate existing customer emails into customer_contact records
    op.execute(
        """
        INSERT INTO customer_contact (customer_id, name, email, "primary")
        SELECT id, name, email, true
        FROM customer
        WHERE email IS NOT NULL AND email != ''
        """
    )

    # Drop email column from customer
    op.drop_column('customer', 'email')


def downgrade():
    # Add email column back to customer
    op.add_column('customer', sa.Column('email', sa.String()))

    # Migrate primary contact emails back to customer
    op.execute(
        """
        UPDATE customer
        SET email = (
            SELECT email FROM customer_contact
            WHERE customer_contact.customer_id = customer.id
            AND customer_contact."primary" = true
            LIMIT 1
        )
        """
    )

    # Drop customer_contact table
    op.drop_index('ix_customer_contact_customer_id', 'customer_contact')
    op.drop_table('customer_contact')
