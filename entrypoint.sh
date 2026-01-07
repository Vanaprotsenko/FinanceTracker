#!/bin/bash

# Run migrations
alembic upgrade head

# Start the application
exec "$@"
