#!/bin/sh
poetry run python manage.py migrate
poetry run python manage.py createsuperuser --username=admin --email=  --noinput
poetry run gunicorn Emailkasten.wsgi --bind 0.0.0.0:443 --keyfile=key.pem --certfile=cert.pem
