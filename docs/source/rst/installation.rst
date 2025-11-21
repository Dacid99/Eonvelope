..
   SPDX-License-Identifier: CC-BY-SA 4.0

   Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
   Licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.

Installation
============

General
-------

While the general functionalities are stable, there may be breaking changes nonetheless.
If you need to archive your emails for a critical purpose, it is not recommended to solely
rely on this application.

The docker image comes with a SSL certificate issued and signed by the Eonvelope project.
It ensures safe communication between your server and your reverse proxy
as well as within your local network.

.. note::
   The SSL certificate is a different one for every version of Eonvelope.

It is not safe or intended for use on the open web.

Therefore, do not expose this application to the web without a reverse proxy like `nginx <https://nginx.org>`_.
Further details on this can be found in the :ref:`Reverse-proxy` section below.

Recommended
-----------

The project is intended to be run with the container image
provided at `dockerhub <https://hub.docker.com/r/dacid99/eonvelope>`_.

The Eonvelope service mounts 2 volumes,
one for the logfiles of Eonvelope and one for the files that Eonvelope archives.

.. Note::
    You can also mount all logfiles of the container by changing the path in the docker-compose.yml to /var/log.
    In that case you will have to give the directory 777 permissions, otherwise services will fail to start and log properly.

It is recommeneded to use the minimal version of the docker-compose for the first time you deploy Eonvelope
and to skim the docker settings section of the :doc:`configuration reference <configurations page>` beforehand.

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
   in the django application settings ``eonvelope/settings.py`` on your machine.
4. Finally the Eonvelope server is started via the docker entrypoint script
   ``docker/docker-compose.yml``.

Other database type
^^^^^^^^^^^^^^^^^^^

Depending on your setup, you may want to use a database that is not a mariadb.

In that case you can set the type of database you want to use in the docker-compose.yml file.
See :doc:`configuration` for more details on this.

It is crucial that the name of the database service in the stack is `db`!
Otherwise the connection from the Eonvelope container to the database will fail.

.. note::
   Using a database other than the default mysql can lead to issues.
   If possible try to stick with the default, which is tested and guaranteed to work flawlessly.

Reverse-proxy
-------------

If you reverse-proxy or expose your Eonvelope instance another way,
you must make sure that the prometheus endpoint ``/metrics`` is not exposed for the entire world to see!

Just add

.. code-block::
   location /metrics {
      return 403;   # or 404
   }

to your nginx config.

.. note::
   Make sure to add the address to the ALLOWED_HOSTS environment variable in the docker-compose file.

Updating
========

You can update your Eonvelope server by getting and deploying the latest version from `dockerhub <https://hub.docker.com/r/dacid99/eonvelope>`_.

Database migrations
-------------------

If there are structural changes to the database of Eonvelope,
these changes will be implemented and mitigated by migrations applied before the Eonvelope container starts.
This ensures continuity of the data.
Sometimes there are changes that may not be easy to mitigate with a migration alone.
In that case a script for this purpose to be applied manually in the Eonvelope will be supplied.

It can be run from the terminal of your server with

.. code-block:: bash

   docker exec -it eonvelope-web python3 manage.py runscript scriptname

Swap in the name of the specific script for the migration fix.
Just the name is required, drop the .py suffix.
If your containers have different names, you may have to exchange the `eonvelope-web` part.

For more details see `the django docs on this topic <https://django-extensions.readthedocs.io/en/latest/runscript.html>`_.

.. note::
   If you are migrating from version 0.2.0 or lower to a version above 0.2.0,
   you will have to add an adminer container (see the docker-compose.debug.yml for reference) to the stack
   and change the ``app`` column of all rows in the migrations table that have emailkasten as value to eonvelope.


Migration
=========

To new server
-------------

If you already have a running Eonvelope instance and want to move it to a new server there are 4 steps you can go through to do so in a save manner.

1. Locate and docker volumes of all containers in the docker stack in the old servers storage.
2. Copy these complete folders to the new server to the locations of the volumes on the new server.
3. Copy the docker compose from the old server setup to the new server and adjust the volume paths if necessary. Do not change the passwords and secret key!
4. Start the stack. Done.


From other service
------------------

In principle it is possible to migrate to Eonvelope from another service fetching emails.
The main part is required for this is a migration that rewrites that services database into one compatible with Eonvelope.

If you are interested in providing such a program for the application you are using right now, please get in touch!

Alternatively, you can also export all emails from the other application and import them into Eonvelope.
The import supports various formats for collections of emails, including the popular mbox format.
For details please refer to the :doc:`instructions <web-instructions>`.
