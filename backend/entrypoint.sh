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


echo "Starting Gunicorn with Daphne workers..."


exec gunicorn \
    app.asgi:application \
    --bind 0.0.0.0:8000 \
    --worker-class daphne.worker.DaphneWorker \
    --workers 4 \
    --timeout 120