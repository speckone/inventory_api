from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from inventory_api_app.models import Inventory, Product, Unit, Vendor, Order, OrderItem, OrderStatus
from inventory_api_app.api.schemas import InventorySchema, VendorSchema, UnitSchema, ProductSchema, OrderSchema, \
    OrderItemSchema
from inventory_api_app.extensions import ma, db
from twilio.rest import Client

class InventoryResource(Resource):
    """Single object resource
    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: inventory_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  inventory: InventorySchema
        404:
          description: inventory does not exists
    put:
      tags:
        - api
      parameters:
        - in: path
          name: inventory_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              InventorySchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: inventory updated
                  inventory: InventorySchema
        404:
          description: inventory does not exists
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: inventory_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: inventory deleted
        404:
          description: inventory does not exists
    """
    method_decorators = [jwt_required]

    def get(self, inventory_id):
        schema = InventorySchema()
        inventory = Inventory.query.get_or_404(inventory_id)
        return {"inventory": schema.dump(inventory)}

    def put(self, inventory_id):
        schema = InventorySchema(partial=True)
        inventory = Inventory.query.get_or_404(inventory_id)
        inventory = schema.load(request.json, instance=inventory, session=db.session)

        db.session.commit()

        return {"msg": "inventory updated", "inventory": schema.dump(inventory)}

    def delete(self, inventory_id):
        inventory = Inventory.query.get_or_404(inventory_id)
        db.session.delete(inventory)
        db.session.commit()

        return {"msg": "Inventory deleted"}


class InventoryList(Resource):
    """Creation and get_all
    ---
    get:
      tags:
        - api
      responses:
        200:
          content:
            application/json:
              schema:
                allOf:
                  - type: array
                    items:
                      $ref: '#/components/schemas/InventorySchema'
    post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              InventorySchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: inventory created
                  inventory: InventorySchema
    """
    method_decorators = [jwt_required]

    def get(self):
        schema = InventorySchema(many=True)
        query = Inventory.query
        return schema.dump(query.all())

    def post(self):
        schema = InventorySchema()
        inventory = schema.load(request.json, session=db.session)

        db.session.add(inventory)
        db.session.commit()

        return {"msg": "Inventory created", "inventory": schema.dump(inventory)}, 201


class ProductResource(Resource):
    """Single object resource
    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: product_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  product: ProductSchema
        404:
          description: product does not exists
    put:
      tags:
        - api
      parameters:
        - in: path
          name: product_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              ProductSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: product updated
                  product: ProductSchema
        404:
          description: product does not exists
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: product_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: product deleted
        404:
          description: product does not exists
    """
    method_decorators = [jwt_required]

    def get(self, product_id):
        schema = ProductSchema()
        product = Product.query.get_or_404(product_id)
        return {"product": schema.dump(product)}

    def put(self, product_id):
        schema = ProductSchema(partial=True)
        product = Product.query.get_or_404(product_id)
        product = schema.load(request.json, instance=product, session=db.session)

        db.session.commit()

        return {"msg": "product updated", "product": schema.dump(product)}

    def delete(self, product_id):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()

        return {"msg": "product deleted"}


class ProductList(Resource):
    """Creation and get_all
    ---
    get:
      tags:
        - api
      responses:
        200:
          content:
            application/json:
              schema:
                allOf:
                  - type: array
                    items:
                      $ref: '#/components/schemas/ProductSchema'
    post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              ProductSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: product created
                  product: ProductSchema
    """
    method_decorators = [jwt_required]

    def get(self):
        schema = ProductSchema(many=True)
        query = Product.query
        return schema.dump(query.all())

    def post(self):
        schema = ProductSchema()
        product = schema.load(request.json, session=db.session)

        db.session.add(product)
        db.session.commit()

        return {"msg": "product created", "product": schema.dump(product)}, 201


class UnitResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: unit_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  unit: UnitSchema
        404:
          description: unit does not exists
    put:
      tags:
        - api
      parameters:
        - in: path
          name: unit_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              UnitSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: unit updated
                  unit: UnitSchema
        404:
          description: unit does not exists
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: unit_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: unit deleted
        404:
          description: unit does not exists
    """
    method_decorators = [jwt_required]

    def get(self, unit_id):
        schema = UnitSchema()
        unit = Unit.query.get_or_404(unit_id)
        return {"unit": schema.dump(unit)}

    def put(self, unit_id):
        schema = UnitSchema(partial=True)
        unit = Unit.query.get_or_404(unit_id)
        unit = schema.load(request.json, instance=unit, session=db.session)

        db.session.commit()

        return {"msg": "unit updated", "unit": schema.dump(unit)}

    def delete(self, unit_id):
        unit = Unit.query.get_or_404(unit_id)
        db.session.delete(unit)
        db.session.commit()

        return {"msg": "unit deleted"}


class UnitList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      responses:
        200:
          content:
            application/json:
              schema:
                allOf:
                  - type: array
                    items:
                      $ref: '#/components/schemas/UnitSchema'
    post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              UnitSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: unit created
                  unit: UnitSchema
    """
    method_decorators = [jwt_required]

    def get(self):
        schema = UnitSchema(many=True)
        query = Unit.query
        return schema.dump(query.all())

    def post(self):
        schema = UnitSchema()
        unit = schema.load(request.json, session=db.session)

        db.session.add(unit)
        db.session.commit()

        return {"msg": "unit created", "unit": schema.dump(unit)}, 201


class VendorResource(Resource):
    """Single object resource
    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: vendor_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  vendor: VendorSchema
        404:
          description: vendor does not exists
    put:
      tags:
        - api
      parameters:
        - in: path
          name: vendor_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              VendorSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: vendor updated
                  vendor: VendorSchema
        404:
          description: vendor does not exists
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: vendor_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: vendor deleted
        404:
          description: vendor does not exists
    """
    method_decorators = [jwt_required]

    def get(self, vendor_id):
        schema = VendorSchema()
        vendor = Vendor.query.get_or_404(vendor_id)
        return {"vendor": schema.dump(vendor)}

    def put(self, vendor_id):
        schema = VendorSchema(partial=True)
        vendor = Vendor.query.get_or_404(vendor_id)
        vendor = schema.load(request.json, instance=vendor, session=db.session)

        db.session.commit()

        return {"msg": "vendor updated", "vendor": schema.dump(vendor)}

    def delete(self, vendor_id):
        vendor = Vendor.query.get_or_404(vendor_id)
        db.session.delete(vendor)
        db.session.commit()

        return {"msg": "vendor deleted"}


class VendorList(Resource):
    """Creation and get_all
    ---
    get:
      tags:
        - api
      responses:
        200:
          content:
            application/json:
              schema:
                allOf:
                  - type: array
                    items:
                      $ref: '#/components/schemas/VendorSchema'
    post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              VendorSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: vendor created
                  vendor: VendorSchema
    """
    method_decorators = [jwt_required]

    def get(self):
        schema = VendorSchema(many=True)
        query = Vendor.query
        return schema.dump(query.all())

    def post(self):
        schema = VendorSchema()
        vendor = schema.load(request.json, session=db.session)

        db.session.add(vendor)
        db.session.commit()

        return {"msg": "vendor created", "vendor": schema.dump(vendor)}, 201


class OrderResource(Resource):
    """Single object resource
    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: order_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  order: OrderSchema
        404:
          description: order does not exists
    put:
      tags:
        - api
      parameters:
        - in: path
          name: order_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              OrderSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: order updated
                  order: OrderSchema
        404:
          description: order does not exists
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: order_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: order deleted
        404:
          description: order does not exists
    """
    method_decorators = [jwt_required]

    def get(self, order_id):
        schema = OrderSchema()
        order = Order.query.get_or_404(order_id)
        return {"order": schema.dump(order)}

    def put(self, order_id):
        schema = OrderSchema(partial=True)
        order_db = Order.query.get_or_404(order_id)
        order = schema.load(request.json, instance=order_db, session=db.session)
        db.session.commit()

        # Compose SMS on order submit
        if request.json['status'] == OrderStatus.SUBMITTED.value:
            config = current_app.config
            account_sid = config["TWILLIO_SID"]
            auth_token = config["TWILLIO_TOKEN"]
            client = Client(account_sid, auth_token)
            vendor = None
            order_info = list()
            for order_item in sorted(order_db.order_items, key=lambda o:o.product.vendor_id):
                if vendor != order_item.product.vendor:
                    order_info.append(f"{order_item.product.vendor}:")
                    vendor = order_item.product.vendor
                order_info.append(f"{order_item.quantity} {order_item.product.unit.name}s of {order_item.product.name}")
            message = client.messages.create(from_=config["FROM_PHONE"],
                                             to=config["TO_PHONE"],
                                             body="\n".join(order_info))
            current_app.logger.debug(message.sid)
        elif request.json['status'] == OrderStatus.RECEIVED.value:
            for order_item in order_db.order_items:
                inventory_item = Inventory.query.filter(Inventory.product_id == order_item.product_id).one()
                inventory_item.quantity += order_item.quantity
                inventory_item.save()
                db.session.commit()
        return {"msg": "order updated", "order": schema.dump(order)}

    def delete(self, order_id):
        order = Order.query.get_or_404(order_id)
        order_items = order.order_items
        for order_item in order_items:
            db.session.delete(order_item)
        db.session.delete(order)
        db.session.commit()

        return {"msg": "order deleted"}


class OrderList(Resource):
    """Creation and get_all
    ---
    get:
      tags:
        - api
      responses:
        200:
          content:
            application/json:
              schema:
                allOf:
                  - type: array
                    items:
                      $ref: '#/components/schemas/OrderSchema'
    post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              OrderSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: order created
                  order: OrderSchema
    """
    method_decorators = [jwt_required]

    def get(self):
        schema = OrderSchema(many=True)
        query = Order.query
        return schema.dump(query.all())

    def post(self):
        schema = OrderSchema()
        order_request = dict()
        if request.json:
            order_request = request.json
        order = schema.load(order_request, session=db.session)

        db.session.add(order)
        inventory = Inventory.query.all()
        for item in inventory:
            order_item = OrderItem(quantity=item.needed_at_store,
                                   order_id=order.id,
                                   product_id=item.product.id)
            order_item.save()
        db.session.commit()

        return {"msg": "order created", "order": schema.dump(order)}, 201


class OrderItemResource(Resource):
    """Single object resource
    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: order_item_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  order_item: OrderItemSchema
        404:
          description: order_item does not exists
    put:
      tags:
        - api
      parameters:
        - in: path
          name: order_item_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              OrderItemSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: order_item updated
                  order_item: OrderItemSchema
        404:
          description: order_item does not exists
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: order_item_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: order_item deleted
        404:
          description: order_item does not exists
    """
    method_decorators = [jwt_required]

    def get(self, order_item_id):
        schema = OrderItemSchema()
        order_item = OrderItem.query.get_or_404(order_item_id)
        return {"order_item": schema.dump(order_item)}

    def put(self, order_item_id):
        schema = OrderItemSchema(partial=True)
        order_item = OrderItem.query.get_or_404(order_item_id)
        order_item = schema.load(request.json, instance=order_item, session=db.session)

        db.session.commit()

        return {"msg": "order_item updated", "order_item": schema.dump(order_item)}

    def delete(self, order_item_id):
        order_item = OrderItem.query.get_or_404(order_item_id)
        db.session.delete(order_item)
        db.session.commit()

        return {"msg": "order_item deleted"}


class OrderItemList(Resource):
    """Creation and get_all
    ---
    get:
      tags:
        - api
      responses:
        200:
          content:
            application/json:
              schema:
                allOf:
                  - type: array
                    items:
                      $ref: '#/components/schemas/OrderItemSchema'
    post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              OrderItemSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: order_item created
                  order_item: OrderItemSchema
    """
    method_decorators = [jwt_required]

    def get(self):
        schema = OrderItemSchema(many=True)
        query = OrderItem.query
        return schema.dump(query.all())

    def post(self):
        schema = OrderItemSchema()
        order_item = schema.load(request.json, session=db.session)

        db.session.add(order_item)
        db.session.commit()

        return {"msg": "order_item created", "order_item": schema.dump(order_item)}, 201
