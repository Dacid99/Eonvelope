FROM python:3.13-rc-bookworm
RUN apt-get -y update && apt-get -y install build-essential default-mysql-client
WORKDIR /mnt
COPY dependencies.txt /mnt/
RUN pip install -r dependencies.txt
EXPOSE 8000
COPY . /mnt/
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]