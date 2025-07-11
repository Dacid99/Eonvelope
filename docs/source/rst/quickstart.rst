Quickstart
==========

If you don't have already, install `docker <https://docs.docker.com/engine/install/>`_.

Next take this docker-compose file and adapt the environment settings that need to be changed.

.. literalinclude:: ../../../docker/docker-compose.minimal.yml
   :language: yaml
   :caption: docker-compose.yml

For security reasons please change all passwords and the ``SECRET_KEY``.

Now you can start the docker stack with ``docker compose up -d``.
Or you use a container management platform like  `portainer <https://www.portainer.io/>`_, `dockge <https://dockge.kuma.pet/>`_ or many others.

After the container is up you can access the webapp at *https://localhost:1122/*.


For a detailed overview of the available settings
see the :doc:`configurations documentation <configuration>`.

If you need help with how to use the application refer
to the :doc:`instructions overview <instructions>`.

In case you encounter a problem or have further questions, check the :doc:`FAQ <faq>`.
