"""Default configuration

Use env var to override
"""
import os
from dotenv import load_dotenv

load_dotenv()


DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise RuntimeError(
        "SECRET_KEY environment variable must be set and at least 32 characters long."
    )

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")

MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT", "465"))
MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "1") == "1"
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
MAIL_ORDER_RECIPIENT = os.getenv("MAIL_ORDER_RECIPIENT")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
