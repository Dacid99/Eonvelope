FROM python:3.13-alpine3.22

ARG APK_DEPENDENCIES="gettext \
    python3-dev \
    linux-headers \
    musl-dev \
    gcc \
    build-base \
    mariadb-connector-c-dev \
    mariadb-dev \
    mariadb-client \
    rabbitmq-server \
    krb5 \
    openssl \
    curl"
ARG SRC_PATH=/opt/
ARG LOG_PATH=/var/log/emailkasten/

# create directories
RUN mkdir -p ${SRC_PATH}
RUN mkdir -p ${LOG_PATH}

# environment setup
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    XDG_RUNTIME_DIR=/tmp/xdg_runtime \
    DJANGO_SETTINGS_MODULE=Emailkasten.settings \
    PYTHONPATH=${SRC_PATH}'src/'

WORKDIR ${SRC_PATH}
COPY . ${SRC_PATH}

# install dependencies
RUN apk update && \
    apk add --no-cache ${APK_DEPENDENCIES}
RUN pip install -U --no-cache-dir poetry && poetry install

# ssl cert
RUN openssl req -x509 -newkey rsa:4096 -keyout ${SRC_PATH}'key.pem' -out ${SRC_PATH}'cert.pem' -days 365 -nodes -subj "/C=DE/ST=Bavaria/L=Munich/O=SBV/OU=Emailkasten/CN=emailkasten.org"

# src setup
ENV SECRET_KEY=IM_JUST_HERE_AS_A_WORKAROUND
RUN poetry run django-admin collectstatic --noinput && \
    poetry run django-admin compilemessages
ENV SECRET_KEY=

EXPOSE 443

# entrypoint
RUN chmod +x docker/entrypoint.sh
ENTRYPOINT [ "./docker/entrypoint.sh" ]

HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 CMD curl -kf https://localhost:443/health/ || exit 1
