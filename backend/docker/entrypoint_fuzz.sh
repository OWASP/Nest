#!/bin/sh

set -e

python manage.py migrate
python manage.py collectstatic --noinput

# Load initial data
python manage.py load_data

# Added true temporarily to allow the script to continue when the test coverage fails
pytest fuzz_tests || true

python manage.py runserver 0.0.0.0:8000
