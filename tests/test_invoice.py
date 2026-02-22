from inventory_api_app.models import Customer, Invoice, InvoiceItem  # type: ignore[unresolved-import]
from tests.factories import (  # type: ignore[unresolved-import]
    CustomerFactory,
    InvoiceFactory,
    InvoiceItemFactory,
)


def _create_customer(db, **overrides):
    """Helper to create a customer."""
    customer = CustomerFactory(**overrides)
    db.session.add(customer)
    db.session.commit()
    return customer


def _create_invoice(db, customer, **overrides):
    """Helper to create an invoice linked to a customer."""
    defaults = dict(customer_id=customer.id)
    defaults.update(overrides)
    invoice = InvoiceFactory(**defaults)
    db.session.add(invoice)
    db.session.commit()
    return invoice


def _create_invoice_item(db, invoice, **overrides):
    """Helper to create an invoice item linked to an invoice."""
    defaults = dict(invoice_id=invoice.id)
    defaults.update(overrides)
    invoice_item = InvoiceItemFactory(**defaults)
    db.session.add(invoice_item)
    db.session.commit()
    return invoice_item


# --- Customer tests ---


def test_create_customer(client, db, admin_headers):
    """POST /customer creates a new customer."""
    data = {
        "name": "Acme Corp",
        "address": "456 Oak Ave",
        "city": "Springfield",
        "state": "IL",
        "zip_code": "62704",
        "phone": "555-0200",
        "email": "acme@example.com",
    }

    rep = client.post("/api/v1/customer", json=data, headers=admin_headers)
    assert rep.status_code == 201

    result = rep.get_json()
    assert result["msg"] == "customer created"
    assert result["customer"]["name"] == "Acme Corp"
    assert result["customer"]["email"] == "acme@example.com"


def test_get_customer(client, db, admin_headers):
    """GET /customer/<id> returns the customer."""
    customer = _create_customer(db)

    rep = client.get(f"/api/v1/customer/{customer.id}", headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()["customer"]
    assert data["id"] == customer.id
    assert data["name"] == customer.name


def test_get_customer_404(client, db, admin_headers):
    """GET /customer/<id> returns 404 for nonexistent customer."""
    rep = client.get("/api/v1/customer/99999", headers=admin_headers)
    assert rep.status_code == 404


def test_get_customer_list_paginated(client, db, admin_headers):
    """GET /customer returns paginated results."""
    _create_customer(db)
    _create_customer(db)

    rep = client.get("/api/v1/customer", headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()
    assert "results" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data
    assert data["total"] == 2


def test_update_customer(client, db, admin_headers):
    """PUT /customer/<id> updates customer fields."""
    customer = _create_customer(db)

    data = {"name": "Updated Corp"}
    rep = client.put(
        f"/api/v1/customer/{customer.id}", json=data, headers=admin_headers
    )
    assert rep.status_code == 200

    result = rep.get_json()
    assert result["msg"] == "customer updated"
    assert result["customer"]["name"] == "Updated Corp"


def test_delete_customer(client, db, admin_headers):
    """DELETE /customer/<id> removes the customer."""
    customer = _create_customer(db)
    cust_id = customer.id

    rep = client.delete(f"/api/v1/customer/{cust_id}", headers=admin_headers)
    assert rep.status_code == 200
    assert rep.get_json()["msg"] == "customer deleted"

    assert db.session.get(Customer, cust_id) is None


# --- Invoice tests ---


def test_create_invoice(client, db, admin_headers):
    """POST /invoice creates a new invoice."""
    customer = _create_customer(db)

    data = {
        "invoice_number": 5001,
        "customer_id": customer.id,
        "paid": False,
    }

    rep = client.post("/api/v1/invoice", json=data, headers=admin_headers)
    assert rep.status_code == 201

    result = rep.get_json()
    assert result["msg"] == "invoice created"
    assert result["invoice"]["invoice_number"] == 5001
    assert result["invoice"]["customer_id"] == customer.id
    assert result["invoice"]["paid"] is False


def test_get_invoice(client, db, admin_headers):
    """GET /invoice/<id> returns the invoice."""
    customer = _create_customer(db)
    invoice = _create_invoice(db, customer)

    rep = client.get(f"/api/v1/invoice/{invoice.id}", headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()["invoice"]
    assert data["id"] == invoice.id
    assert data["invoice_number"] == invoice.invoice_number


def test_get_invoice_404(client, db, admin_headers):
    """GET /invoice/<id> returns 404 for nonexistent invoice."""
    rep = client.get("/api/v1/invoice/99999", headers=admin_headers)
    assert rep.status_code == 404


def test_get_invoice_list_paginated(client, db, admin_headers):
    """GET /invoice returns paginated results."""
    customer = _create_customer(db)
    _create_invoice(db, customer, invoice_number=6001)
    _create_invoice(db, customer, invoice_number=6002)

    rep = client.get("/api/v1/invoice", headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()
    assert "results" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data
    assert data["total"] == 2


def test_update_invoice(client, db, admin_headers):
    """PUT /invoice/<id> updates invoice fields."""
    customer = _create_customer(db)
    invoice = _create_invoice(db, customer)

    data = {"paid": True}
    rep = client.put(
        f"/api/v1/invoice/{invoice.id}", json=data, headers=admin_headers
    )
    assert rep.status_code == 200

    result = rep.get_json()
    assert result["msg"] == "invoice updated"
    assert result["invoice"]["paid"] is True


def test_delete_invoice(client, db, admin_headers):
    """DELETE /invoice/<id> removes the invoice."""
    customer = _create_customer(db)
    invoice = _create_invoice(db, customer)
    inv_id = invoice.id

    rep = client.delete(f"/api/v1/invoice/{inv_id}", headers=admin_headers)
    assert rep.status_code == 200
    assert rep.get_json()["msg"] == "invoice deleted"

    assert db.session.get(Invoice, inv_id) is None


# --- InvoiceItem tests ---


def test_create_invoice_item(client, db, admin_headers):
    """POST /invoiceitem creates a new invoice item."""
    customer = _create_customer(db)
    invoice = _create_invoice(db, customer)

    data = {
        "description": "Consulting service",
        "price_per_unit": 150.0,
        "quantity": 3.0,
        "invoice_id": invoice.id,
    }

    rep = client.post("/api/v1/invoiceitem", json=data, headers=admin_headers)
    assert rep.status_code == 201

    result = rep.get_json()
    assert result["msg"] == "invoice_item created"
    assert result["invoice_item"]["description"] == "Consulting service"
    assert result["invoice_item"]["price_per_unit"] == 150.0
    assert result["invoice_item"]["quantity"] == 3.0
    assert result["invoice_item"]["amount"] == 450.0


def test_get_invoice_item(client, db, admin_headers):
    """GET /invoiceitem/<id> returns the invoice item."""
    customer = _create_customer(db)
    invoice = _create_invoice(db, customer)
    item = _create_invoice_item(db, invoice)

    rep = client.get(f"/api/v1/invoiceitem/{item.id}", headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()["invoice_item"]
    assert data["id"] == item.id
    assert data["description"] == item.description


def test_get_invoice_item_404(client, db, admin_headers):
    """GET /invoiceitem/<id> returns 404 for nonexistent item."""
    rep = client.get("/api/v1/invoiceitem/99999", headers=admin_headers)
    assert rep.status_code == 404


def test_get_invoice_item_list_paginated(client, db, admin_headers):
    """GET /invoiceitem returns paginated results."""
    customer = _create_customer(db)
    invoice = _create_invoice(db, customer)
    _create_invoice_item(db, invoice)
    _create_invoice_item(db, invoice)

    rep = client.get("/api/v1/invoiceitem", headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()
    assert "results" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data
    assert data["total"] == 2


def test_update_invoice_item(client, db, admin_headers):
    """PUT /invoiceitem/<id> updates invoice item fields."""
    customer = _create_customer(db)
    invoice = _create_invoice(db, customer)
    item = _create_invoice_item(db, invoice, price_per_unit=10.0, quantity=1.0)

    data = {"quantity": 5.0}
    rep = client.put(
        f"/api/v1/invoiceitem/{item.id}", json=data, headers=admin_headers
    )
    assert rep.status_code == 200

    result = rep.get_json()
    assert result["msg"] == "invoice_item updated"
    assert result["invoice_item"]["quantity"] == 5.0


def test_delete_invoice_item(client, db, admin_headers):
    """DELETE /invoiceitem/<id> removes the invoice item."""
    customer = _create_customer(db)
    invoice = _create_invoice(db, customer)
    item = _create_invoice_item(db, invoice)
    item_id = item.id

    rep = client.delete(f"/api/v1/invoiceitem/{item_id}", headers=admin_headers)
    assert rep.status_code == 200
    assert rep.get_json()["msg"] == "invoice_item deleted"

    assert db.session.get(InvoiceItem, item_id) is None
