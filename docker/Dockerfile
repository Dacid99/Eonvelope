FROM python:3.13-rc-bookworm
RUN apt-get -y update && apt-get -y install gettext build-essential default-mysql-client krb5-user krb5-multidev
WORKDIR /mnt
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV XDG_RUNTIME_DIR=/tmp/xdg_runtime
ENV PYTHONPATH=/mnt/Emailkasten
COPY ../ /mnt/
RUN pip install -U --no-cache-dir poetry
RUN poetry install
RUN poetry run python manage.py collectstatic --noinput
RUN poetry run python manage.py makemigrations
RUN poetry run python manage.py compilemessages
RUN chmod +x docker/entrypoint.sh
EXPOSE 8000
ENTRYPOINT [ "./docker/entrypoint.sh" ]
HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/health/ || exit 1
