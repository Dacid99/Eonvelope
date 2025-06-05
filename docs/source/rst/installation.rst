Installation
============

General
-------

Do not expose this application to the web without a reverse proxy like nginx.

The docker image comes with a SSL certificate issued and signed by the emailkasten project.
It ensures safe communication between your reverse proxy and within your local network.
It is not safe for use on the general web.


Recommended
-----------

The project is intended to be run with *docker compose* using the compose file docker/docker-compose.yml or an equivalent *docker run* command.
Take the docker compose file from the docker directory of the project, adapt it to your needs and run ``docker compose up -d``. Done!

Advanced
--------

Alternatively, you can run the application bare metal.

1. Clone the repository.
2. Install the dependencies for python and the system as described in `development`_.
3. Spin up a mysql db server matching the configurations in the django application settings ``Emailkasten/settings.py`` on your machine.
4. Finally the Emailkasten server is started via the docker entrypoint script ``docker/docker-compose.yml``.
