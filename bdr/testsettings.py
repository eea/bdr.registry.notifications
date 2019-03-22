# Settings module for running tests
# Use:  python manage.py test --settings=bdr.testsettings

from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

ASYNC_EMAILS = False
ALLOW_EDITING_COMPANIES = True

SECRET_KEY = 'app_tests_secret_key'
