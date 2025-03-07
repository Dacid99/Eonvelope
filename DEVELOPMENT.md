# Setup

Your global python version should be at least *3.12*.

If necessary you can install it via [the deadsnakes ppa](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa).

First install the packages required for the build environment, on debian based distros:

```bash
sudo apt-get -y update && apt-get -y install build-essential default-mysql-client wkhtmltopdf krb5-user krb5-multidev libmysqlclient-dev pkg-config mysql-server nodejs npm
```

Then to install the python dependencies start a new virtual environment and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Then install the dependencies:

```bash
pip install -Ur dependencies.txt
pip install -Ur dev-dependencies.txt
pip install -Ur docs/dependencies.txt
```

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

### VSCode

#### Settings

- Trim final newlines
- Trim trailing whitespace
- Insert final newline

#### Extensions

- everything for python and django
- python test (with setting "python.testing.cwd": "/path/to/repo/test/")
- ruff (with setting "ruff.configuration": "validation/ruff.toml"
)
- pylint (with setting "pylint.args": ["--rcfile=validation/pylintrc(_strict)_extension"] )
- mypy (with setting "mypy-type-checker.args": ["--config-file=validation/mypy_extension.ini"] )
- black (with setting "mypy-type-checker.args": ["--config=validation/black_config"] )
- isort
- ANSI colors (iliazeus.vscode-ansi) (for validation reports)
- reStructuredText (lextudio.restructuredtext) for docs
