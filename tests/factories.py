import factory  # type: ignore[unresolved-import]
from inventory_api_app.models import (  # type: ignore[unresolved-import]
    User,
    Category,
    Unit,
    Vendor,
    Product,
    Inventory,
    Order,
    OrderItem,
    Customer,
    CustomerContact,
    Invoice,
    InvoiceItem,
)


class UserFactory(factory.Factory):

    username = factory.Sequence(lambda n: "user%d" % n)
    email = factory.Sequence(lambda n: "user%d@mail.com" % n)
    password = "mypwd"

    class Meta:
        model = User


class CategoryFactory(factory.Factory):

    name = factory.Sequence(lambda n: "category%d" % n)

    class Meta:
        model = Category


class UnitFactory(factory.Factory):

    name = factory.Sequence(lambda n: "unit%d" % n)

    class Meta:
        model = Unit


class VendorFactory(factory.Factory):

    name = factory.Sequence(lambda n: "vendor%d" % n)

    class Meta:
        model = Vendor


class ProductFactory(factory.Factory):

    name = factory.Sequence(lambda n: "product%d" % n)
    unit_price = 10.0

    class Meta:
        model = Product


class InventoryFactory(factory.Factory):

    quantity = 50.0
    capacity = 100.0
    reorder_level = 10.0

    class Meta:
        model = Inventory


class OrderFactory(factory.Factory):

    class Meta:
        model = Order


class OrderItemFactory(factory.Factory):

    quantity = 5.0

    class Meta:
        model = OrderItem


class CustomerFactory(factory.Factory):

    name = factory.Sequence(lambda n: "customer%d" % n)
    address = "123 Main St"
    city = "Testville"
    state = "TX"
    zip_code = "12345"
    phone = "555-0100"

    class Meta:
        model = Customer


class CustomerContactFactory(factory.Factory):

    name = factory.Sequence(lambda n: "contact%d" % n)
    email = factory.Sequence(lambda n: "contact%d@mail.com" % n)
    primary = False

    class Meta:
        model = CustomerContact


class InvoiceFactory(factory.Factory):

    invoice_number = factory.Sequence(lambda n: 1000 + n)
    paid = False

    class Meta:
        model = Invoice


class InvoiceItemFactory(factory.Factory):

    description = factory.Sequence(lambda n: "Service item %d" % n)
    price_per_unit = 25.0
    quantity = 2.0

    class Meta:
        model = InvoiceItem
