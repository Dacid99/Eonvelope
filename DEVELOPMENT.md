# Development Quickstart

## Setup

Your global python version should be at least *3.12*.

If necessary you can install it via [the deadsnakes ppa](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa).

Make sure to also install the *python-dev* version!

First install the packages required for the build environment, on debian based distros:

```bash
sudo apt-get -y update && apt-get -y install build-essential gettext default-mysql-client krb5-user krb5-multidev libmysqlclient-dev pkg-config mysql-server nodejs npm
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

## Workspace Recommendations

### Validation and Linting

You can use the tools in validation/ to lint and check your changes.

The code is formatted using black formatter.

The imports are sorted with ruffs isort.

There are preconfigured githooks in validation/githooks that format, check and lint the code before every commit.
Set them for your local repository via

```bash
git config core.hooksPath validation/githooks/
```

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
- python test (with setting "python.testing.cwd": "/path/to/repo/test/")
- ruff (with setting "ruff.configuration": "validation/ruff.toml")
- pylint, with config

```json
"pylint.args": ["--rcfile=validation/pylintrc_extension"]
```

- mypy, with config

```json
 "mypy-type-checker.args": ["--config-file=validation/mypy.ini"]
```

- black, with config

```json
 "black-formatter.args": ["--config=validation/black_config"]
```

- python poetry
- ANSI colors (iliazeus.vscode-ansi) (for validation reports)
- reStructuredText (lextudio.restructuredtext) for docs, with config

```json
 "restructuredtext.linter.doc8.extraArgs": ["--config /path/to/validation/doc8.ini"]
```

- bootstrap 5 intellisense etc.
