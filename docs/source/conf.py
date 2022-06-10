# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
from datetime import date

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, '../..')

from mikud import __version__

# -- Project information -----------------------------------------------------

project = 'mikud'
copyright = f"{date.today().year}, David Lev"
author = 'David Lev'

version = __version__
release = __version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx_copybutton",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinxext.opengraph"
]

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

pygments_style = "friendly"

html_theme = "furo"
html_favicon = "../images/favicon.ico"


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['../_static']


html_theme_options = {
    "sidebar_hide_name": True,
    "light_logo": "light_logo.png",
    "dark_logo": "dark_logo.png",
}

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

ogp_site_url = "https://mikud.readthedocs.io/"
ogp_site_name = "mikud documentation"
ogp_image = "https://mikud.readthedocs.io/en/latest/_static/ogp_image.png"
ogp_description_length = 300
ogp_type = "website"
ogp_custom_meta_tags = [
    '<meta property="og:description" content="mikud - Search for Israeli zip code numbers" /> '
]

# html_extra_path = ["google.html"]
