#!/bin/sh
set -e
echo "Waiting for PostgreSQL..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
    echo "PostgreSQL unavailable - sleeping"
    sleep 1
done
echo "PostgreSQL is ready"
echo "Running migrations..."
python manage.py migrate
echo "Starting Daphne..."
exec daphne \
    -b 0.0.0.0 \
    -p 8000 \
    app.asgi:application