from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from inventory_api_app.models.invoice import Customer, Invoice, InvoiceItem
from inventory_api_app.api.schemas.invoice import CustomerSchema, InvoiceSchema, InvoiceItemSchema
from inventory_api_app.extensions import db


class CustomerResource(Resource):
    """Single object resource
    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: customer_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  customer: CustomerSchema
        404:
          description: customer does not exists
    put:
      tags:
        - api
      parameters:
        - in: path
          name: customer_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              CustomerSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: customer updated
                  customer: CustomerSchema
        404:
          description: customer does not exists
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: customer_id
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
                    example: customer deleted
        404:
          description: customer does not exists
    """
    method_decorators = [jwt_required()]

    def get(self, customer_id):
        schema = CustomerSchema()
        customer = Customer.query.get_or_404(customer_id)
        return {"customer": schema.dump(customer)}

    def put(self, customer_id):
        schema = CustomerSchema(partial=True)
        customer = Customer.query.get_or_404(customer_id)
        customer = schema.load(request.json, instance=customer, session=db.session)

        db.session.commit()

        return {"msg": "customer updated", "customer": schema.dump(customer)}

    def delete(self, customer_id):
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()

        return {"msg": "customer deleted"}


class CustomerList(Resource):
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
                      $ref: '#/components/schemas/CustomerSchema'
    post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              CustomerSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: customer created
                  customer: CustomerSchema
    """
    method_decorators = [jwt_required()]

    def get(self):
        schema = CustomerSchema(many=True)
        query = Customer.query
        return schema.dump(query.all())

    def post(self):
        schema = CustomerSchema()
        customer = schema.load(request.json, session=db.session)

        db.session.add(customer)
        db.session.commit()

        return {"msg": "customer created", "customer": schema.dump(customer)}, 201


class InvoiceResource(Resource):
    """Single object resource
    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: invoice_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  invoice: InvoiceSchema
        404:
          description: invoice does not exists
    put:
      tags:
        - api
      parameters:
        - in: path
          name: invoice_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              InvoiceSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: invoice updated
                  invoice: InvoiceSchema
        404:
          description: invoice does not exists
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: invoice_id
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
                    example: invoice deleted
        404:
          description: invoice does not exists
    """
    method_decorators = [jwt_required()]

    def get(self, invoice_id):
        schema = InvoiceSchema()
        invoice = Invoice.query.get_or_404(invoice_id)
        return {"invoice": schema.dump(invoice)}

    def put(self, invoice_id):
        schema = InvoiceSchema(partial=True)
        invoice = Invoice.query.get_or_404(invoice_id)
        invoice = schema.load(request.json, instance=invoice, session=db.session)

        db.session.commit()

        return {"msg": "invoice updated", "invoice": schema.dump(invoice)}

    def delete(self, invoice_id):
        invoice = Invoice.query.get_or_404(invoice_id)
        for item in invoice.invoice_items:
            db.session.delete(item)
        db.session.delete(invoice)
        db.session.commit()

        return {"msg": "invoice deleted"}


class InvoiceList(Resource):
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
                      $ref: '#/components/schemas/InvoiceSchema'
    post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              InvoiceSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: invoice created
                  invoice: InvoiceSchema
    """
    method_decorators = [jwt_required()]

    def get(self):
        schema = InvoiceSchema(many=True)
        query = Invoice.query
        return schema.dump(query.all())

    def post(self):
        schema = InvoiceSchema()
        invoice = schema.load(request.json, session=db.session)

        db.session.add(invoice)
        db.session.commit()

        return {"msg": "invoice created", "invoice": schema.dump(invoice)}, 201


class InvoiceItemResource(Resource):
    """Single object resource
    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: invoice_item_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  invoice_item: InvoiceItemSchema
        404:
          description: invoice_item does not exists
    put:
      tags:
        - api
      parameters:
        - in: path
          name: invoice_item_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              InvoiceItemSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: invoice_item updated
                  invoice_item: InvoiceItemSchema
        404:
          description: invoice_item does not exists
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: invoice_item_id
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
                    example: invoice_item deleted
        404:
          description: invoice_item does not exists
    """
    method_decorators = [jwt_required()]

    def get(self, invoice_item_id):
        schema = InvoiceItemSchema()
        invoice_item = InvoiceItem.query.get_or_404(invoice_item_id)
        return {"invoice_item": schema.dump(invoice_item)}

    def put(self, invoice_item_id):
        schema = InvoiceItemSchema(partial=True)
        invoice_item = InvoiceItem.query.get_or_404(invoice_item_id)
        invoice_item = schema.load(request.json, instance=invoice_item, session=db.session)

        db.session.commit()

        return {"msg": "invoice_item updated", "invoice_item": schema.dump(invoice_item)}

    def delete(self, invoice_item_id):
        invoice_item = InvoiceItem.query.get_or_404(invoice_item_id)
        db.session.delete(invoice_item)
        db.session.commit()

        return {"msg": "invoice_item deleted"}


class InvoiceItemList(Resource):
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
                      $ref: '#/components/schemas/InvoiceItemSchema'
    post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              InvoiceItemSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: invoice_item created
                  invoice_item: InvoiceItemSchema
    """
    method_decorators = [jwt_required()]

    def get(self):
        schema = InvoiceItemSchema(many=True)
        query = InvoiceItem.query
        return schema.dump(query.all())

    def post(self):
        schema = InvoiceItemSchema()
        invoice_item = schema.load(request.json, session=db.session)

        db.session.add(invoice_item)
        db.session.commit()

        return {"msg": "invoice_item created", "invoice_item": schema.dump(invoice_item)}, 201
