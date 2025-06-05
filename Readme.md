# Emailkasten

A open-source self-hosted mail archive using the django framework.

## We need your opinion

This project is currently in **alpha** stage.

We are looking for people to test run it and give feedback!

Interested? Just go ahead and run this application on your homelab.

If you encounter an issue please let us know via an issue or direct message!

## Installation

### Recommended

The project is intended to be run with *docker compose* using the [compose file](docker/docker-compose.yml) or an equivalent *docker run* command.

### Advanced

Alternatively, you can run the application bare metal.

1. Clone this repo.
1. Install the dependencies for python and the system as described in [the development guide](DEVELOPMENT.md).
1. Spin up a mysql db server matching the configurations in [the django application settings](Emailkasten/settings.py) on your machine.

Finally the Emailkasten server is started via [the entrypoint script](docker/entrypoint.sh).

## Docs

The documentation is available on ReadTheDocs.

Check it out for details on configuration and instructions on how to use the running server.

## Translation

We are striving to support as many languages as possible to make the application accessible to everyone!

Translation is done via weblate. If you want to add a language that is missing, go check it out! If the language is missing on weblate too, please file an issue using the missing-language template.

## Contributing

If you want to help us improving this projetc that is great! Please don't hesitate to approach us with ideas. And of course we are looking forward to your pull requests!

To get you started smoothly just follow [the development guide](DEVELOPMENT.md). This will help you set up a workspace for working with this project conveniently!

In order to keep the code maintainable and in a consistent style please make sure to follow the rules in [the guidelines](CONTRIBUTING.md).

## License

This software is proudly released under [the AGPLv3 open-source license](LICENSE).
