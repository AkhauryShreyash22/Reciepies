#!/bin/sh

echo "Running Django migrations..."
python recipies/manage.py migrate

echo "Starting Django..."
exec "$@"
