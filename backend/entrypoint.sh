#!/bin/sh

set -e

# Add container's private IP to ALLOWED_HOSTS for ALB health checks.
CONTAINER_IP=$(hostname -i)
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS},${CONTAINER_IP}"

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py clear_cache

gunicorn wsgi:application --bind 0.0.0.0:8000
