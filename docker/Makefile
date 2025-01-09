image: Dockerfile entrypoint.sh
	sudo docker compose build

up: docker-compose.yml Dockerfile entrypoint.sh
	sudo docker compose up

down: docker-compose.yml Dockerfile entrypoint.sh
	sudo docker compose down

clean:
	sudo docker image rm emailkasten
