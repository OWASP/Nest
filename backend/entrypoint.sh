#!/bin/sh

set -e

# Add container's private IP to ALLOWED_HOSTS for ALB health checks.
CONTAINER_IP=$(hostname -i)
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS},${CONTAINER_IP},localhost"

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py clear_cache

gunicorn wsgi:application \
  --access-logfile - \
  --bind 0.0.0.0:8000 \
  --error-logfile - \
  --graceful-timeout "${GUNICORN_GRACEFUL_TIMEOUT:-60}" \
  --max-requests "${GUNICORN_MAX_REQUESTS:-1000}" \
  --max-requests-jitter "${GUNICORN_MAX_REQUESTS_JITTER:-50}" \
  --threads "${GUNICORN_THREADS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --workers "${GUNICORN_WORKERS:-3}"
