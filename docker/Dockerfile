# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright © 2024 David Aderbauer & The Emailkasten Contributors

FROM python:3.13-alpine

ARG APK_DEPENDENCIES="gettext \
    python3-dev \
    linux-headers \
    musl-dev \
    build-base \
    mariadb-connector-c-dev \
    mariadb-dev \
    mariadb-client \
    rabbitmq-server \
    openssl \
    curl \
    xz"
ARG SRC_PATH=/opt/
ARG LOG_PATH=/var/log/emailkasten/

# create directories
RUN mkdir -p ${SRC_PATH} && mkdir -p ${LOG_PATH} && mkdir -p /etc/s6-overlay

# environment setup
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    XDG_RUNTIME_DIR=/tmp/xdg_runtime \
    DJANGO_SETTINGS_MODULE=Emailkasten.settings \
    PYTHONPATH=${SRC_PATH}'src/'

LABEL org.opencontainers.image.authors="David Aderbauer & The Emailkasten Contributors <18516197-Dacid99@users.noreply.gitlab.com>"
LABEL org.opencontainers.image.documentation="https://emailkasten.readthedocs.io"
LABEL org.opencontainers.image.source="https://gitlab.com/Dacid99/emailkasten"
LABEL org.opencontainers.image.url="https://gitlab.com/Dacid99/emailkasten"
LABEL org.opencontainers.image.licenses="AGPL-3.0-or-later"
LABEL org.opencontainers.image.description="An email-archiving server using the django framework"
LABEL org.opencontainers.image.title="Emailkasten Server"

WORKDIR ${SRC_PATH}
COPY ./ ${SRC_PATH}
COPY ./docker/s6-overlay /etc/s6-overlay
RUN find /etc/s6-overlay -type f -name run -exec chmod +x {} \;

# install dependencies
RUN apk update && \
    apk add --no-cache ${APK_DEPENDENCIES}
RUN pip install -U --no-cache-dir poetry && poetry install

# install s6-overlay
ARG S6_OVERLAY_VERSION=3.2.1.0
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-x86_64.tar.xz

# ssl cert
RUN openssl req -x509 -newkey rsa:4096 -keyout ${SRC_PATH}'key.pem' -out ${SRC_PATH}'cert.pem' -days 365 -nodes -subj "/C=DE/ST=Bavaria/L=Munich/O=SBV/OU=Emailkasten/CN=emailkasten.org"

# src setup
ENV SECRET_KEY=IM_JUST_HERE_AS_A_WORKAROUND
RUN poetry run django-admin collectstatic --noinput && \
    poetry run django-admin compilemessages
ENV SECRET_KEY=

EXPOSE 443

# entrypoint

ENTRYPOINT [ "/init" ]

HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 CMD curl -kf https://localhost:443/health/ || exit 1
