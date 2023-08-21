#!/bin/bash

# Collect static files
echo "Collect static files"
python mysite/manage.py makemigrations

# Apply database migrations
echo "Apply database migrations"
python mysite/manage.py migrate

# Start server
echo "Starting server"
python mysite/manage.py runserver 0.0.0.0:8000