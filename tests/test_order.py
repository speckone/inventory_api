from inventory_api_app.models import Order, OrderItem  # type: ignore[unresolved-import]
from tests.factories import (  # type: ignore[unresolved-import]
    CategoryFactory,
    UnitFactory,
    VendorFactory,
    ProductFactory,
    OrderFactory,
    OrderItemFactory,
)


def _create_product(db):
    """Helper to create a product with required foreign keys."""
    category = CategoryFactory()
    unit = UnitFactory()
    vendor = VendorFactory()
    db.session.add_all([category, unit, vendor])
    db.session.flush()

    product = ProductFactory(
        category_id=category.id,
        unit_id=unit.id,
        vendor_id=vendor.id,
    )
    db.session.add(product)
    db.session.flush()
    return product


def _create_order(db):
    """Helper to create an order."""
    order = OrderFactory()
    db.session.add(order)
    db.session.commit()
    return order


def _create_order_item(db, order, product, quantity=5.0):
    """Helper to create an order item linked to an order and product."""
    order_item = OrderItemFactory(
        order_id=order.id,
        product_id=product.id,
        quantity=quantity,
    )
    db.session.add(order_item)
    db.session.commit()
    return order_item


# --- Order tests ---


def test_create_order(client, db, admin_headers):
    """POST /order creates a new order with status New."""
    rep = client.post("/api/v1/order", json={}, headers=admin_headers)
    assert rep.status_code == 201

    result = rep.get_json()
    assert result["msg"] == "order created"
    assert result["order"]["status"] == "New"
    assert result["order"]["id"] is not None


def test_get_order(client, db, admin_headers):
    """GET /order/<id> returns the order."""
    order = _create_order(db)

    rep = client.get(f"/api/v1/order/{order.id}", headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()["order"]
    assert data["id"] == order.id
    assert data["status"] == "New"


def test_get_order_404(client, db, admin_headers):
    """GET /order/<id> returns 404 for nonexistent order."""
    rep = client.get("/api/v1/order/99999", headers=admin_headers)
    assert rep.status_code == 404


def test_get_order_list_paginated(client, db, admin_headers):
    """GET /order returns paginated results."""
    _create_order(db)
    _create_order(db)

    rep = client.get("/api/v1/order", headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()
    assert "results" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data
    assert data["total"] == 2


def test_update_order_status(client, db, admin_headers):
    """PUT /order/<id> updates the order status to Cancelled."""
    order = _create_order(db)

    data = {"status": "Cancelled"}
    rep = client.put(f"/api/v1/order/{order.id}", json=data, headers=admin_headers)
    assert rep.status_code == 200

    result = rep.get_json()
    assert result["msg"] == "order updated"


def test_delete_order(client, db, admin_headers):
    """DELETE /order/<id> removes the order and its items."""
    order = _create_order(db)
    product = _create_product(db)
    db.session.commit()
    _create_order_item(db, order, product)
    order_id = order.id

    rep = client.delete(f"/api/v1/order/{order_id}", headers=admin_headers)
    assert rep.status_code == 200
    assert rep.get_json()["msg"] == "order deleted"

    assert db.session.get(Order, order_id) is None


def test_delete_order_404(client, db, admin_headers):
    """DELETE /order/<id> returns 404 for nonexistent order."""
    rep = client.delete("/api/v1/order/99999", headers=admin_headers)
    assert rep.status_code == 404


# --- OrderItem tests ---


def test_create_order_item(client, db, admin_headers):
    """POST /orderitem creates a new order item."""
    order = _create_order(db)
    product = _create_product(db)
    db.session.commit()

    data = {
        "quantity": 10.0,
        "order_id": order.id,
        "product_id": product.id,
    }

    rep = client.post("/api/v1/orderitem", json=data, headers=admin_headers)
    assert rep.status_code == 201

    result = rep.get_json()
    assert result["msg"] == "order_item created"
    assert result["order_item"]["quantity"] == 10.0
    assert result["order_item"]["order_id"] == order.id
    assert result["order_item"]["product_id"] == product.id


def test_get_order_item(client, db, admin_headers):
    """GET /orderitem/<id> returns the order item."""
    order = _create_order(db)
    product = _create_product(db)
    db.session.commit()
    order_item = _create_order_item(db, order, product)

    rep = client.get(f"/api/v1/orderitem/{order_item.id}", headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()["order_item"]
    assert data["id"] == order_item.id
    assert data["quantity"] == order_item.quantity


def test_get_order_item_404(client, db, admin_headers):
    """GET /orderitem/<id> returns 404 for nonexistent item."""
    rep = client.get("/api/v1/orderitem/99999", headers=admin_headers)
    assert rep.status_code == 404


def test_update_order_item(client, db, admin_headers):
    """PUT /orderitem/<id> updates order item fields."""
    order = _create_order(db)
    product = _create_product(db)
    db.session.commit()
    order_item = _create_order_item(db, order, product, quantity=5.0)

    data = {"quantity": 20.0}
    rep = client.put(
        f"/api/v1/orderitem/{order_item.id}", json=data, headers=admin_headers
    )
    assert rep.status_code == 200

    result = rep.get_json()
    assert result["msg"] == "order_item updated"
    assert result["order_item"]["quantity"] == 20.0


def test_delete_order_item(client, db, admin_headers):
    """DELETE /orderitem/<id> removes the order item."""
    order = _create_order(db)
    product = _create_product(db)
    db.session.commit()
    order_item = _create_order_item(db, order, product)
    item_id = order_item.id

    rep = client.delete(f"/api/v1/orderitem/{item_id}", headers=admin_headers)
    assert rep.status_code == 200
    assert rep.get_json()["msg"] == "order_item deleted"

    assert db.session.get(OrderItem, item_id) is None


def test_get_order_item_list_paginated(client, db, admin_headers):
    """GET /orderitem returns paginated results."""
    order = _create_order(db)
    product = _create_product(db)
    db.session.commit()
    _create_order_item(db, order, product)

    rep = client.get("/api/v1/orderitem", headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()
    assert "results" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data
