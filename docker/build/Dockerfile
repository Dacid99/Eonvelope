FROM python:3.13-alpine3.22
RUN apk update && \
    apk add --no-cache gettext python3-dev linux-headers musl-dev gcc build-base mariadb-connector-c-dev mariadb-dev mariadb-client rabbitmq-server krb5 openssl
WORKDIR /mnt
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    XDG_RUNTIME_DIR=/tmp/xdg_runtime \
    DJANGO_SETTINGS_MODULE='Emailkasten.settings' \
    PYTHONPATH='/mnt/'
COPY ../ /mnt/
RUN openssl req -x509 -newkey rsa:4096 -keyout /mnt/key.pem -out /mnt/cert.pem -days 365 -nodes -subj "/C=DE/ST=Bavaria/L=Munich/O=SBV/OU=Emailkasten/CN=emailkasten.org"
RUN pip install -U --no-cache-dir poetry && poetry install
ENV SECRET_KEY='IM_JUST_HERE_AS_A_WORKAROUND'
RUN poetry run django-admin collectstatic --noinput && \
    poetry run django-admin compilemessages
ENV SECRET_KEY=
RUN chmod +x docker/entrypoint.sh
RUN chmod 777 /var/log
EXPOSE 443
ENTRYPOINT [ "./docker/entrypoint.sh" ]
HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 CMD curl -kf https://localhost:443/health/ || exit 1
