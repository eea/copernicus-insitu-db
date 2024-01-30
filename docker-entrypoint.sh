#!/bin/sh

set -e

# create directory for static and protected files
mkdir -p /var/local/static/protected

while ! nc -z "$POSTGRES_HOST" 5432; do
  echo "Waiting for PostgreSQL server at 5432 to accept connections on port 5432..."
  sleep 1s
done

if [ -z "$TIMEOUT" ]; then
    TIMEOUT=30
fi

if [ "x$DJANGO_MIGRATE" = 'xyes' ]; then
    python manage.py migrate --noinput
    python manage.py loaddata explorer
fi

if [ "x$DJANGO_COLLECT_STATIC" = "xyes" ]; then
  python manage.py collectstatic --noinput
fi

if [ "x$DJANGO_INDEX_CONTENT" = "xyes" ]; then
  python manage.py search_index -f --rebuild
fi


if [ -z "$1" ]; then
  uwsgi uwsgi.ini
fi

exec python manage.py $@
