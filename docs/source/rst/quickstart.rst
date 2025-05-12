Quickstart
==========

If you dont have already, install `https://docs.docker.com/engine/install/ <docker>`_.

Next take this docker-compose file and adapt the environment settings that need to be changed.

.. literalinclude:: ../../../docker/docker-compose.yml
   :language: yaml
   :caption: docker-compose.yaml

For security reasons please change all passwords and the SECRET_KEY.

Now you can start the docker stack with ``docker compose up -d``.

After the container is up you can access the webapp at http://localhost:1122/.


For a detailed overview of the available settings see the :doc:`configurations documentation <configuration>`.

If you need help with how to use the application refer to the :doc:`instructions overview <instructions>`.
