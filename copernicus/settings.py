"""
Django settings for copernicus project.

Generated by 'django-admin startproject' using Django 1.11.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import environ
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

env = environ.Env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="secret")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", default=False)
DEBUG_TOOLBAR = env("DEBUG_TOOLBAR", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default="localhost,127.0.0.1")

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Sentry
SENTRY_DSN = env("SENTRY_DSN", default="")
SENTRY_TAG_RELEASE = env("SENTRY_TAG_RELEASE", default="")
SENTRY_TAG_ENVIRONMENT = env("SENTRY_TAG_ENVIRONMENT", default="")
SENTRY_TAG_SITE = env("SENTRY_TAG_SITE", default="")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN, release=SENTRY_TAG_RELEASE, integrations=[DjangoIntegration()]
    )

    SENTRY_AUTH_TOKEN = env("SENTRY_AUTH_TOKEN", default="")
    SENTRY_API_URL = env("SENTRY_API_URL", default="")

# Application definition

INSTALLED_APPS = [
    "markdownx",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_elasticsearch_dsl",
    "django_filters",
    "bootstrap3",
    "django_advance_thumbnail",
    "django_fsm",
    "hijack",
    "hijack.contrib.admin",
    "docs",
    "guardian",
    "explorer",
    "wkhtmltopdf",
    "picklists",
    "insitu",
    "use_cases",
]

if not DEBUG:
    import os

    INSTALLED_APPS += [
        "raven.contrib.django.raven_compat",
    ]

    RAVEN_CONFIG = {
        "dsn": env("SENTRY_DSN", default=None),
    }

if DEBUG_TOOLBAR:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]

MIDDLEWARE = [
    "csp.middleware.CSPMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "insitu.middleware.sentry_middleware",
    "hijack.middleware.HijackUserMiddleware",
]

if DEBUG_TOOLBAR:
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

ROOT_URLCONF = "copernicus.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.static",
                "django.template.context_processors.media",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "insitu.context_processors.base",
                "insitu.context_processors.matomo",
                "insitu.context_processors.crazy_egg",
                "insitu.context_processors.sentry",
            ],
            "libraries": {
                "js": "insitu.views.product",
            },
        },
    },
]
WKHTMLTOPDF_CMD = "/usr/bin/wkhtmltopdf"
WSGI_APPLICATION = "copernicus.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env("POSTGRES_HOST", default="db"),
        "PORT": 5432,
        "NAME": env("POSTGRES_DB", default="insitu"),
        "USER": env("POSTGRES_USER", default="demo"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="demo"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
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

READ_ONLY_GROUP = env("READ_ONLY_GROUP", default="ReadOnly")
PRODUCT_EDITOR_GROUP = env("PRODUCT_EDITOR_GROUP", default="ProductEditor")
PICKLISTS_EDITOR_GROUP = env("PICKLISTS_EDITOR_GROUP", default="PicklistsEditor")
USE_CASES_PUBLISHER_GROUP = env(
    "USE_CASES_PUBLISHER_GROUP", default="UseCasesPublisher"
)

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = env("TZ", default="Europe/Copenhagen")

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "..", "static/")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "..", "static/media/")

ELASTICSEARCH_DSL = {
    "default": {
        "hosts": env("ELASTICSEARCH_HOST", default="elasticsearch"),
        "http_auth": os.environ.get("ELASTICSEARCH_AUTH", "user:password"),
        "timeout": int(os.environ.get("ELASTICSEARCH_TIMEOUT", 120)),
    },
}

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",  # default
    "guardian.backends.ObjectPermissionBackend",
)

MAX_RESULT_WINDOW = 10000  # This is ElasticSearch's default, but we define it
# here explicitly to minimize refactoring in case we ever change it.

LOGGING_CSV_FILENAME = os.environ.get(
    "LOGGING_CSV_FILENAME", "user-actions-logging.csv"
)
LOGGING_CSV_PATH = os.path.join(BASE_DIR, "logging", LOGGING_CSV_FILENAME)

MATOMO = os.environ.get("MATOMO", False)

CRAZY_EGG = os.environ.get("CRAZY_EGG", "")


# Hijack customization

HIJACK_LOGIN_REDIRECT_URL = "/"
HIJACK_LOGOUT_REDIRECT_URL = "/"
HIJACK_ALLOW_GET_REQUESTS = True
HIJACK_INSERT_BEFORE = "</body>"

LOGIN_REDIRECT_URL = "/"

SUPPORT_EMAIL = os.environ.get("SUPPORT_EMAIL", "")

EXPLORER_CONNECTIONS = {"Default": "default"}
EXPLORER_DEFAULT_ROWS = 50000
EXPLORER_SQL_WHITELIST = {
    "update_frequency",
    "_deleted",
    "Update Frequency",
    "picklists_updatefrequency",
    "Data updated",
    "data_updated",
}

USE_CASES_FEATURE_TOGGLE = os.environ.get("USE_CASES_FEATURE_TOGGLE", False)


def EXPLORER_PERMISSION_VIEW(request):
    return request.user.is_authenticated


EXPLORER_DEFAULT_CONNECTION = "default"
EXPLORER_SCHEMA_EXCLUDE_TABLE_PREFIXES = [
    "auth_group",
    "auth_group_permissions",
    "auth_permission",
    "auth_user_groups",
    "auth_user_user_permissions",
    "django_admin_log",
    "django_content_type",
    "django_migrations",
    "django_session",
    "explorer_query",
    "explorer_querylog",
]

DOCS_ROOT = os.path.join(BASE_DIR, "docs/_build/html")
DOCS_PDF_ROOT = os.path.join(BASE_DIR, "docs/_build/latex")

DOCS_ACCESS = "login_required"

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "postfix")
EMAIL_PORT = os.environ.get("EMAIL_PORT", 25)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "")

SITE_URL = os.environ.get("SITE_URL", "")

if DEBUG_TOOLBAR:
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": "copernicus.settings.show_toolbar",
        # Rest of config
    }
    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda _request: True}
    INTERNAL_IPS = [
        # ...
        "127.0.0.1",
        # ...
    ]


# Content Security Policy
CSP_IMG_SRC = "'self'"
CSP_STYLE_SRC = (
    "'self'",
    "http://cdnjs.cloudflare.com",
    "http://code.jquery.com",
    "http://maxcdn.bootstrapcdn.com",
)
CSP_SCRIPT_SRC = (
    "'self'",
    "http://cdnjs.cloudflare.com",
    "http://code.jquery.com",
    "https://matomo.eea.europa.eu",
    "cdn.ravenjs.com",
)
CSP_INCLUDE_NONCE_IN = ["script-src", "style-src"]
