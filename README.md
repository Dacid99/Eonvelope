# Emailkasten

A open-source self-hostable email archive using the [django framework](https://www.djangoproject.com/).

## Features

- Automated continuous email fetching
- Support for IMAP, POP and Exchange
- Import and export of emails
- Indexing of attachments and correspondents
- Filter and search your emails, attachments, correspondents
- Identification of related emails
- Mobile-friendly Bootstrap5 webapp
- Full-fledged API
- Multi-language and timezone support
- Easy docker setup and configuration
- SSL certificate out of the box

Your emails are serious business, so this projects codebase has > 95% test-coverage!

### Roadmap

- Consolidate existing features
- A LOT of other ideas (see [the TODO list](TODO.md))

*Tell us what you'd like to see in a feature request!*

## We need your opinion

This project is currently in **beta** stage.

We are looking for people to run it and give feedback!

Interested? Just go ahead and run this application on your homelab.

If you encounter an issue please let us know via an issue or direct message!

## Installation

### Recommended

The project is intended to be run with the container image provided at [dockerhub](https://hub.docker.com/repository/docker/dacid99/emailkasten/general).

**Docker**

Use *docker compose* using [the compose file](docker/docker-compose.minimal.yml) or an equivalent *docker run* command.

**Podman**

Do the same thing as above, just using *podman* instead of *docker*.

**Kubernetes**

You can use [the example kubernetes cluster setup](docker/kubernetes/minimal/) and launch it, for example via *minikube*.

### Advanced

Alternatively, you can run the application bare metal.

1. Clone this repo.
1. Install the dependencies for python and the system as described in [the development guide](DEVELOPMENT.md).
1. Spin up a mysql db server matching the configurations in [the django application settings](Emailkasten/settings.py) on your machine.

Finally the Emailkasten server is started via [the entrypoint script](docker/entrypoint.sh).

## Docs

The full documentation is available on [ReadTheDocs](https://emailkasten.readthedocs.io/latest/).

Check it out for details on configuration and instructions on how to use the running server.

## Translation

We are striving to support as many languages as possible to make the application accessible to everyone!

Translation is done via [weblate](https://hosted.weblate.org/projects/emailkasten/). If you want to add a language that is missing, go check it out! If the language is missing on [weblate](https://hosted.weblate.org/projects/emailkasten/) too, please file an [issue](https://gitlab.com/Dacid99/emailkasten/-/issues) using the missing-language template.

## Accessibility

Everybody should be able to use Emailkasten. Please don't hesitate to report any problem related to accessibility via an [issue](https://gitlab.com/Dacid99/emailkasten/-/issues).

## Contributing

If you want to help us improving this project that is great! Please don't hesitate to approach us with ideas. And of course we are looking forward to your pull requests!

To get you started smoothly just follow [the development guide](DEVELOPMENT.md). This will help you set up a workspace for working with this project conveniently!

In order to keep the code maintainable and in a consistent style please make sure to follow the rules in [the guidelines](CONTRIBUTING.md).

The complete source code documentation is part of the docs on [ReadTheDocs](https://emailkasten.readthedocs.io/latest/rst/developers.html)

Thank you to [everybody who helped with advancing this project](CONTRIBUTORS.md)
and [who helped with translation](TRANSLATORS.rst)!

## License

This software is proudly released under [the AGPLv3 open-source license](LICENSE).
