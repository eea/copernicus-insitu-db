# Settings module for running tests
# Use:  ./manage.py test --settings=copernicus.testsettings

from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

SECRET_KEY = 'app_tests_secret_key'

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'elasticsearch',
        'http_auth': 'elastic:changeme',
    },
}