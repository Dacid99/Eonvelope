#!/bin/sh
poetry run python manage.py migrate
poetry run python manage.py createsuperuser --username=admin --email=  --noinput
echo "Starting rabbitmq ..."
rabbitmq-server -detached
echo "Successfully started rabbitmq."
echo "Starting celery worker ..."
poetry run celery -A src.Emailkasten worker --loglevel=${CELERY_LOG_LEVEL} --detach
echo "Successfully started celery worker."
echo "Starting celery beat ..."
poetry run celery -A src.Emailkasten beat --loglevel=${CELERY_LOG_LEVEL} -S django --detach
echo "Successfully started celery beat."
poetry run gunicorn src.Emailkasten.wsgi --bind 0.0.0.0:443 --keyfile=key.pem --certfile=cert.pem --workers=${GUNICORN_WORKER_NUMBER:-1} --access-logfile "/var/log/gunicorn_access.log"
