from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent.parent  # points to project root (where manage.py is)


# Application definition
INSTALLED_APPS = [
    "widget_tweaks",
    "users.apps.UsersConfig",
    "services.apps.ServicesConfig",
    "messaging.apps.MessagingConfig",
    "contact.apps.ContactConfig",
    "storages",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "analytics.apps.AnalyticsConfig",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "users.middleware.UpdateLastSeenMiddleware",
]


ROOT_URLCONF = "handyhub.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "messaging.context_processors.unread_message_count",
            ],
        },
    },
]


WSGI_APPLICATION = "handyhub.wsgi.application"


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


AUTHENTICATION_BACKENDS = [
    "users.backends.UsernameOrEmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"


# Media uploads
MEDIA_ROOT = BASE_DIR / "pictures"
MEDIA_URL = "/profile_picture/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Auth redirects
LOGIN_REDIRECT_URL = "users:post_login"
LOGIN_URL = "users:login"