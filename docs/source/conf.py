# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import datetime
import django

sys.path.insert(0, os.path.abspath('../..'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'Emailkasten.settings'
django.setup()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Emailkasten'
copyright = '2024, David & Philipp Aderbauer'
author = 'David & Philipp Aderbauer'
year = datetime.date.today().year
release = '0.0.0'

django_version = ".".join(map(str, django.VERSION[0:2]))
python_version = ".".join(map(str, sys.version_info[0:2]))

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'sphinxcontrib.apidoc',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': True,
    'special-members': '__init__',
    'show-inheritance': True
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/{}'.format(python_version), None),
    'django': ('https://docs.djangoproject.com/en/{}/'.format(django_version),
               'https://docs.djangoproject.com/en/{}/_objects/'.format(django_version)),
    'rest_framework': ('https://www.django-rest-framework.org/', None),
}

nitpick = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'prev_next_buttons_location': 'both',
    'collapse_navigation': True,
}
# html_static_path = ['_static']


# Extension settings

apidoc_module_dir = '../../Emailkasten'
apidoc_output_dir = '../source'
apidoc_excluded_paths = ['../Emailkasten/migrations']
apidoc_separate_modules = True
apidoc_toc_file = False
apidoc_module_first = True

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True
