# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright © 2024 David Aderbauer & The Eonvelope Contributors

##    stage 1    ##
## build python dependencies ##
## no cleanup required ##
FROM python:3.14-alpine AS python-prestage

WORKDIR /
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry && \
    poetry self add poetry-plugin-export && \
    poetry export -f requirements.txt > requirements.txt

##   stage 2   ##
## install s6-overlay ##
FROM python:3.14-alpine AS s6-overlay-base

ARG S6_OVERLAY_VERSION=3.2.1.0

WORKDIR /tmp

# install s6-overlay
ARG TARGETARCH
ARG TARGETVARIANT

ARG BUILD_S6_APK_DEPENDENCIES="curl xz"

RUN apk add --no-cache ${BUILD_S6_APK_DEPENDENCIES} && \
    S6_ARCH="" && \
    if [ "${TARGETARCH}${TARGETVARIANT}" = "amd64" ]; then S6_ARCH="x86_64"; \
    elif [ "${TARGETARCH}${TARGETVARIANT}" = "arm64" ]; then S6_ARCH="aarch64"; fi && \
    if [ -z "${S6_ARCH}" ]; then { echo "Error: Not able to determine target platform"; exit 1; }; fi && \
    curl --fail --silent --no-progress-meter --show-error --location --remote-name-all --parallel --parallel-max 4 \
    "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz" \
    "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz.sha256" \
    "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${S6_ARCH}.tar.xz" \
    "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${S6_ARCH}.tar.xz.sha256" && \
    sha256sum -c ./*.sha256 && \
    tar --directory / -Jxpf s6-overlay-noarch.tar.xz && \
    tar --directory / -Jxpf s6-overlay-${S6_ARCH}.tar.xz && \
    apk del ${BUILD_S6_APK_DEPENDENCIES} && \
    rm ./*.tar.xz && \
    rm ./*.sha256 && \
    rm -rf /var/cache/apk/*


##   stage 3   ##
##  final image  ##
FROM s6-overlay-base AS eonvelope

### general config

# labels
LABEL org.opencontainers.image.authors="David Aderbauer & The Eonvelope Contributors <eonvelope@mailo.com>"
LABEL org.opencontainers.image.documentation="https://eonvelope.readthedocs.io"
LABEL org.opencontainers.image.source="https://gitlab.com/Dacid99/eonvelope"
LABEL org.opencontainers.image.url="https://gitlab.com/Dacid99/eonvelope"
LABEL org.opencontainers.image.licenses="AGPL-3.0-or-later"
LABEL org.opencontainers.image.description="An email-archiving server using the django framework"
LABEL org.opencontainers.image.title="Eonvelope Server"

ARG SRC_PATH=/opt/
ARG STORAGE_PATH=/mnt/archive/  # must match STORAGE_PATH in settings.py
ARG LOG_PATH=/var/log/eonvelope/  # must match LOG_DIRECTORY_PATH in settings.py
ARG S6_OVERLAY_PATH=/etc/s6-overlay/

WORKDIR ${SRC_PATH}

# environment setup
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=${SRC_PATH}'src/' \
    PYTHONUNBUFFERED=1 \
    XDG_RUNTIME_DIR=/tmp/xdg_runtime \
    DJANGO_SETTINGS_MODULE=eonvelope.settings

# create ssl cert
RUN apk add --no-cache openssl && \
    openssl req -x509 -newkey rsa:4096 -keyout ${SRC_PATH}'key.pem' -out ${SRC_PATH}'cert.pem' -days 365 -nodes -subj "/C=DE/ST=Bavaria/L=Munich/O=SBV/OU=Eonvelope/CN=eonvelope.org" && \
    apk del openssl && \
    rm -rf /var/cache/apk/*


### requirements

# install runtime apk dependencies
ARG RUNTIME_APK_DEPENDENCIES="curl \
    rabbitmq-server \
    mariadb-client \
    mariadb-connector-c \
    gettext"

RUN apk update && \
    apk add --no-cache ${RUNTIME_APK_DEPENDENCIES} && \
    rm -rf /var/cache/apk/*


# install python dependencies
ARG BUILD_PYTHON_APK_DEPENDENCIES="python3-dev \
    linux-headers \
    musl-dev \
    gcc \
    mariadb-dev"

COPY --from=python-prestage /requirements.txt .
RUN apk add --no-cache ${BUILD_PYTHON_APK_DEPENDENCIES} && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del ${BUILD_PYTHON_APK_DEPENDENCIES} && \
    rm -rf /var/cache/apk/* && \
    rm -rf /tmp/* && \
    rm -f requirements.txt


### move source files

# create directories
RUN mkdir -p ${SRC_PATH}'src/' ${LOG_PATH} ${STORAGE_PATH} ${S6_OVERLAY_PATH}

# copy s6-overlay config
COPY ./docker/s6-overlay ${S6_OVERLAY_PATH}
# and set permissions
RUN find /etc/s6-overlay -type f -name run -exec chmod +x {} \;

# copy source files
COPY ./manage.py ./pyproject.toml ./
COPY ./src/ ./src/


### finish setup

# django setup
ENV SECRET_KEY=IM_JUST_HERE_AS_A_WORKAROUND
RUN django-admin collectstatic --noinput && \
    django-admin compilemessages
ENV SECRET_KEY=

# must match port used by gunicorn or python3 runserver
EXPOSE 443

VOLUME ${STORAGE_PATH} ${LOG_PATH}

ENTRYPOINT [ "/init" ]

HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 CMD curl -kf https://localhost:443/health/ || exit 1
