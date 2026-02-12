from sqlalchemy import event

from inventory_api_app.extensions import db, pwd_context


class User(db.Model):
    """Basic user model
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return "<User %s>" % self.username


@event.listens_for(User.password, "set", retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value and not value.startswith("$pbkdf2-sha256$"):
        return pwd_context.hash(value)
    return value
