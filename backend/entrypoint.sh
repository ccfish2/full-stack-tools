#!/bin/sh

# Wait for database to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! nc -z $DB_HOST $DB_PORT; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL is up"

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser (if needed)..."
python manage.py shell << END
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser 'admin' created")
else:
    print("Superuser already exists")
END

# Start the server
# NOTE: runserver is sync/WSGI and will hang on the streaming SSE response.
# Daphne serves app.asgi:application, which is what actually makes the
# /api/events/ StreamingHttpResponse work without blocking the worker.
echo "Starting Daphne (ASGI)..."
daphne -b 0.0.0.0 -p 8000 app.asgi:application
