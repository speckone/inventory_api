from inventory_api_app.database import SurrogatePK, Model, reference_col, relationship, Column
from inventory_api_app.extensions import db
import enum
from datetime import datetime


class Inventory(SurrogatePK, Model):
    __tablename__ = 'inventory'
    quantity = Column(db.Integer, nullable=False)
    capacity = Column(db.Integer, nullable=False)
    product_id = reference_col('product', unique=True)
    reorder_level = Column(db.Integer, nullable=False)
    product = relationship('Product', backref='inventory_items')

    def __repr__(self):
        return self.product.name

    @property
    def running_low(self):
        return self.quantity <= self.reorder_level

    @property
    def needed_at_store(self):
        return self.capacity - self.quantity

    @property
    def cost(self):
        return self.product.unit_price * self.needed_at_store


class Product(SurrogatePK, Model):
    __tablename__ = 'product'
    name = Column(db.String, unique=True, nullable=False)
    unit_price = Column(db.Float, nullable=False)
    unit_id = reference_col('unit')
    unit = relationship('Unit', backref='products')
    vendor_id = reference_col('vendor')
    vendor = relationship('Vendor', backref='products')

    def __repr__(self):
        return self.name


class Unit(SurrogatePK, Model):
    __tablename__ = 'unit'
    name = Column(db.String, unique=True, nullable=False)


class Vendor(SurrogatePK, Model):
    __tablename__ = 'vendor'
    name = Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return self.name


class OrderStatus(enum.Enum):
    NEW = 'New'
    SUBMITTED = 'Submitted'
    RECEIVED = 'Received'

    def __str__(self):
        return self.value


class Order(SurrogatePK, Model):
    __tablename__ = 'order'
    date = Column(db.DateTime)
    status = Column(db.Enum(OrderStatus))

    @property
    def cost(self):
        total = 0
        for order_item in self.order_items:
            total += order_item.quantity * order_item.product.unit_price
        return total

    def __init__(self):
        self.date = datetime.now()
        self.status = OrderStatus.NEW


class OrderItem(SurrogatePK, Model):
    __tablename__ = 'order_item'
    quantity = Column(db.Integer)
    order_id = reference_col('order')
    order = relationship('Order', backref='order_items')
    product_id = reference_col('product')
    product = relationship('Product', backref='order_items')


