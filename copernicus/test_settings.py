# Settings module for running tests
# Use:  ./manage.py test --settings=copernicus.test_settings

from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

ELASTICSEARCH_DSL = {
    "default": {
        "hosts": os.environ.get("ELASTICSEARCH_TEST_HOST", "elasticsearch_test"),
        "http_auth": os.environ.get("ELASTICSEARCH_TEST_AUTH", "user:password"),
    },
}

USE_CASES_FEATURE_TOGGLE = True

SECRET_KEY = "app_tests_secret_key"

LOGGING_CSV_FILENAME = "test-user-actions.csv"
LOGGING_CSV_PATH = os.path.join(BASE_DIR, "logging", LOGGING_CSV_FILENAME)

API_TOKEN = env("API_TOKEN", default="token")
API_PREFIX = env("API_PREFIX", default="Token")
