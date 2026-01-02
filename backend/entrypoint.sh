#!/bin/sh

set -e

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py clear_cache

gunicorn wsgi:application --bind 0.0.0.0:8000
