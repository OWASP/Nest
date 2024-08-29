"""WSGI config for OWASP Nest project."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Staging")

from configurations.wsgi import get_wsgi_application

application = get_wsgi_application()
