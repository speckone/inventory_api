from flask import url_for  # type: ignore[unresolved-import]
from inventory_api_app.models import User  # type: ignore[unresolved-import]


def test_get_user(client, db, user, admin_headers):
    # test 404
    user_url = url_for('api.user_by_id', user_id="100000")
    rep = client.get(user_url, headers=admin_headers)
    assert rep.status_code == 404

    db.session.add(user)
    db.session.commit()

    # test get_user
    user_url = url_for('api.user_by_id', user_id=user.id)
    rep = client.get(user_url, headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()["user"]
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["active"] == user.active


def test_put_user(client, db, user, admin_headers):
    # test 404
    user_url = url_for('api.user_by_id', user_id="100000")
    rep = client.put(user_url, headers=admin_headers)
    assert rep.status_code == 404

    db.session.add(user)
    db.session.commit()

    data = {"username": "updated"}

    user_url = url_for('api.user_by_id', user_id=user.id)
    # test update user
    rep = client.put(user_url, json=data, headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()["user"]
    assert data["username"] == "updated"
    assert data["email"] == user.email
    assert data["active"] == user.active


def test_delete_user(client, db, user, admin_headers):
    # test 404
    user_url = url_for('api.user_by_id', user_id="100000")
    rep = client.delete(user_url, headers=admin_headers)
    assert rep.status_code == 404

    db.session.add(user)
    db.session.commit()

    # test get_user

    user_url = url_for('api.user_by_id', user_id=user.id)
    rep = client.delete(user_url,  headers=admin_headers)
    assert rep.status_code == 200
    assert db.session.query(User).filter_by(id=user.id).first() is None


def test_create_user(client, db, admin_headers):
    # test bad data
    users_url = url_for('api.users')
    data = {"username": "created"}
    rep = client.post(users_url, json=data, headers=admin_headers)
    assert rep.status_code == 400

    data["password"] = "admin"
    data["email"] = "create@mail.com"

    rep = client.post(users_url, json=data, headers=admin_headers)
    assert rep.status_code == 201

    data = rep.get_json()
    user = db.session.query(User).filter_by(id=data["user"]["id"]).first()

    assert user.username == "created"
    assert user.email == "create@mail.com"


def test_get_all_user(client, db, user_factory, admin_headers):
    users_url = url_for('api.users')
    users = user_factory.create_batch(30)

    db.session.add_all(users)
    db.session.commit()

    rep = client.get(users_url, headers=admin_headers)
    assert rep.status_code == 200

    results = rep.get_json()
    for user in users:
        assert any(u["id"] == user.id for u in results["results"])


# --- Authorization / RBAC tests ---


def test_non_admin_cannot_get_user_list(client, db, regular_headers):
    """Non-admin user should get 403 when accessing user list."""
    users_url = url_for('api.users')
    rep = client.get(users_url, headers=regular_headers)
    assert rep.status_code == 403


def test_non_admin_cannot_delete_other_user(client, db, user, regular_headers):
    """Non-admin user should get 403 when deleting another user."""
    db.session.add(user)
    db.session.commit()

    user_url = url_for('api.user_by_id', user_id=user.id)
    rep = client.delete(user_url, headers=regular_headers)
    assert rep.status_code == 403

    # verify user was NOT deleted
    assert db.session.query(User).filter_by(id=user.id).first() is not None


def test_user_can_get_own_profile(client, db, regular_user, regular_headers):
    """A user should be able to GET their own profile."""
    user_url = url_for('api.user_by_id', user_id=regular_user.id)
    rep = client.get(user_url, headers=regular_headers)
    assert rep.status_code == 200

    data = rep.get_json()["user"]
    assert data["username"] == regular_user.username
    assert data["email"] == regular_user.email


def test_user_cannot_put_other_user_profile(client, db, user, regular_headers):
    """A non-admin user should get 403 when updating another user's profile."""
    db.session.add(user)
    db.session.commit()

    user_url = url_for('api.user_by_id', user_id=user.id)
    rep = client.put(user_url, json={"username": "hacked"}, headers=regular_headers)
    assert rep.status_code == 403

    # verify user was NOT modified
    unchanged = db.session.query(User).filter_by(id=user.id).first()
    assert unchanged.username != "hacked"
