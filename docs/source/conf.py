# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import datetime
import os
import sys

import django


sys.path.insert(0, os.path.abspath("../.."))

os.environ["DJANGO_SETTINGS_MODULE"] = "Emailkasten.settings"
django.setup()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Emailkasten"
copyright = "2024-%Y, David Aderbauer"
author = "David Aderbauer"
year = datetime.date.today().year
version = "0.0.0"
release = "0.0.0"

django_version = ".".join(map(str, django.VERSION[0:2]))
python_version = ".".join(map(str, sys.version_info[0:2]))

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.graphviz",
    "sphinx.ext.apidoc",  # sphinx-apidoc run automatically with sphinx-build
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
    "myst_parser",
]

# Options for figure numbering

numfig = True
numfig_secnum_depth = 1

# Options for internationalisation

language = "en"

# Options for markup

default_role = None
option_emphasise_placeholders = False
rst_epilog = ""
rst_prolog = ""
trim_footnote_reference_space = True

# Options for the nitpicky mode

nitpicky = True
nitpick_ignore = ()
nitpick_ignore_regex = ()

# Options for object signatures

toc_object_entries = False
toc_object_entries_show_parents = "domain"

# Options for source files

exclude_patterns = [
    "**/venv",
    "**/.venv",
    "**/docs",
    "**/.git",
    "**/migrations",
    "**/validation",
    "**/.mypy_cache",
    "**/.ruff_cache",
    "**/.pytest_cache",
    "**/__pycache__",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Options for HTML output

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "collapse_navigation": True,
    "navigation_depth": -1,
    "prev_next_buttons_location": "both",
}
html_title = "Emailkasten Docs"
html_logo = ""
html_favicon = ""
html_static_path = ["_static"]
html_last_updated_fmt = ""
html_show_sourcelink = True

# Options for the Python domain

add_module_names = True


# -- Autodoc configuration  ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

autoclass_content = "class"
autodoc_class_signature = "mixed"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "exclude-members": "_abc_impl",
    "member-order": "bysource",
    "undoc-members": True,
    "private-members": True,
    "special-members": "__init__, __str__",
    "show-inheritance": True,
    "inherited-members": False,
}
autodoc_typehints = "description"
autodoc_typehints_format = "short"
autodoc_inherit_docstrings = True


# -- Apidoc configuration  ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/apidoc.html#configuration

apidoc_modules = [
    {"path": "../../Emailkasten", "destination": "apidoc-rst/Emailkasten"},
    {"path": "../../core", "destination": "apidoc-rst/core"},
    {"path": "../../api", "destination": "apidoc-rst/api"},
    {"path": "../../web", "destination": "apidoc-rst/web"},
    {"path": "../../test", "destination": "apidoc-rst/test"},
]
apidoc_exclude_patterns = [
    "**/.git/**",
    "**/validation/**",
    "**/docker/**",
    "**/migrations/**",
    "**/manage.py",
    "**/__pycache__/**",
    "**/.mypy_cache/**",
    "**/.ruff_cache/**",
    "**/.pytest_cache/**",
    "**/.vscode/**",
    "**/.venv/**",
    "**/venv/**",
    "**/htmlcov/**",
    "**/reports/**",
    "**/.coverage",
    "**/*.log",
]
apidoc_separate_modules = True
apidoc_module_first = True
apidoc_include_private = False
apidoc_implicit_namespaces = True


# -- Intersphinx configuration  ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    "python": (f"https://docs.python.org/{python_version}", None),
    "django": (f"https://docs.djangoproject.com/en/{django_version}/", None),
}


# -- Napoleon configuration  ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html#configuration

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False  # restores default autodoc behaviour
napoleon_include_private_with_doc = False  # restores default autodoc behaviour
napoleon_include_special_with_doc = False  # restores default autodoc behaviour
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_keyword = True
napoleon_use_rtype = True


# -- Todo configuration  ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration

todo_include_todos = True
todo_emit_warnings = False
todo_link_only = False
