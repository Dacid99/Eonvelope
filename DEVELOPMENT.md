# Setup

To install the python dependencies start a new virtual environment and activate it:

```bash
python3 -m venv .venv
source venv/bin/activate
```

Then install the dependencies:

```bash
pip install -Ur dependencies.txt
pip install -Ur dev-dependencies.txt
pip install -Ur docs/dependencies.txt
```

# Workspace Recommendations

## VSCode extensions

- everything for python and django
- pylint (with setting "pylint.args": ["--rcfile=validation/pylintrc(_strict)"] )
- mypy (with setting "mypy-type-checker.args": ["--config-file=validation/mypy_extension.ini"] )
- isort
- ANSI colors (iliazeus.vscode-ansi) (for validation reports)
- reStructuredText (lextudio.restructuredtext) for docs

## VSCode settings

- Trim final newlines
- Trim trailing whitespace
- Insert final newline

# Validation and Linting

You can use the tools in validation/ to lint and check your changes.
There are preconfigured githooks in validation/githooks that run check and lint jobs before every commit
Set them for your local repository via

```bash
git config core.hooksPath validation/githooks/
```
