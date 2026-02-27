from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from inventory_api_app.models.invoice import Customer, CustomerContact, Invoice, InvoiceItem, InvoiceItemTemplate
from inventory_api_app.auth.decorators import admin_required
from inventory_api_app.services.email import EmailService
from inventory_api_app.api.schemas.invoice import (
    CustomerSchema,
    CustomerContactSchema,
    InvoiceSchema,
    InvoiceItemSchema,
    InvoiceItemTemplateSchema,
)
from inventory_api_app.extensions import db
from inventory_api_app.commons.pagination import paginate


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
        return paginate(query, schema)

    def post(self):
        schema = CustomerSchema()
        customer = schema.load(request.json, session=db.session)

        db.session.add(customer)
        db.session.commit()

        return {"msg": "customer created", "customer": schema.dump(customer)}, 201


class CustomerContactResource(Resource):
    """Single customer contact resource
    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: customer_id
          schema:
            type: integer
        - in: path
          name: contact_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  customer_contact: CustomerContactSchema
        404:
          description: contact does not exist
    put:
      tags:
        - api
      parameters:
        - in: path
          name: customer_id
          schema:
            type: integer
        - in: path
          name: contact_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              CustomerContactSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: customer contact updated
                  customer_contact: CustomerContactSchema
        404:
          description: contact does not exist
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: customer_id
          schema:
            type: integer
        - in: path
          name: contact_id
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
                    example: customer contact deleted
        404:
          description: contact does not exist
    """
    method_decorators = [jwt_required()]

    def get(self, customer_id, contact_id):
        schema = CustomerContactSchema()
        Customer.query.get_or_404(customer_id)
        contact = CustomerContact.query.filter_by(
            id=contact_id, customer_id=customer_id
        ).first_or_404()
        return {"customer_contact": schema.dump(contact)}

    def put(self, customer_id, contact_id):
        schema = CustomerContactSchema(partial=True)
        Customer.query.get_or_404(customer_id)
        contact = CustomerContact.query.filter_by(
            id=contact_id, customer_id=customer_id
        ).first_or_404()
        contact = schema.load(request.json, instance=contact, session=db.session)

        if contact.primary:
            CustomerContact.query.filter(
                CustomerContact.customer_id == customer_id,
                CustomerContact.id != contact_id,
            ).update({"primary": False})

        db.session.commit()
        return {"msg": "customer contact updated", "customer_contact": schema.dump(contact)}

    def delete(self, customer_id, contact_id):
        Customer.query.get_or_404(customer_id)
        contact = CustomerContact.query.filter_by(
            id=contact_id, customer_id=customer_id
        ).first_or_404()
        db.session.delete(contact)
        db.session.commit()
        return {"msg": "customer contact deleted"}


class CustomerContactList(Resource):
    """Customer contacts list and creation
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
                allOf:
                  - type: array
                    items:
                      $ref: '#/components/schemas/CustomerContactSchema'
    post:
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
              CustomerContactSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: customer contact created
                  customer_contact: CustomerContactSchema
    """
    method_decorators = [jwt_required()]

    def get(self, customer_id):
        schema = CustomerContactSchema(many=True)
        Customer.query.get_or_404(customer_id)
        contacts = CustomerContact.query.filter_by(customer_id=customer_id).all()
        return {"results": schema.dump(contacts)}

    def post(self, customer_id):
        schema = CustomerContactSchema()
        Customer.query.get_or_404(customer_id)
        contact = schema.load(request.json, session=db.session)
        contact.customer_id = customer_id

        if contact.primary:
            CustomerContact.query.filter_by(
                customer_id=customer_id
            ).update({"primary": False})

        db.session.add(contact)
        db.session.commit()
        return {"msg": "customer contact created", "customer_contact": schema.dump(contact)}, 201


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
        return paginate(query, schema)

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
        return paginate(query, schema)

    def post(self):
        schema = InvoiceItemSchema()
        invoice_item = schema.load(request.json, session=db.session)

        db.session.add(invoice_item)
        db.session.commit()

        return {"msg": "invoice_item created", "invoice_item": schema.dump(invoice_item)}, 201


class InvoiceItemTemplateResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: invoice_item_template_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  invoice_item_template: InvoiceItemTemplateSchema
        404:
          description: invoice_item_template does not exists
    put:
      tags:
        - api
      parameters:
        - in: path
          name: invoice_item_template_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              InvoiceItemTemplateSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: invoice_item_template updated
                  invoice_item_template: InvoiceItemTemplateSchema
        404:
          description: invoice_item_template does not exists
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: invoice_item_template_id
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
                    example: invoice_item_template deleted
        404:
          description: invoice_item_template does not exists
    """

    method_decorators = [jwt_required()]

    def get(self, invoice_item_template_id):
        schema = InvoiceItemTemplateSchema()
        invoice_item_template = InvoiceItemTemplate.query.get_or_404(
            invoice_item_template_id
        )
        return {"invoice_item_template": schema.dump(invoice_item_template)}

    def put(self, invoice_item_template_id):
        schema = InvoiceItemTemplateSchema(partial=True)
        invoice_item_template = InvoiceItemTemplate.query.get_or_404(
            invoice_item_template_id
        )
        invoice_item_template = schema.load(
            request.json, instance=invoice_item_template, session=db.session
        )

        db.session.commit()

        return {
            "msg": "invoice_item_template updated",
            "invoice_item_template": schema.dump(invoice_item_template),
        }

    def delete(self, invoice_item_template_id):
        invoice_item_template = InvoiceItemTemplate.query.get_or_404(
            invoice_item_template_id
        )
        db.session.delete(invoice_item_template)
        db.session.commit()

        return {"msg": "invoice_item_template deleted"}


class InvoiceItemTemplateList(Resource):
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
                      $ref: '#/components/schemas/InvoiceItemTemplateSchema'
    post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              InvoiceItemTemplateSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: invoice_item_template created
                  invoice_item_template: InvoiceItemTemplateSchema
    """

    method_decorators = [jwt_required()]

    def get(self):
        schema = InvoiceItemTemplateSchema(many=True)
        query = InvoiceItemTemplate.query
        return paginate(query, schema)

    def post(self):
        schema = InvoiceItemTemplateSchema()
        invoice_item_template = schema.load(request.json, session=db.session)

        db.session.add(invoice_item_template)
        db.session.commit()

        return {
            "msg": "invoice_item_template created",
            "invoice_item_template": schema.dump(invoice_item_template),
        }, 201


class InvoiceSendResource(Resource):
    """Send invoice via email
    ---
    post:
      tags:
        - api
      parameters:
        - in: path
          name: invoice_id
          schema:
            type: integer
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                pdf:
                  type: string
                  format: binary
      responses:
        200:
          description: email queued
        400:
          description: missing PDF or no primary contact
        404:
          description: invoice not found
    """

    method_decorators = [admin_required()]

    def post(self, invoice_id):
        invoice = db.session.get(Invoice, invoice_id)
        if not invoice:
            return {"msg": "Invoice not found"}, 404

        customer = db.session.get(Customer, invoice.customer_id)
        if not customer:
            return {"msg": "Customer not found"}, 404

        pdf_file = request.files.get("pdf")
        if not pdf_file:
            return {"msg": "PDF file is required"}, 400

        pdf_bytes = pdf_file.read()

        error = EmailService.send_invoice_email(invoice, customer, pdf_bytes)
        if error:
            return error

        invoice.update(sent=True)

        return {"msg": "Invoice email queued"}, 200
