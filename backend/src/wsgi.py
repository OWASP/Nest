"""WSGI config for OWASP Nest project."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.local")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

from configurations.wsgi import get_wsgi_application

application = get_wsgi_application()
