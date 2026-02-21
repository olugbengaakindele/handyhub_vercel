from .base import *
import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
from decouple import config


load_dotenv()  # this reads the .env file
DEBUG = False

# For local dev, a fallback key is okay (but best to set env var)
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-unsafe-secret-key")

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")

# Usually not needed locally unless you're testing https/domains
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if os.environ.get("CSRF_TRUSTED_ORIGINS") else []

# ✅ Your current local DB (SQL Server) - keep for now


# ✅ Your current local DB (SQL Server) - keep for now
DEBUG = False

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ["DATABASE_URL"],
        conn_max_age=600,
        ssl_require=True,
    )
}


# Email - safer local option (prints emails to console)
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "LocalTradePros <noreply@local>")
# Email (env-based)
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "LocalTradePros <noreply@localtradespro.ca>")

