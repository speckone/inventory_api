from inventory_api_app.models import Inventory  # type: ignore[unresolved-import]
from tests.factories import (  # type: ignore[unresolved-import]
    CategoryFactory,
    UnitFactory,
    VendorFactory,
    ProductFactory,
    InventoryFactory,
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


def _create_inventory(db, **overrides):
    """Helper to create an inventory item with a backing product."""
    product = _create_product(db)
    defaults = dict(product_id=product.id)
    defaults.update(overrides)
    inventory = InventoryFactory(**defaults)
    db.session.add(inventory)
    db.session.commit()
    return inventory


def test_get_inventory_list_paginated(client, db, admin_headers):
    """GET /inventory returns paginated results with expected keys."""
    _create_inventory(db)
    _create_inventory(db)

    rep = client.get("/api/v1/inventory", headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()
    assert "results" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data
    assert data["total"] == 2
    assert data["page"] == 1
    assert len(data["results"]) == 2


def test_get_single_inventory(client, db, admin_headers):
    """GET /inventory/<id> returns the inventory item."""
    inventory = _create_inventory(db)

    rep = client.get(f"/api/v1/inventory/{inventory.id}", headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()["inventory"]
    assert data["id"] == inventory.id
    assert data["quantity"] == inventory.quantity
    assert data["capacity"] == inventory.capacity
    assert data["reorder_level"] == inventory.reorder_level


def test_get_single_inventory_404(client, db, admin_headers):
    """GET /inventory/<id> returns 404 for nonexistent item."""
    rep = client.get("/api/v1/inventory/99999", headers=admin_headers)
    assert rep.status_code == 404


def test_create_inventory(client, db, admin_headers):
    """POST /inventory creates a new inventory item."""
    product = _create_product(db)
    db.session.commit()

    data = {
        "quantity": 25.0,
        "capacity": 200.0,
        "reorder_level": 5.0,
        "product_id": product.id,
    }

    rep = client.post("/api/v1/inventory", json=data, headers=admin_headers)
    assert rep.status_code == 201

    result = rep.get_json()
    assert result["msg"] == "Inventory created"
    assert result["inventory"]["quantity"] == 25.0
    assert result["inventory"]["capacity"] == 200.0
    assert result["inventory"]["product_id"] == product.id


def test_update_inventory_quantity(client, db, admin_headers):
    """PUT /inventory/<id> updates inventory fields."""
    inventory = _create_inventory(db, quantity=10.0)

    data = {"quantity": 75.0}
    rep = client.put(
        f"/api/v1/inventory/{inventory.id}", json=data, headers=admin_headers
    )
    assert rep.status_code == 200

    result = rep.get_json()
    assert result["msg"] == "inventory updated"
    assert result["inventory"]["quantity"] == 75.0


def test_update_inventory_404(client, db, admin_headers):
    """PUT /inventory/<id> returns 404 for nonexistent item."""
    rep = client.put(
        "/api/v1/inventory/99999", json={"quantity": 1.0}, headers=admin_headers
    )
    assert rep.status_code == 404


def test_delete_inventory(client, db, admin_headers):
    """DELETE /inventory/<id> removes the inventory item."""
    inventory = _create_inventory(db)
    inv_id = inventory.id

    rep = client.delete(f"/api/v1/inventory/{inv_id}", headers=admin_headers)
    assert rep.status_code == 200
    assert rep.get_json()["msg"] == "Inventory deleted"

    assert db.session.get(Inventory, inv_id) is None


def test_delete_inventory_404(client, db, admin_headers):
    """DELETE /inventory/<id> returns 404 for nonexistent item."""
    rep = client.delete("/api/v1/inventory/99999", headers=admin_headers)
    assert rep.status_code == 404
