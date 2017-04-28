"""
WSGI config for bdr project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bdr.settings")

application = get_wsgi_application()

HEADER_MAP = {
    'REMOTE_ADDR': 'HTTP_X_FORWARDED_FOR',
    'SCRIPT_NAME': 'HTTP_X_FORWARDED_SCRIPT_NAME',
    'HTTP_HOST': 'HTTP_X_FORWARDED_HOST',
    'wsgi.url_scheme': 'HTTP_X_FORWARDED_SCHEME',
}

def proxy_middleware(app):
    def proxy_fix(environ, start_response):
        for name in HEADER_MAP:
            value = environ.get(HEADER_MAP[name])
            if value:
                environ[name] = value

        return app(environ, start_response)

    return proxy_fix

if settings.APP_REVERSE_PROXY:
    application = proxy_middleware(application)
