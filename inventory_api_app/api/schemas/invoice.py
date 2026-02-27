from inventory_api_app.models.invoice import Customer, CustomerContact, Invoice, InvoiceItem, InvoiceItemTemplate
from inventory_api_app.extensions import ma
from marshmallow import fields


class CustomerContactSchema(ma.SQLAlchemyAutoSchema):
    customer_id = fields.Integer(dump_only=True)

    class Meta:
        model = CustomerContact
        load_instance = True
        include_fk = True


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    invoices = fields.List(
        fields.Nested("InvoiceSchema", dump_only=True, exclude=("customer",))
    )
    contacts = fields.List(
        fields.Nested("CustomerContactSchema", dump_only=True)
    )

    class Meta:
        model = Customer
        load_instance = True
        include_relationships = True


class InvoiceSchema(ma.SQLAlchemyAutoSchema):
    subtotal = fields.Float(dump_only=True)
    customer = fields.Nested(
        CustomerSchema, dump_only=True, exclude=("invoices",)
    )

    class Meta:
        model = Invoice
        load_instance = True
        include_fk = True
        include_relationships = True


class InvoiceItemSchema(ma.SQLAlchemyAutoSchema):
    amount = fields.Float(dump_only=True)

    class Meta:
        model = InvoiceItem
        load_instance = True
        include_fk = True


class InvoiceItemTemplateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = InvoiceItemTemplate
        load_instance = True
