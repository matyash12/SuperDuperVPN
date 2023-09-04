#!/bin/bash
apt update
apt install -y wireguard


echo "Running makemigrations"
python mysite/manage.py makemigrations

# Apply database migrations
echo "Apply database migrations"
python mysite/manage.py migrate


#collect static for nginx
python mysite/manage.py collectstatic --noinput

# Start server
echo "Starting gunicorn"
(cd mysite; gunicorn mysite.wsgi --bind=0.0.0.0:8000)
#python mysite/manage.py runserver 0.0.0.0:8000