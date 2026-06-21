#!/bin/bash

# Script to create initial database migrations
echo "Creating Django migrations..."
docker-compose exec -T backend python manage.py makemigrations

echo "Running migrations..."
docker-compose exec -T backend python manage.py migrate

echo "✓ Database initialization complete"
