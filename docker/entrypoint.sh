#!/bin/sh
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright © 2024 David Aderbauer & The Emailkasten Contributors

poetry run python manage.py migrate
poetry run python manage.py createsuperuser --username=admin --email=  --noinput
echo "Starting rabbitmq ..."
rabbitmq-server -detached
echo "Successfully started rabbitmq."
echo "Starting celery worker ..."
poetry run celery -A src.Emailkasten worker --loglevel=${CELERY_LOG_LEVEL:-INFO} --detach
echo "Successfully started celery worker."
echo "Starting celery beat ..."
poetry run celery -A src.Emailkasten beat --loglevel=${CELERY_LOG_LEVEL:-INFO} -S django --detach
echo "Successfully started celery beat."
poetry run gunicorn src.Emailkasten.wsgi --bind 0.0.0.0:443 --keyfile=key.pem --certfile=cert.pem --workers=${GUNICORN_WORKER_NUMBER:-1} --access-logfile "/var/log/gunicorn_access.log"
