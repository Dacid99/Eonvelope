FROM python:3.13-rc-bookworm
ENV SECRET_KEY='IM_JUST_HERE_AS_A_WORKAROUND'
RUN apt-get -y update && apt-get -y install gettext build-essential default-mysql-client krb5-user krb5-multidev openssl
WORKDIR /mnt
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV XDG_RUNTIME_DIR=/tmp/xdg_runtime
COPY ../ /mnt/
RUN openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=DE/ST=Bavaria/L=Munich/O=SBV/OU=Emailkasten/CN=emailkasten.org"
RUN pip install -U --no-cache-dir poetry
RUN poetry install
RUN poetry run python manage.py collectstatic --noinput
RUN poetry run python manage.py makemigrations
RUN poetry run python manage.py compilemessages
RUN chmod +x docker/entrypoint.sh
ENV SECRET_KEY=
EXPOSE 443
ENTRYPOINT [ "./docker/entrypoint.sh" ]
HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/health/ || exit 1
