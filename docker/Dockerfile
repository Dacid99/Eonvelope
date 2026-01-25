# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright © 2024 David Aderbauer & The Eonvelope Contributors

ARG PYTHON_VERSION=3.14
ARG ALPINE_VERSION=3.23
ARG S6_OVERLAY_VERSION=3.2.1.0

ARG RUNTIME_APK_DEPENDENCIES="curl \
    rabbitmq-server \
    mariadb-client \
    mariadb-connector-c"

ARG BUILD_PYTHON_APK_DEPENDENCIES="python3-dev \
    linux-headers \
    musl-dev \
    gcc \
    mariadb-dev"

ARG BUILD_DJANGO_APK_DEPENDENCIES="gettext"

ARG STORAGE_PATH=/mnt/archive/  # must match STORAGE_PATH in settings.py
ARG LOG_PATH=/var/log/eonvelope/  # must match LOG_DIRECTORY_PATH in settings.py


##    stage 1    ##
## convert pyproject.toml to requirements file for python dependencies ##
## no cleanup required ##

FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION} AS poetry-prestage

WORKDIR /

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir poetry && \
    poetry self add poetry-plugin-export && \
    poetry export -f requirements.txt > /requirements.txt


##   stage 2   ##
## download and unpack s6-overlay ##
## no cleanup required ##

FROM alpine:${ALPINE_VERSION} AS s6-overlay-prestage

ARG S6_OVERLAY_VERSION

WORKDIR /tmp

# install s6-overlay
ARG TARGETARCH
ARG TARGETVARIANT

ARG BUILD_S6_APK_DEPENDENCIES="curl xz"

RUN apk add --no-cache ${BUILD_S6_APK_DEPENDENCIES} && \
    S6_ARCH="" && \
    if [ "${TARGETARCH}""${TARGETVARIANT}" = "amd64" ]; then S6_ARCH="x86_64"; \
    elif [ "${TARGETARCH}""${TARGETVARIANT}" = "arm64" ]; then S6_ARCH="aarch64"; fi && \
    if [ -z "${S6_ARCH}" ]; then { echo "Error: Not able to determine target platform"; exit 1; }; fi && \
    curl --fail --silent --no-progress-meter --show-error --location --remote-name-all --parallel --parallel-max 4 \
    "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz" \
    "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz.sha256" \
    "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${S6_ARCH}.tar.xz" \
    "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${S6_ARCH}.tar.xz.sha256" && \
    sha256sum -c ./*.sha256 && \
    mkdir -p /s6-overlay && \
    tar --directory /s6-overlay -Jxpf "s6-overlay-noarch.tar.xz" && \
    tar --directory /s6-overlay -Jxpf "s6-overlay-${S6_ARCH}.tar.xz"


##   stage 3  -  amd64  ##
## build django translation and staticfiles ##
## no cleanup required ##

# hadolint ignore=DL3029 # required to fix arm64 build
FROM --platform=linux/amd64 python:${PYTHON_VERSION}-alpine${ALPINE_VERSION} AS django-prestage

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=src/ \
    DJANGO_SETTINGS_MODULE=config.settings \
    SECRET_KEY=IM_JUST_HERE_AS_A_WORKAROUND

ARG RUNTIME_APK_DEPENDENCIES
ARG BUILD_PYTHON_APK_DEPENDENCIES
ARG BUILD_DJANGO_APK_DEPENDENCIES
ARG STORAGE_PATH
ARG LOG_PATH

# install python deps, must be done twice for arm build to work
COPY --from=poetry-prestage /requirements.txt ./

RUN apk add --no-cache ${BUILD_DJANGO_APK_DEPENDENCIES} ${BUILD_PYTHON_APK_DEPENDENCIES} ${RUNTIME_APK_DEPENDENCIES} && \
    pip install --no-cache-dir --requirement requirements.txt && \
    mkdir -p ${STORAGE_PATH} ${LOG_PATH}

COPY ./manage.py ./pyproject.toml ./
COPY ./src/ ./src/

RUN django-admin collectstatic --noinput && \
    django-admin compilemessages


##   stage 4   ##
## make SSL cert ##
## no cleanup required ##

FROM alpine:${ALPINE_VERSION} AS ssl-cert-prestage

WORKDIR /

RUN apk add --no-cache openssl && \
    openssl req -x509 \
    -newkey rsa:4096 \
    -keyout /key.pem \
    -out /cert.pem \
    -days 365 \
    -nodes \
    -subj "/C=DE/ST=Bavaria/L=Munich/O=SBV/OU=Eonvelope/CN=eonvelope.org"


##   stage 5   ##
## compile final image  ##
## cleanup mandatory ##
## order operations by increasing frequency of change ##

FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION} AS eonvelope

# labels
LABEL org.opencontainers.image.authors="David Aderbauer & The Eonvelope Contributors <eonvelope@mailo.com>"
LABEL org.opencontainers.image.documentation="https://eonvelope.readthedocs.io"
LABEL org.opencontainers.image.source="https://gitlab.com/Dacid99/eonvelope"
LABEL org.opencontainers.image.url="https://gitlab.com/Dacid99/eonvelope"
LABEL org.opencontainers.image.licenses="AGPL-3.0-or-later"
LABEL org.opencontainers.image.description="An email-archiving server using the django framework"
LABEL org.opencontainers.image.title="Eonvelope Server"

ARG SRC_PATH=/opt/
ARG S6_OVERLAY_PATH=/etc/s6-overlay/
ARG STORAGE_PATH
ARG LOG_PATH

WORKDIR ${SRC_PATH}

# environment setup
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=${SRC_PATH}'src/' \
    PYTHONUNBUFFERED=1 \
    XDG_RUNTIME_DIR=/tmp/xdg_runtime \
    DJANGO_SETTINGS_MODULE=config.settings

VOLUME ${STORAGE_PATH} ${LOG_PATH}

COPY --from=ssl-cert-prestage /cert.pem /key.pem ./

# setup s6-overlay
COPY --from=s6-overlay-prestage /s6-overlay/ /

COPY --chmod=550 ./docker/s6-overlay/ ${S6_OVERLAY_PATH}

ENTRYPOINT [ "/init" ]

# install apk runtime dependencies
ARG RUNTIME_APK_DEPENDENCIES

RUN apk update && \
    apk add --no-cache ${RUNTIME_APK_DEPENDENCIES} && \
    rm -rf /var/cache/apk/* && \
    rm -rf /tmp/*

# install python dependencies
COPY --from=poetry-prestage /requirements.txt ./

ARG BUILD_PYTHON_APK_DEPENDENCIES

RUN apk add --no-cache ${BUILD_PYTHON_APK_DEPENDENCIES} && \
    pip install --no-cache-dir --requirement requirements.txt && \
    apk del ${BUILD_PYTHON_APK_DEPENDENCIES} && \
    rm -rf /var/cache/apk/* && \
    rm -rf /tmp/* && \
    rm -f requirements.txt

# copy django components
COPY --from=django-prestage /app ./

# must match port used by gunicorn or manage.py runserver
EXPOSE 443

HEALTHCHECK\
    --interval=60s \
    --timeout=10s \
    --start-period=5s \
    --retries=3 \
    CMD curl -kf https://localhost:443/health/ || exit 1
