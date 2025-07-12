Installation
============

General
-------

**This project is currently still in active development.**

While the general functionalities are stable, there may be breaking changes nonetheless.
If you need to archive your emails for a critical purpose, it is not recommended to solely
rely on this application.

The docker image comes with a SSL certificate issued and signed by the emailkasten project.
It ensures safe communication between your reverse proxy and within your local network.
It is not safe for use on the general web.

Therefore, do not expose this application to the web without a reverse proxy like nginx.


Recommended
-----------

The project is intended to be run with the container image
provided at [dockerhub](https://hub.docker.com/repository/docker/dacid99/emailkasten/general).

The emailkasten service mounts 2 volumes,
one for the logfiles of emailkasten and one for the files that emailkasten archives.

.. Note::
    You can also mount all logfiles of the container by changing the path in the docker-compose.yml to /var/log.
    In that case you will have to give the directory 777 permissions, otherwise services will fail to start and log properly.


Docker
^^^^^^

There are two example compose-files in the docker directory of the repository,
a minimal version and one with all settings for full customization.

Take one of these examples,
adapt it to your needs and start the stack with ``docker compose up -d``
or via your container manager.
Done!

Podman
^^^^^^

Just do the same thing as above, just with *podman* instead of *docker*.

Kubernetes
^^^^^^^^^^

There are two example kubernetes setup in the *docker/kubernetes* directory of the repository.
One is a minimal version with only the basic setup and configuration.
The other is a full setup with all environment level configurations.
Take one of them, adapt and launch it, for example via *minikube*.


Advanced
--------

Alternatively, you can run the application bare metal.

1. Clone the repository.
2. Install the dependencies for python and the system
   as described in :doc:`development <development>`.
3. Spin up a mysql db server matching the configurations
   in the django application settings ``Emailkasten/settings.py`` on your machine.
4. Finally the Emailkasten server is started via the docker entrypoint script
   ``docker/docker-compose.yml``.
