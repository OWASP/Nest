#!/bin/sh

set -e

# Add container's private IP to ALLOWED_HOSTS for ALB health checks.
CONTAINER_IP=$(hostname -i)
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS},${CONTAINER_IP}"

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py clear_cache

gunicorn wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-4}" \
  --threads "${GUNICORN_THREADS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-30}" \
  --graceful-timeout "${GUNICORN_GRACEFUL_TIMEOUT:-30}" \
  --max-requests "${GUNICORN_MAX_REQUESTS:-1000}" \
  --max-requests-jitter "${GUNICORN_MAX_REQUESTS_JITTER:-50}" \
  --access-logfile - \
  --error-logfile -
