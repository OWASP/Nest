#!/bin/bash

set -e

python manage.py migrate --fake
python manage.py collectstatic --noinput

gunicorn wsgi:application --bind 0.0.0.0:8000
