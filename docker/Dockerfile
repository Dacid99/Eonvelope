FROM python:3.13-rc-bookworm
RUN apt-get -y update && apt-get -y install build-essential pipx default-mysql-client wkhtmltopdf krb5-user krb5-multidev
WORKDIR /mnt
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV XDG_RUNTIME_DIR=/tmp/xdg_runtime
ENV PYTHONPATH=/mnt/Emailkasten
COPY ../ /mnt/
RUN pipx install -U poetry --no-cache-dir
RUN poetry install
RUN chmod +x docker/entrypoint.sh
EXPOSE 8000
ENTRYPOINT [ "./docker/entrypoint.sh" ]
HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/health/ || exit 1
