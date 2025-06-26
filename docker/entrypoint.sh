#!/bin/sh
poetry run python manage.py migrate
poetry run python manage.py createsuperuser --username=admin --email=  --noinput
echo "Starting rabbitmq ..."
rabbitmq-server -detached
echo "Successfully started rabbitmq."
echo "Starting celery worker ..."
poetry run celery -A Emailkasten worker --loglevel=${CELERY_LOG_LEVEL} --detach
echo "Successfully started celery worker."
echo "Starting celery beat ..."
poetry run celery -A Emailkasten beat --loglevel=${CELERY_LOG_LEVEL} -S django --detach
echo "Successfully started celery beat."
poetry run gunicorn Emailkasten.wsgi --bind 0.0.0.0:443 --keyfile=key.pem --certfile=cert.pem
