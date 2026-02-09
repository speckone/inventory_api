from flask import Flask, jsonify
from jwt.exceptions import ExpiredSignatureError, DecodeError, InvalidTokenError

from inventory_api_app import auth, api
from inventory_api_app.extensions import db, jwt, migrate, apispec


def create_app(testing=False, cli=False):
    """Application factory, used to create application"""
    app = Flask("inventory_api_app")
    app.config.from_object("inventory_api_app.config")

    if testing is True:
        app.config["TESTING"] = True

    configure_extensions(app, cli)
    configure_apispec(app)
    register_blueprints(app)
    register_apispec_views(app)
    register_error_handlers(app)

    return app


def configure_extensions(app, cli):
    """Configure flask extensions"""
    db.init_app(app)
    jwt.init_app(app)

    # Configure JWT error handlers
    auth.views.configure_jwt_handlers()

    if cli is True:
        migrate.init_app(app, db)


def configure_apispec(app):
    """Configure APISpec for swagger support"""
    apispec.init_app(app, security=[{"jwt": []}])
    apispec.spec.components.security_scheme(
        "jwt", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    )


def register_blueprints(app):
    """Register all blueprints for application"""
    app.register_blueprint(auth.views.blueprint)
    app.register_blueprint(api.views.blueprint)


def register_apispec_views(app):
    """Register apispec views after blueprints are loaded"""
    auth.views.register_apispec_views(app)
    api.views.register_apispec_views(app)


def register_error_handlers(app):
    """Register error handlers for JWT exceptions"""

    @app.errorhandler(ExpiredSignatureError)
    def handle_expired_token(e):
        return jsonify({"msg": "Token has expired"}), 401

    @app.errorhandler(DecodeError)
    def handle_decode_error(e):
        return jsonify({"msg": "Invalid token"}), 401

    @app.errorhandler(InvalidTokenError)
    def handle_invalid_token(e):
        return jsonify({"msg": "Invalid token"}), 401
