from inventory_api_app.database import SurrogatePK, Model, reference_col, relationship, Column
from inventory_api_app.extensions import db
from datetime import datetime


class Customer(SurrogatePK, Model):
    __tablename__ = 'customer'
    name = Column(db.String, unique=True, nullable=False)
    address = Column(db.String)
    city = Column(db.String)
    state = Column(db.String)
    zip_code = Column(db.String)
    phone = Column(db.String)
    email = Column(db.String)

    def __repr__(self):
        return self.name


class Invoice(SurrogatePK, Model):
    __tablename__ = 'invoice'
    invoice_number = Column(db.Integer, unique=True, nullable=False)
    date = Column(db.DateTime)
    paid = Column(db.Boolean, default=False, nullable=False)
    customer_id = reference_col('customer')
    customer = relationship('Customer', backref='invoices')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.date is None:
            self.date = datetime.now()

    @property
    def subtotal(self):
        total = 0
        for item in self.invoice_items:
            total += item.price_per_unit * item.quantity
        return total

    def __repr__(self):
        return f'Invoice #{self.invoice_number}'


class InvoiceItem(SurrogatePK, Model):
    __tablename__ = 'invoice_item'
    date_of_service = Column(db.Date)
    description = Column(db.String, nullable=False)
    price_per_unit = Column(db.Float, nullable=False)
    quantity = Column(db.Float, nullable=False)
    invoice_id = reference_col('invoice')
    invoice = relationship('Invoice', backref='invoice_items')

    @property
    def amount(self):
        return self.price_per_unit * self.quantity

    def __repr__(self):
        return self.description
