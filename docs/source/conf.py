# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import datetime
import os
import sys

import django
import tomli


sys.path.insert(0, os.path.abspath("../../"))
sys.path.insert(0, os.path.abspath("../../src/"))

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
django.setup()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Eonvelope"
copyright = (
    "2024-%Y, David Aderbauer & The Eonvelope Contributors; Licensed under CC BY-SA 4.0"
)
author = "David Aderbauer"
year = datetime.date.today().year

with open("../../pyproject.toml", "rb") as pyproject_toml:
    config = tomli.load(pyproject_toml)

version = config["project"]["version"]
release = config["project"]["version"]

django_version = ".".join(map(str, django.VERSION[0:2]))
python_version = ".".join(map(str, sys.version_info[0:2]))

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autodoc",
    "sphinx.ext.graphviz",
    "sphinx.ext.apidoc",  # sphinx-apidoc run automatically with sphinx-build
    "sphinx_autodoc_typehints",
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
nitpick_ignore_regex = [
    (r"py:.*", r"rest_framework\..*"),  # restframework has no sphinx inventory
]

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
    "**/tools",
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

html_theme = "alabaster"
html_sidebars = {
    "**": [
        "about.html",
        "searchfield.html",
        "navigation.html",
        "relations.html",
        "donate.html",
    ]
}
html_theme_options = {
    "description": "A open-source self-hostable email archive using the django framework",
    "logo": "",
    # "logo_name": ,
    "touch_icon": "",
    "github_button": True,
    "github_repo": "eonvelope",
    "github_user": "Dacid99",
    "show_powered_by": True,
    "show_relbars": True,
    "fixed_sidebar": True,
}
html_title = "Eonvelope Docs"
html_short_title = "Eonvelope Docs"
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
    {"path": "../../src/config", "destination": "apidoc-rst/config"},
    {"path": "../../src/eonvelope", "destination": "apidoc-rst/eonvelope"},
    {"path": "../../src/core", "destination": "apidoc-rst/core"},
    {"path": "../../src/api", "destination": "apidoc-rst/api"},
    {"path": "../../src/web", "destination": "apidoc-rst/web"},
    {"path": "../../test", "destination": "apidoc-rst/test"},
]
apidoc_exclude_patterns = [
    "**/.git/**",
    "**/tools/**",
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
    "django_filters": (
        "https://django-filter.readthedocs.io/en/stable/",
        None,
    ),
    "django_dirtyfields": (
        "https://django-dirtyfields.readthedocs.io/en/stable/",
        None,
    ),
    "django_constance": (
        "https://django-constance.readthedocs.io/en/stable/",
        None,
    ),
    "django_allauth": (
        "https://django-allauth.readthedocs.io/en/stable/",
        None,
    ),
    "django_environ": (
        "https://django-environ.readthedocs.io/en/stable/",
        None,
    ),
    "django_health_check": (
        "https://django-health-check.readthedocs.io/en/stable/",
        None,
    ),
    "django_celery_beat": (
        "https://django-celery-beat.readthedocs.io/en/stable/",
        None,
    ),
    "django_celery_results": (
        "https://django-celery-results.readthedocs.io/en/stable/",
        None,
    ),
    "django_crispy_forms": (
        "https://django-crispy-forms.readthedocs.io/en/stable/",
        None,
    ),
    "drf_spectacular": (
        "https://drf-spectacular.readthedocs.io/en/stable/",
        None,
    ),
    "django_extensions": (
        "https://django-extensions.readthedocs.io/en/stable/",
        None,
    ),
    "celery": (
        "https://docs.celeryq.dev/en/stable/",
        None,
    ),
    "django_tables2": (
        "https://django-tables2.readthedocs.io/en/latest/",
        None,
    ),
    "vobject": (
        "https://vobject.readthedocs.io/latest/",
        None,
    ),
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
