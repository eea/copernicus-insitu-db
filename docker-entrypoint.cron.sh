#!/bin/sh

set -e

while ! nc -z db 5432; do
  echo "Waiting for PostgreSQL server at 5432 to accept connections on port 5432..."
  sleep 1s
done

# Update crontab
crontab -u root crontab

# Start crontab service
/usr/sbin/crond -f
