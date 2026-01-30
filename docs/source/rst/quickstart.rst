..
   SPDX-License-Identifier: CC-BY-SA 4.0

   Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
   Licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.

Quickstart
==========

If you don't have already, install `docker <https://docs.docker.com/engine/install/>`_.

Next take this docker-compose file and adapt the environment settings that need to be changed.

.. literalinclude:: ../../../docker/docker-compose.minimal.yml
   :language: yaml
   :caption: docker-compose.yml

For security reasons please change all passwords and the ``SECRET_KEY``.

If your device is low on compute power and system resources, you may prefer to use the slim version of the docker-compose file instead.
This will only run the core of the application in the docker container, excluding some additional components mostly aimed at development.

Now you can start the docker stack with ``docker compose up -d``.
Or you use a container management platform like  `portainer <https://www.portainer.io/>`_, `dockge <https://dockge.kuma.pet/>`_ or many others.

After the container is up you can access the webapp at *https://localhost:1122/*.

The credentials for the default admin account are *admin* and the value of ``DJANGO_SUPERUSER_PASSWORD`` you set in the docker-compose file.
Using this account you can then create the user accounts and configure the instance.
If you want users to sign up themselves, set the docker environment variable ``REGISTRATION_ENABLED`` to *True*.

For a full information about the administration of the instance and how to create user accounts
check out the :doc:`admin instructions <admin-instructions>`.

For a detailed overview of the available settings
see the :doc:`configurations documentation <configuration>`.

If you need help with how to use the application refer
to the :doc:`user manual <instructions>`.

There are other ways you can run Eonvelope,
please see :doc:`the installation guide <installation>` for details.

In case you encounter a problem or have further questions, check the :doc:`FAQ <faq>`.
