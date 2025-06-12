#!/bin/sh
poetry run python manage.py migrate
poetry run python manage.py createsuperuser --username=admin --email=  --noinput
rabbitmq-server -detached
poetry run celery -A Emailkasten worker --loglevel=info --detach
poetry run celery -A Emailkasten beat --loglevel=info -S django --detach
