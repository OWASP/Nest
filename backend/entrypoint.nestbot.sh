#!/bin/sh

set -eu

# Allow ALB health checks addressed to the container's private IP.
CONTAINER_IP=$(hostname -i)
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS:-},${CONTAINER_IP}"

exec gunicorn wsgi:application \
  --bind 0.0.0.0:8000 \
  --worker-class gthread \
  --workers "${GUNICORN_WORKERS:-1}" \
  --threads "${GUNICORN_THREADS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --graceful-timeout "${GUNICORN_GRACEFUL_TIMEOUT:-30}" \
  --access-logfile - \
  --error-logfile -
