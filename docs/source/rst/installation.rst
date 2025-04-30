Installation
============

Recommended
-----------

The project is intended to be run with *docker compose* using the compose fil docker/docker-compose.yml or an equivalent *docker run* command.

Advanced
--------

Alternatively, you can run the application bare metal.

1. Clone the repository.
2. Install the dependencies for python and the system as described in `development`_.
3. Spin up a mysql db server matching the configurations in the django application settings ``Emailkasten/settings.py`` on your machine.
4. Finally the Emailkasten server is started via the docker entrypoint script ``docker/docker-compose.yml``.
