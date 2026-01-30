# E∘nvelope

[![Docker Image Version](https://img.shields.io/docker/v/dacid99/eonvelope)][dockerhub]
[![Docker Pulls](https://img.shields.io/docker/pulls/dacid99/eonvelope)][dockerhub]

[![Last commit](https://img.shields.io/github/last-commit/dacid99/eonvelope)][gitlab]
[![Commit frequency](https://img.shields.io/github/commit-activity/m/dacid99/eonvelope/development)][gitlab]
[![Pipeline](https://gitlab.com/Dacid99/eonvelope/badges/master/pipeline.svg)][gitlab]
[![Coverage](https://gitlab.com/Dacid99/eonvelope/badges/master/coverage.svg?job=test_codebase)][gitlab]
[![Read the Docs](https://img.shields.io/readthedocs/eonvelope/latest)][readthedocs]
[![Translation status](https://img.shields.io/weblate/progress/eonvelope)][weblate]

[![Framework](https://pypi-camo.freetls.fastly.net/beb496af0833573259d4094b1fe3b0a3ea831607/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6672616d65776f726b2d446a616e676f2d3043334332362e737667)](https://www.djangoproject.com/)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

<!-- markdownlint-disable-next-line MD033 -->
<img alt="Eonvelope icon" src="src/eonvelope/static/eonvelope/icons/favicon.svg" height="200"/>

Preserve your emails for [an indefinite long period of time](https://en.wikipedia.org/wiki/Aeon) with this open-source self-hostable email archive!

## Features

As a user you may like this application because of

- Automatic and continuous email fetching
- Support for all major mail access protocols: IMAP, POP, Exchange and JMAP
- Import and export of emails in various formats
- Identification of related emails
- Restoring of emails to your mail account
- Cross integrations with other self-hosted projects like Paperless-ngx, Searxng and Grafana
- Mobile-friendly Bootstrap5 webapp with PWA support
- Easy filtering and searching options for your archived emails, attachments and correspondents

As an admin you may choose this project because of its

- Quick and easy setup and configuration via container (Docker, Podman, Kubernetes, etc.)
- SSL certificate out of the box
- Full-fledged API
- Slim mode for low-spec systems

*Check out the [project website][website] for screenshots and more information.*

Your emails are serious business, so this projects codebase has > 95% test-coverage!

### Roadmap

- Consolidate existing features
- A LOT of other ideas (see [the TODO list](TODO.md))

*Tell us what you'd like to see in a feature request!*

*If you encounter an issue please let us know via an issue or direct message!*

## Installation

The project is intended to be run with the container image provided at [dockerhub][dockerhub].

### Docker

Use *docker compose* using [the compose file](docker/docker-compose.minimal.yml) or an equivalent *docker run* command.

### Podman

Do the same thing as above, just using *podman* instead of *docker*.

### Kubernetes

You can use [the example kubernetes cluster setup](docker/kubernetes/minimal/) and launch it, for example via *minikube*.

### Agentic installation

If you want an agent to install Eonvelope for you, point it to [the install.md file](install.md), e.g.

```bash
  curl -fsSL https://github.com/dacid99/eonvelope/blob/master/install.md | claude
```

## Docs

The full documentation is available on [ReadTheDocs][readthedocs].

Check it out for details on configuration and instructions on how to use the running server.

## Translation

We are striving to support as many languages as possible to make the application accessible to everyone!

[![Translation status](https://hosted.weblate.org/widget/eonvelope/multi-auto.svg)][weblate]

Translation is done via [weblate][weblate-engage].
If you want to add a language that is missing, go check it out!

If the language is missing on [weblate][weblate] too,
please file an [issue][[github-issues]] using the missing-language template.

## Accessibility

Everybody should be able to use Eonvelope.
Please don't hesitate to report any problem related to accessibility via a [github][github-issues] or [gitlab][gitlab-issues] issue.

## Contributing

If you want to help with improving this project that is great!
You can always approach us with ideas or issues you have come across.
The easiest way to get in touch is via a [github][github-issues] or [gitlab][gitlab-issues] issue.

And of course we are looking forward to your pull requests!

To get you started smoothly just follow [the development guide](DEVELOPMENT.md).
This will help you set up a workspace for working with this project conveniently!

In order to keep the code maintainable and in a consistent style
please make sure to follow the rules in [the guidelines](CONTRIBUTING.md).

The complete source code documentation is part of the docs on [ReadTheDocs](https://eonvelope.readthedocs.io/latest/rst/developers.html)

Thank you to [everybody who helped with advancing this project](CONTRIBUTORS.md)
and [who helped with translation](TRANSLATORS.rst)!

## Support

The most important support for this project are your contributions!

If you want to help financially, you can donate via buy-me-a-coffee. Thank you very much!

[![BuyMeACoffee](https://raw.githubusercontent.com/pachadotdev/buymeacoffee-badges/main/bmc-orange.svg)](https://www.buymeacoffee.com/Dacid99)

## License

This software is proudly released under [the GNU Affero General Public License v3.0 or later (AGPLv3) open-source license](LICENSE).

Its documentation is licensed under [the Creative Commons Attributions-ShareAlike 4.0 International (CC BY-SA 4.0) license](docs/LICENSE).

Any contributions will be subject to the same licensing.


[weblate]: https://hosted.weblate.org/engage/eonvelope/
[weblate-engage]: https://hosted.weblate.org/engage/eonvelope/
[dockerhub]: https://hub.docker.com/r/dacid99/eonvelope
[readthedocs]: https://eonvelope.readthedocs.io/latest/
[website]: https://dacid99.gitlab.io/eonvelope
[gitlab]: https://gitlab.com/Dacid99/eonvelope/
[gitlab-issues]: https://gitlab.com/Dacid99/eonvelope/-/issues
[github-issues]: https://github.com/Dacid99/eonvelope/issues
