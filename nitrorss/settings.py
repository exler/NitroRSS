from pathlib import Path

import dj_database_url
import sentry_sdk
from django.contrib.messages import constants as message_constants
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

from nitrorss.utils.env import (
    get_env_bool,
    get_env_float,
    get_env_int,
    get_env_list,
    get_env_str,
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = get_env_str("DJANGO_SECRET_KEY", "secretkey")

DEBUG = get_env_bool("DJANGO_DEBUG", False)

ALLOWED_HOSTS = get_env_list("DJANGO_ALLOWED_HOSTS")

INTERNAL_IPS = get_env_list("DJANGO_INTERNAL_IPS", ["127.0.0.1"])

BASE_URL = get_env_str("BASE_URL")

# Application definition

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "debug_toolbar",
    "django_q",
    "nitrorss",
    "mailer",
    "users",
    "feeds",
    "subscriptions",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "compressor",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if not DEBUG:
    sentry_dsn = get_env_str("SENTRY_DSN")
    sentry_env = get_env_str("SENTRY_ENV")
    if sentry_dsn and sentry_env:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=sentry_env,
            integrations=[DjangoIntegration()],
            send_default_pii=True,
            attach_stacktrace=True,
            traces_sample_rate=get_env_float("SENTRY_TRACES_SAMPLE_RATE", "0.0"),
        )

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        }
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}


ROOT_URLCONF = "nitrorss.urls"

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
                "nitrorss.context_processors.base_url_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "nitrorss.wsgi.application"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]
STATICFILES_DIRS = [
    BASE_DIR / "nitrorss" / "static",
]

COMPRESS_OFFLINE = not DEBUG
COMPRESS_STORAGE = "compressor.storage.BrotliCompressorFileStorage"

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
# https://github.com/jazzband/dj-database-url

DATABASES = {"default": dj_database_url.config(conn_max_age=600)}

# Caches

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unlovable-nervous-system",
    }
}

# Django Q

Q_CLUSTER = {
    "name": "nitrorss",
    "workers": 2,
    "timeout": 30,
    "retry": 60,
    "catch_up": False,
    "compress": False,
    "queue_limit": 20,
    "bulk": 10,
    "orm": "default",
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# CSRF

CSRF_TRUSTED_ORIGINS = get_env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

# Authentication

AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ["users.backends.EmailVerificationRequiredBackend"]

# Emails

DEFAULT_FROM_EMAIL = get_env_str("DEFAULT_FROM_EMAIL")
EMAIL_BACKEND = "mailer.backend.DatabaseBackend"
EMAIL_HOST = get_env_str("EMAIL_HOST")
EMAIL_PORT = get_env_int("EMAIL_PORT")
EMAIL_HOST_USER = get_env_str("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = get_env_str("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = get_env_bool("EMAIL_USE_TLS", True)
EMAIL_TIMEOUT = get_env_int("EMAIL_TIMEOUT", 10)

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Messages

MESSAGE_TAGS = {
    message_constants.SUCCESS: "success",
    message_constants.ERROR: "danger",
    message_constants.WARNING: "warning",
    message_constants.INFO: "info",
    message_constants.DEBUG: "secondary",
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
