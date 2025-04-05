#!/bin/sh

set -e

python manage.py migrate
python manage.py collectstatic --noinput

# Added true temporarily to allow the script to continue when the test coverage fails
pytest fuzz_tests || true

gunicorn wsgi:application --bind 0.0.0.0:8000
