FROM python:3.13-rc-bookworm
WORKDIR /code
RUN apt-get -y update && apt-get -y install build-essential default-mysql-client
COPY dependencies.txt dependencies.txt
RUN pip install -r dependencies.txt
EXPOSE 8000
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]