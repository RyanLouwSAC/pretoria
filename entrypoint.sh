#!/bin/sh

# Apply database migrations
python manage.py migrate

# Run custom command to create superuser
python manage.py createAdminuser


# Start server
exec "$@"
