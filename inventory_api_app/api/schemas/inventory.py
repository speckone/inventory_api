from inventory_api_app.models import Inventory, Product, Unit, Vendor, Order, OrderItem, OrderStatus, Category
from inventory_api_app.extensions import ma, db
from marshmallow import fields


class InventorySchema(ma.SQLAlchemyAutoSchema):
    running_low = fields.Boolean(dump_only=True)
    needed_at_store = fields.Float(dump_only=True)
    cost = fields.Float(dump_only=True)

    class Meta:
        model = Inventory
        load_instance = True
        include_fk = True


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        include_fk = True


class UnitSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Unit
        load_instance = True
        include_relationships = True


class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        load_instance = True
        include_relationships = True


class VendorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vendor
        load_instance = True
        include_relationships = True


class OrderSchema(ma.SQLAlchemyAutoSchema):
    status = fields.Enum(OrderStatus, by_value=True)
    cost = fields.Float(dump_only=True)

    class Meta:
        model = Order
        load_instance = True
        include_relationships = True


class OrderItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderItem
        load_instance = True
        include_fk = True


