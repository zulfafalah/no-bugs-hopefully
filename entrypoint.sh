#!/bin/sh

echo "Starting Django application..."

# Run migrations
python manage.py migrate --noinput

# Create superuser if it doesn't exist (optional)
# python manage.py createsuperuser --noinput --username admin --email admin@example.com || true

# Collect static files
python manage.py collectstatic --noinput

echo "Django setup complete!"

# Start server
exec "$@"
