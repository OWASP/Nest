#!/bin/sh

python manage.py migrate
python manage.py collectstatic --noinput

# Load initial data
python manage.py load_data

pytest fuzz_tests

python manage.py runserver 0.0.0.0:8000
