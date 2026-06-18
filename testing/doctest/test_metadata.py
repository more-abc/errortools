"""Doctests for the version and metadata of :mod:`errortools`.

These examples demonstrate and verify the package-level metadata
exposed by :mod:`errortools`:

* :data:`errortools.__version__` / :func:`errortools.version`
* :data:`errortools.__version_tuple__` / :func:`errortools.version_tuple`
* :data:`errortools.__commit_id__` / :func:`errortools.commit_id`
* :data:`errortools.__author__` / :data:`errortools.__author_email__`
* :data:`errortools.__license__` / :data:`errortools.__title__`
* :data:`errortools.__description__` / :data:`errortools.__url__`
* :data:`errortools.__fullname__` / :data:`errortools.__slug__`
* :data:`errortools.__signature__` / :data:`errortools.__uid__`

The doctests can be executed via::

    python -m doctest testing/doctest/test_metadata.py -v

or simply by running :func:`testing.doctest.run_doctests`.


Version strings
---------------

``__version__`` is a non-empty dotted-decimal string that follows the
PEP 440 spirit::

    >>> import errortools
    >>> isinstance(errortools.__version__, str)
    True
    >>> bool(errortools.__version__)
    True
    >>> all(part.isdigit() for part in errortools.__version__.split("."))
    True

The legacy alias :func:`version` resolves to the same string::

    >>> errortools.version == errortools.__version__
    True

``__version_tuple__`` is the same information split into an
``(int, int, int)`` triple::

    >>> isinstance(errortools.__version_tuple__, tuple)
    True
    >>> len(errortools.__version_tuple__)
    3
    >>> all(isinstance(part, int) for part in errortools.__version_tuple__)
    True
    >>> errortools.version_tuple == errortools.__version_tuple__
    True
    >>> tuple(int(p) for p in errortools.__version__.split(".")) == errortools.__version_tuple__
    True

``__commit_id__`` is either ``None`` (for source-only builds) or a
non-empty string (for builds that bundle a commit hash)::

    >>> errortools.__commit_id__ is None or (
    ...     isinstance(errortools.__commit_id__, str)
    ...     and len(errortools.__commit_id__) > 0
    ... )
    True
    >>> errortools.commit_id is errortools.__commit_id__
    True


Author and licensing metadata
-----------------------------

The author and license metadata are populated as plain strings::

    >>> bool(isinstance(errortools.__author__, str) and errortools.__author__)
    True
    >>> bool(isinstance(errortools.__author_email__, str) and "@" in errortools.__author_email__)
    True
    >>> bool(isinstance(errortools.__license__, str) and errortools.__license__)
    True
    >>> bool(isinstance(errortools.__title__, str) and errortools.__title__)
    True
    >>> bool(isinstance(errortools.__url__, str) and errortools.__url__.startswith(("http://", "https://")))
    True
    >>> bool(isinstance(errortools.__description__, str) and errortools.__description__)
    True


Generated identifiers
---------------------

The four auto-generated identifiers are non-empty strings::

    >>> for name in ("__fullname__", "__slug__", "__signature__", "__uid__"):
    ...     value = getattr(errortools, name)
    ...     bool(isinstance(value, str) and len(value) > 0)
    True
    True
    True
    True


Top-level :mod:`errortools` package exposure
--------------------------------------------

All metadata attributes appear in the public ``__all__`` list of the
top-level package::

    >>> for name in (
    ...     "__version__", "__version_tuple__", "__commit_id__",
    ...     "version", "version_tuple", "commit_id",
    ...     "__author__", "__author_email__", "__copyright__",
    ...     "__description__", "__license__", "__title__", "__url__",
    ...     "__fullname__", "__signature__", "__slug__", "__uid__",
    ... ):
    ...     name in errortools.__all__
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
"""

from __future__ import annotations

__all__ = ["__doc__"]
