# E∘nvelope

[![Docker Pulls](https://img.shields.io/docker/pulls/dacid99/eonvelope)](https://hub.docker.com/repository/docker/dacid99/eonvelope/general)
[![Docker Image Version](https://img.shields.io/docker/v/dacid99/eonvelope)](https://hub.docker.com/repository/docker/dacid99/eonvelope/general)
[![Read the Docs](https://img.shields.io/readthedocs/eonvelope/latest)](https://eonvelope.readthedocs.io/latest/)
[![Translation status](https://img.shields.io/weblate/progress/eonvelope)](https://hosted.weblate.org/projects/eonvelope/)
[![Coverage](https://gitlab.com/Dacid99/eonvelope/badges/master/coverage.svg?job=test_codebase)](https://gitlab.com/Dacid99/eonvelope/)
[![Pipeline](https://gitlab.com/Dacid99/eonvelope/badges/master/pipeline.svg)](https://gitlab.com/Dacid99/eonvelope/)
[![Framework](https://pypi-camo.freetls.fastly.net/beb496af0833573259d4094b1fe3b0a3ea831607/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6672616d65776f726b2d446a616e676f2d3043334332362e737667)](https://www.djangoproject.com/)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Preserve your emails for [an indefinite long period of time](https://en.wikipedia.org/wiki/Aeon) with this open-source self-hostable email archive!

## Features

As a user you may like this application because of

- Automated continuous email fetching
- Support for IMAP, POP and Exchange
- Import and export of emails in various formats
- Identification of related emails
- Restoring of emails to your mailaccount
- Cross integrations with other self-hosted projects like Paperless-ngx, Searxng and Grafana
- Mobile-friendly Bootstrap5 webapp with PWA support
- Easy filtering and searching options for your archived emails, attachments and correspondents

As an admin you may choose this project because of its

- Quick and easy setup and configuration via container (docker, podman, kubernetes, etc.)
- SSL certificate out of the box
- Full-fledged API

Your emails are serious business, so this projects codebase has > 95% test-coverage!

### Roadmap

- Consolidate existing features
- A LOT of other ideas (see [the TODO list](TODO.md))

*Tell us what you'd like to see in a feature request!*

*If you encounter an issue please let us know via an issue or direct message!*

## Installation

The project is intended to be run with the container image provided at [dockerhub](https://hub.docker.com/repository/docker/dacid99/eonvelope/general).

### Docker

Use *docker compose* using [the compose file](docker/docker-compose.minimal.yml) or an equivalent *docker run* command.

### Podman

Do the same thing as above, just using *podman* instead of *docker*.

### Kubernetes

You can use [the example kubernetes cluster setup](docker/kubernetes/minimal/) and launch it, for example via *minikube*.

## Docs

The full documentation is available on [ReadTheDocs](https://eonvelope.readthedocs.io/latest/).

Check it out for details on configuration and instructions on how to use the running server.

## Translation

We are striving to support as many languages as possible to make the application accessible to everyone!

Translation is done via [weblate](https://hosted.weblate.org/projects/eonvelope/). If you want to add a language that is missing, go check it out! If the language is missing on [weblate](https://hosted.weblate.org/projects/eonvelope/) too, please file an [issue](https://gitlab.com/Dacid99/eonvelope/-/issues) using the missing-language template.

## Accessibility

Everybody should be able to use Eonvelope. Please don't hesitate to report any problem related to accessibility via an [issue](https://gitlab.com/Dacid99/eonvelope/-/issues).

## Contributing

If you want to help with improving this project that is great! Please don't hesitate to approach us with ideas. And of course we are looking forward to your pull requests!

To get you started smoothly just follow [the development guide](DEVELOPMENT.md). This will help you set up a workspace for working with this project conveniently!

In order to keep the code maintainable and in a consistent style please make sure to follow the rules in [the guidelines](CONTRIBUTING.md).

The complete source code documentation is part of the docs on [ReadTheDocs](https://eonvelope.readthedocs.io/latest/rst/developers.html)

Thank you to [everybody who helped with advancing this project](CONTRIBUTORS.md)
and [who helped with translation](TRANSLATORS.rst)!

## License

This software is proudly released under [the GNU Affero General Public License v3.0 or later (AGPLv3) open-source license](LICENSE).

Its documentation is licensed under [the Creative Commons Attributions-ShareAlike 4.0 International (CC BY-SA 4.0) license](docs/LICENSE).

Any contributions will be subject to the same licensing.
