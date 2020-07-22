from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from flask_restful.utils import cors
from marshmallow import ValidationError

from inventory_api_app.api.resources import UserResource, UserList, OrderList, OrderResource, OrderItemList, \
    OrderItemResource, ProductList, ProductResource, VendorList, VendorResource, UnitList, UnitResource, \
    InventoryList, InventoryResource, CategoryList, CategoryResource, ProductHistoryResource
from inventory_api_app.api.schemas import UserSchema, InventorySchema, UnitSchema, VendorSchema, ProductSchema, \
    OrderSchema, OrderItemSchema, CategorySchema
from inventory_api_app.extensions import apispec
from flask_cors import CORS

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(blueprint)
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


@blueprint.before_app_first_request
def register_views():
    apispec.spec.components.schema("UserSchema", schema=UserSchema)
    apispec.spec.path(view=UserResource, app=current_app)
    apispec.spec.path(view=UserList, app=current_app)
    apispec.spec.components.schema("InventorySchema", schema=InventorySchema)
    apispec.spec.path(view=InventoryResource, app=current_app)
    apispec.spec.path(view=InventoryList, app=current_app)
    apispec.spec.components.schema("UnitSchema", schema=UnitSchema)
    apispec.spec.path(view=UnitResource, app=current_app)
    apispec.spec.path(view=UnitList, app=current_app)
    apispec.spec.components.schema("CategorySchema", schema=CategorySchema)
    apispec.spec.path(view=CategoryResource, app=current_app)
    apispec.spec.path(view=CategoryList, app=current_app)
    apispec.spec.components.schema("VendorSchema", schema=VendorSchema)
    apispec.spec.path(view=VendorResource, app=current_app)
    apispec.spec.path(view=VendorList, app=current_app)
    apispec.spec.components.schema("ProductSchema", schema=ProductSchema)
    apispec.spec.path(view=ProductResource, app=current_app)
    apispec.spec.path(view=ProductList, app=current_app)
    apispec.spec.path(view=ProductHistoryResource, app=current_app)
    apispec.spec.components.schema("OrderSchema", schema=OrderSchema)
    apispec.spec.path(view=OrderResource, app=current_app)
    apispec.spec.path(view=OrderList, app=current_app)
    apispec.spec.components.schema("OrderItemSchema", schema=OrderItemSchema)
    apispec.spec.path(view=OrderItemResource, app=current_app)
    apispec.spec.path(view=OrderItemList, app=current_app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
