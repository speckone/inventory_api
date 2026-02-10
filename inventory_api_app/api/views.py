from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError
from jwt.exceptions import ExpiredSignatureError, DecodeError, InvalidTokenError

from inventory_api_app.api.resources import UserResource, UserList, OrderList, OrderResource, OrderItemList, \
    OrderItemResource, ProductList, ProductResource, VendorList, VendorResource, UnitList, UnitResource, \
    InventoryList, InventoryResource, CategoryList, CategoryResource, ProductHistoryResource, \
    CustomerResource, CustomerList, InvoiceResource, InvoiceList, InvoiceItemResource, InvoiceItemList
from inventory_api_app.api.schemas import UserSchema, InventorySchema, UnitSchema, VendorSchema, ProductSchema, \
    OrderSchema, OrderItemSchema, CategorySchema, CustomerSchema, InvoiceSchema, InvoiceItemSchema
from inventory_api_app.extensions import apispec
from flask_cors import CORS


class CustomApi(Api):
    """Custom Api class to handle JWT exceptions"""

    def handle_error(self, e):
        """Override handle_error to catch JWT exceptions"""
        if isinstance(e, ExpiredSignatureError):
            return jsonify({"msg": "Token has expired"}), 401
        elif isinstance(e, (DecodeError, InvalidTokenError)):
            return jsonify({"msg": "Invalid token"}), 401
        # Fall back to default error handling
        return super().handle_error(e)


blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = CustomApi(blueprint)
CORS(blueprint)


api.add_resource(UserResource, "/users/<int:user_id>", endpoint="user_by_id")
api.add_resource(UserList, "/users", endpoint="users")
api.add_resource(InventoryResource, '/inventory/<int:inventory_id>', endpoint="inventory_by_id")
api.add_resource(InventoryList, '/inventory', endpoint="inventory")
api.add_resource(UnitResource, '/unit/<int:unit_id>')
api.add_resource(UnitList, '/unit')
api.add_resource(CategoryResource, '/category/<int:category_id>')
api.add_resource(CategoryList, '/category')
api.add_resource(VendorResource, '/vendor/<int:vendor_id>')
api.add_resource(VendorList, '/vendor')
api.add_resource(ProductResource, '/product/<int:product_id>')
api.add_resource(ProductList, '/product')
api.add_resource(ProductHistoryResource, '/product/<int:product_id>/history')
api.add_resource(OrderItemResource, '/orderitem/<int:order_item_id>')
api.add_resource(OrderItemList, '/orderitem')
api.add_resource(OrderResource, '/order/<int:order_id>')
api.add_resource(OrderList, '/order')
api.add_resource(CustomerResource, '/customer/<int:customer_id>')
api.add_resource(CustomerList, '/customer')
api.add_resource(InvoiceResource, '/invoice/<int:invoice_id>')
api.add_resource(InvoiceList, '/invoice')
api.add_resource(InvoiceItemResource, '/invoiceitem/<int:invoice_item_id>')
api.add_resource(InvoiceItemList, '/invoiceitem')


def register_apispec_views(app):
    with app.app_context():
        apispec.spec.components.schema("UserSchema", schema=UserSchema)
        apispec.spec.path(view=UserResource, app=app)
        apispec.spec.path(view=UserList, app=app)
        apispec.spec.components.schema("InventorySchema", schema=InventorySchema)
        apispec.spec.path(view=InventoryResource, app=app)
        apispec.spec.path(view=InventoryList, app=app)
        apispec.spec.components.schema("UnitSchema", schema=UnitSchema)
        apispec.spec.path(view=UnitResource, app=app)
        apispec.spec.path(view=UnitList, app=app)
        apispec.spec.components.schema("CategorySchema", schema=CategorySchema)
        apispec.spec.path(view=CategoryResource, app=app)
        apispec.spec.path(view=CategoryList, app=app)
        apispec.spec.components.schema("VendorSchema", schema=VendorSchema)
        apispec.spec.path(view=VendorResource, app=app)
        apispec.spec.path(view=VendorList, app=app)
        apispec.spec.components.schema("ProductSchema", schema=ProductSchema)
        apispec.spec.path(view=ProductResource, app=app)
        apispec.spec.path(view=ProductList, app=app)
        apispec.spec.path(view=ProductHistoryResource, app=app)
        apispec.spec.components.schema("OrderSchema", schema=OrderSchema)
        apispec.spec.path(view=OrderResource, app=app)
        apispec.spec.path(view=OrderList, app=app)
        apispec.spec.components.schema("OrderItemSchema", schema=OrderItemSchema)
        apispec.spec.path(view=OrderItemResource, app=app)
        apispec.spec.path(view=OrderItemList, app=app)
        apispec.spec.components.schema("CustomerSchema", schema=CustomerSchema)
        apispec.spec.path(view=CustomerResource, app=app)
        apispec.spec.path(view=CustomerList, app=app)
        apispec.spec.components.schema("InvoiceSchema", schema=InvoiceSchema)
        apispec.spec.path(view=InvoiceResource, app=app)
        apispec.spec.path(view=InvoiceList, app=app)
        apispec.spec.components.schema("InvoiceItemSchema", schema=InvoiceItemSchema)
        apispec.spec.path(view=InvoiceItemResource, app=app)
        apispec.spec.path(view=InvoiceItemList, app=app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
