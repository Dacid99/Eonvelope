#!/bin/bash
poetry run python manage.py migrate
poetry run python manage.py createsuperuser --username=admin --email=  --noinput
poetry run python manage.py runserver 0.0.0.0:8000
