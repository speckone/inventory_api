from flask import request, jsonify, Blueprint, current_app as app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from inventory_api_app.models import User
from inventory_api_app.extensions import db, pwd_context, jwt, apispec
from inventory_api_app.auth.helpers import revoke_token, is_token_revoked, add_token_to_database
from flask_cors import CORS

blueprint = Blueprint("auth", __name__, url_prefix="/auth")
CORS(blueprint)


@blueprint.route("/login", methods=["POST"])
def login():
    """Authenticate user and return tokens

    ---
    post:
      tags:
        - auth
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: myuser
                  required: true
                password:
                  type: string
                  example: P4$$w0rd!
                  required: true
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                    example: myaccesstoken
                  refresh_token:
                    type: string
                    example: myrefreshtoken
        400:
          description: bad request
      security: []
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if user is None or not pwd_context.verify(password, user.password):
        return jsonify({"msg": "Bad credentials"}), 400

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    add_token_to_database(access_token)
    add_token_to_database(refresh_token)

    ret = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "role": user.role,
        },
    }
    return jsonify(ret), 200


@blueprint.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Get an access token from a refresh token

    ---
    post:
      tags:
        - auth
      parameters:
        - in: header
          name: Authorization
          required: true
          description: valid refresh token
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                    example: myaccesstoken
        400:
          description: bad request
        401:
          description: unauthorized
    """
    current_user = get_jwt_identity()
    user = db.session.get(User, int(current_user))
    access_token = create_access_token(identity=current_user)
    add_token_to_database(access_token)

    ret = {
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "role": user.role,
        },
    }
    return jsonify(ret), 200


@blueprint.route("/revoke_access", methods=["DELETE"])
@jwt_required()
def revoke_access_token():
    """Revoke an access token

    ---
    delete:
      tags:
        - auth
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: token revoked
        400:
          description: bad request
        401:
          description: unauthorized
    """
    jti = get_jwt()["jti"]
    user_identity = get_jwt_identity()
    revoke_token(jti, user_identity)
    return jsonify({"message": "token revoked"}), 200


@blueprint.route("/revoke_refresh", methods=["DELETE"])
@jwt_required(refresh=True)
def revoke_refresh_token():
    """Revoke a refresh token, used mainly for logout

    ---
    delete:
      tags:
        - auth
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: token revoked
        400:
          description: bad request
        401:
          description: unauthorized
    """
    jti = get_jwt()["jti"]
    user_identity = get_jwt_identity()
    revoke_token(jti, user_identity)
    return jsonify({"message": "token revoked"}), 200


def configure_jwt_handlers():
    """Configure JWT error handlers and callbacks"""

    @jwt.user_lookup_loader
    def user_loader_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.get(User, int(identity))

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(_jwt_header, jwt_data):
        return is_token_revoked(jwt_data)

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_data):
        return jsonify({"msg": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"msg": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({"msg": "Missing authorization header"}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(_jwt_header, _jwt_data):
        return jsonify({"msg": "Token has been revoked"}), 401


def register_apispec_views(app):
    with app.app_context():
        apispec.spec.path(view=login, app=app)
        apispec.spec.path(view=refresh, app=app)
        apispec.spec.path(view=revoke_access_token, app=app)
        apispec.spec.path(view=revoke_refresh_token, app=app)
