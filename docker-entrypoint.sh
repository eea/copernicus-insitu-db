#!/bin/bash

set -e

if [ -z "$POSTGRES_ADDR" ]; then
    POSTGRES_ADDR="postgres"
fi

while ! nc -z $POSTGRES_ADDR 5432; do
  echo "Waiting for PostgreSQL server at '$POSTGRES_ADDR' to accept connections..."
  sleep 3s
done

if [ -z "$TIMEOUT" ]; then
    TIMEOUT=30
fi

if [ -z "$1" ]; then
  python manage.py migrate &&
  python manage.py collectstatic --noinput &&
  exec gunicorn copernicus.wsgi:application \
         --name insitu \
         --bind 0.0.0.0:8000 \
         --workers 3 \
         --timeout $TIMEOUT \
         --access-logfile - \
         --error-logfile -
fi
