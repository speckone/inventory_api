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

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
