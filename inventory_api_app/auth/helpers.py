"""Various helpers for auth. Mainly about token blocklisting."""
from datetime import datetime, timezone

from flask_jwt_extended import decode_token
from sqlalchemy.orm.exc import NoResultFound

from inventory_api_app.extensions import db
from inventory_api_app.models import TokenBlacklist


def add_token_to_database(encoded_token):
    """Adds a new token to the database. It is not revoked when it is added."""
    decoded_token = decode_token(encoded_token)
    jti = decoded_token["jti"]
    token_type = decoded_token["type"]
    user_identity = int(decoded_token["sub"])
    expires = datetime.fromtimestamp(decoded_token["exp"], tz=timezone.utc)
    revoked = False

    db_token = TokenBlacklist(
        jti=jti,
        token_type=token_type,
        user_id=user_identity,
        expires=expires,
        revoked=revoked,
    )
    db.session.add(db_token)
    db.session.commit()


def is_token_revoked(decoded_token):
    """
    Checks if the given token is revoked or not. Because we are adding all the
    tokens that we create into this database, if the token is not present
    in the database we are going to consider it revoked, as we don't know where
    it was created.
    """
    jti = decoded_token["jti"]
    try:
        token = TokenBlacklist.query.filter_by(jti=jti).one()
        return token.revoked
    except NoResultFound:
        return True


def revoke_token(token_jti, user):
    """Revokes the given token

    Since we use it only on logout that already require a valid access token,
    if token is not found we raise an exception
    """
    try:
        token = TokenBlacklist.query.filter_by(jti=token_jti, user_id=int(user)).one()
        token.revoked = True
        db.session.commit()
    except NoResultFound:
        raise Exception(f"Could not find the token {token_jti}")
