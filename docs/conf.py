# autopep8: off
"""Sphinx configuration for the errortools documentation.

This configuration follows the conventions used by the official Python
and pytest documentation projects:

* MyST for Markdown (``*.md``) sources, with a fenced-block syntax that
  stays close to plain Markdown for readers but renders to rich
  reStructuredText for Sphinx.
* The `Furo`_ theme (a modern, accessible, Read-the-Docs-friendly
  alternative) — easy to read and to navigate.
* `Sphinx autodoc` + `napoleon`_ to turn Google / NumPy style
  docstrings in the source tree into the API reference pages, the same
  way Python's own docs are built.
* `intersphinx`_ to cross-link to Python, the standard library,
  :mod:`typing`, and :mod:`pytest` so that references like
  ``:class:`Exception``` or ``:func:`pytest.raises``` resolve to the
  upstream documentation.
* `viewcode` to expose the source of every documented object in the
  HTML build.
* `copybutton` to add a one-click *copy* button on every code block.

.. _Furo: https://pradyunsg.me/furo/
.. _Sphinx autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
.. _napoleon: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
.. _intersphinx: https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
"""

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from __future__ import annotations

import os
import sys

# Make the project root importable so ``autodoc`` can pull docstrings
# from ``_errortools.*`` and ``errortools.*`` without an editable install.
_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.dirname(_ROOT))

from _errortools.version import __version_tuple__

project = "errortools"
author = "aiwonderland and the more-abc team"
copyright = "(C) 2026 aiwonderland and the more-abc team"
release = f"{__version_tuple__[0]}.{__version_tuple__[1]}"
version = f"{__version_tuple__[0]}.{__version_tuple__[1]}.{__version_tuple__[2]}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Minimum reST conventions enforced in *.md — kept tiny on purpose so
# the docs read like prose.
default_role = "obj"
nitpicky = False  # Don't fail the build on cross-reference warnings.

# Patterns to exclude from the build, on top of Sphinx defaults.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**.ipynb_checkpoints",
]

# -- Extensions --------------------------------------------------------------

# Keep this list ordered alphabetically; it is easier to scan and to
# diff in pull requests.  All extensions used here are part of the
# standard Sphinx ecosystem (no first-party plugins).
extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

# -- MyST (Markdown) configuration ------------------------------------------
# https://myst-parser.readthedocs.io/en/latest/configuration.html

myst_enable_extensions = [
    "colon_fence",  # ```python … ``` fenced blocks with an info string
    "dollarmath",  # $LaTeX$ inline + display math
    "tasklist",  # GitHub-style - [ ] checkboxes
]
myst_heading_anchors = 3  # Auto-generate anchors for h1..h3.
myst_ref_domains = ("py", "std")
myst_crossrefs = True  # Allow [text](:role:`target`) cross-references.

# -- Napoleon (Google / NumPy style docstrings) ----------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
#
# Defaults follow the Google style guide; the explicit settings make
# the project policy obvious to future maintainers.

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = {
    # Map our local type aliases to their canonical form so the
    # generated docs read identically to the source.
    "ExceptionType": "type[Exception]",
    "WarningType": "type[Warning]",
}

# -- Autodoc configuration --------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "show-inheritance": True,
    "undoc-members": True,
    "exclude-members": "__weakref__,__dict__,__module__,__init_subclass__",
}
autodoc_member_order = "bysource"
autodoc_typehints = "description"  # Render type hints in the body, not the signature.
autodoc_typehints_format = "short"
autodoc_preserve_defaults = True  # Keep default values visible in signatures.
autoclass_content = "class"  # Document both __init__ and the class itself.

# -- Intersphinx -------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
#
# Each entry lets us cross-reference symbols from another project's
# docs (e.g. ``:class:`Exception``` → Python docs, ``:func:`pytest.raises```
# → pytest docs).  The ``None`` inventory is fetched at build time.

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pytest": ("https://docs.pytest.org/en/stable", None),
    "typing": (
        "https://docs.python.org/3/library/typing.html",
        None,
    ),
}
intersphinx_disabled_reftypes = ["*"]

# -- Copybutton --------------------------------------------------------------
# https://sphinx-copybutton.readthedocs.io/

copybutton_prompt_text = r">>> |\.\.\. |\$ "  # Strip REPL prompts from copy.
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = False

# -- HTML output -------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

templates_path = ["_templates"]
html_static_path = ["_static"]
html_last_updated_fmt = "%Y-%m-%d"

# Markdown is the canonical source format — keep .md as the build entry
# point and ignore .rst.  This keeps the docs contributor-friendly
# (writers can use GitHub-flavoured Markdown) while still benefiting
# from Sphinx's full extension ecosystem.
source_suffix = {
    ".md": "markdown",
}

html_theme = "furo"
html_title = f"errortools {version}"
html_short_title = "errortools"
html_logo = "_static/img/main.png"
html_favicon = "_static/img/main.png"
html_theme_options = {
    "navigation_with_keys": True,
    "sidebar_hide_name": False,
    "light_css_variables": {
        "color-brand-primary": "#4F46E5",
    },
    "dark_css_variables": {
        "color-brand-primary": "#A78BFA",
    },
}
