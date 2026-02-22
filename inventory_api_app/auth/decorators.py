"""RBAC decorators for protecting API endpoints."""
import logging
from functools import wraps

from flask_jwt_extended import get_jwt_identity, jwt_required  # type: ignore[import-untyped]

from inventory_api_app.extensions import db  # type: ignore[import-untyped]
from inventory_api_app.models import User  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


def admin_required():
    """Decorator that requires the current user to have the 'admin' role.

    Wraps jwt_required() and checks the user's role from the database.
    Returns 403 if the user is not an admin.
    """

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            user = db.session.get(User, int(identity))
            if user is None or user.role != "admin":
                logger.warning("Non-admin user %s attempted admin-only action", identity)
                return {"msg": "Admin access required"}, 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def owner_or_admin(user_id_param="user_id"):
    """Decorator that allows access if the current user is an admin OR owns the resource.

    Checks the URL parameter specified by ``user_id_param`` against the
    current JWT identity.  Admins are always allowed through.  Returns 403
    if the user is neither the owner nor an admin.
    """

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            user = db.session.get(User, int(identity))
            if user is None:
                return {"msg": "User not found"}, 401

            requested_user_id = kwargs.get(user_id_param)
            if user.role == "admin" or (requested_user_id is not None and user.id == requested_user_id):
                return fn(*args, **kwargs)

            logger.warning(
                "User %s attempted to access resource belonging to user %s",
                identity,
                requested_user_id,
            )
            return {"msg": "Access denied"}, 403

        return wrapper

    return decorator
