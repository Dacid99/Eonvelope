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
echo "Starting flower ..."
poetry run celery --broker=amqp://guest:guest@localhost:5672// flower --detach
echo "Successfully started flower."
poetry run python3 manage.py runserver 0.0.0.0:8000 --insecure
