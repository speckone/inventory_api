"""Default configuration

Use env var to override
"""
import os
from dotenv import load_dotenv

load_dotenv()


DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
SECRET_KEY = os.getenv("SECRET_KEY")

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")

FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_HOST = os.getenv("EMAIL_HOST")
