# Development Quickstart

## Setup

Your global python version should be at least *3.13*.

If necessary you can install it via [the deadsnakes ppa](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa).

Make sure to also install the **python-dev** version!

First install the packages required for the build environment, on debian based distros:

```bash
sudo apt-get -y update && apt-get -y install build-essential gettext default-mysql-client libmysqlclient-dev pkg-config npx
```

and on redhat distros:

```bash
sudo dnf -y update && dnf -y install gcc gettext mysql-devel pkgconf npx
```

Then to install the python dependencies start a new virtual environment and activate it:

[Poetry](https://python-poetry.org/docs/) is used to manage the python dependencies of this project.

```bash
pip install poetry
```

You can then add the tab completions for it by:

```bash
poetry completions bash >> ~/.bash_completion
```

Then install all the dependencies to a virtual environment:

```bash
poetry install --with dev,docs
```

Finally you can activate the venv with

```bash
eval $(poetry env activate)
```

You should avoid having the venv inside the workspace as that will brick docker run in most cases.

Depending on your OS, the mysqlclient package may cause problems, this can usually be solved by installing a missing system package.

## Testing

### Unittests

The projects tests are in the test/ directory. You can run them from the project root with

```bash
pytest test
```

### Debug build

If you want to test your changes manually, you can build the docker image

```bash
docker build -f docker/Dockerfile . -t eonvelope-debug
```

and run it with the docker-compose.debug.yml.

```bash
docker compose -f docker/docker-compose.debug.yml up -d
```

In debug mode, the container uses djangos runserver instead of gunicorn, allowing you to manipulate the source and static files while the server is running, e.g. via docker exec. Additionally, all internal errors will surface as error webpages with full context of the error and the django-debug toolbar will be shown on webpages. For direct database access, you can go to port 9999, where the adminer service of the stack is available.
To surveil the celery tasks, there is also a flower service running and available under port 5555.

To test the webui on other devices, like your phone or tablet, add your machines IP to ALLOWED_HOSTS and you will be able to access the debug application from other devices as well.

## Validation and Linting

You can use the tools in tools/ to lint and check your changes.

The code is formatted using black formatter.

The imports are sorted with ruffs isort.

There are preconfigured githooks in tools/githooks that format, check and lint the code before every commit.
Set them for your local repository via

```bash
git config core.hooksPath tools/githooks/
```

## Workspace Recommendations

### VSCodium / VSCode

#### Settings

- Trim final newlines

```json
    "files.trimFinalNewlines": true,
```

- Trim trailing whitespace

```json
    "files.trimTrailingWhitespace": true,
```

- Insert final newline

```json
    "files.insertFinalNewline": true,
```

- Disable html autoformatting, it messes up django templates on a regular basis

```json
    "html.format.enable": false
```

#### Extensions

- everything for python and django
- python test, with config

```json
    "python.testing.cwd": "/path/to/repo/test/"
```

- ruff, with config

```json
    "ruff.configuration": "tools/ruff.toml")
```

- pylint, with config

```json
    "pylint.args": ["--rcfile=tools/pylintrc_extension"]
```

- mypy, with config

```json
    "mypy-type-checker.args": ["--config-file=tools/mypy.ini"]
```

- black, with config

```json
    "black-formatter.args": ["--config=tools/black_config"]
```

- python poetry
- ANSI colors (iliazeus.vscode-ansi) (for reports)
- reStructuredText (lextudio.restructuredtext) for docs, with config

```json
    "restructuredtext.linter.doc8.extraArgs": ["--config tools/doc8.ini"]
```

- bootstrap 5 intellisense etc.
