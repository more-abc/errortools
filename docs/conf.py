# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from _errortools.version import __version__, __version_tuple__
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")


project = "errortools"
copyright = "(C) 2026 aiwonderland and more-abc team"
author = "aiwonderland"
release = __version__
version = f"{__version_tuple__[0]}.{__version_tuple__[1]}"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ["_static"]

extensions = [
    "myst_parser",
    "sphinx_rtd_theme",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

source_suffix = {
    # ".rst": "restructuredtext",
    ".md": "markdown",
}

html_theme = "furo"

myst_enable_extensions = [
    "colon_fence",
    "dollarmath",
    "tasklist",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

autodoc_member_order = "bysource"
