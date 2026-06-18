"""Doctest suite for the :mod:`errortools` module.

This package contains doctest-based test modules covering every public
area of the ``errortools`` library:

* exception helpers (``raises``, ``assert_raises``, ``raises_all``, ``reraise``)
* exception suppression (``ignore``, ``ignore_subclass``, ``ignore_warns``)
* ``errno`` introspection (``get_errno_name``, ``get_errno_message``, ...)
* predefined error / warning classes (``InvalidInputError``, ``BaseWarning``, ...)
* decorators (``error_cache``, ``suppress``, ``convert``, ``timeout``, ``retry``, ...)
* descriptors (``ErrorMsg``, ``NonBlankErrorMsg``)
* the lightweight plugin registry (``register``, ``get``, ``run``, ...)
* version / package metadata

Running the suite
-----------------

The doctests in this package can be executed in three equivalent ways:

1. Via the built-in :mod:`doctest` module from the project root::

       python -m doctest testing/doctest/test_raises.py -v
       python -m doctest testing/doctest/test_ignore.py -v
       ...

2. Via pytest's ``--doctest-modules`` flag (recommended)::

       pytest testing/doctest --doctest-modules -v

3. Programmatically from Python::

       >>> from testing.doctest import run_doctests
       >>> run_doctests(verbose=False)  # doctest: +SKIP

Quick sanity check
------------------

The library itself can be imported normally::

    >>> import errortools
    >>> "raises" in errortools.__all__
    True
    >>> "ignore" in errortools.__all__
    True
    >>> "deprecated" in errortools.__all__
    True

The version string is always available and is a non-empty ``str``::

    >>> isinstance(errortools.__version__, str)
    True
    >>> len(errortools.__version__) > 0
    True

A few of the most common public names resolve to the expected classes
or functions::

    >>> errortools.raises([ValueError], ["oops"])  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: oops

    >>> with errortools.ignore(KeyError):
    ...     {}["missing"]
    >>> errortools.has("__never_registered__")
    False
"""

from __future__ import annotations

import doctest
import importlib
import pathlib
import sys
from typing import Iterable

__all__ = [
    "run_doctests",
    "list_doctest_modules",
]

# Directory that holds this package's __init__.py
_PACKAGE_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent
# Project root (the directory that contains both ``errortools/`` and
# ``_errortools/``).  Adding it to ``sys.path`` makes ``import errortools``
# work no matter where the doctests are invoked from.
_PROJECT_ROOT: pathlib.Path = _PACKAGE_DIR.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def list_doctest_modules() -> list[str]:
    """Return the dotted names of every doctest module shipped in this package.

    The list excludes internal modules (those whose name starts with an
    underscore) and the package's own ``__init__``.

    Returns:
        A list of fully-qualified module names sorted alphabetically.
    """
    names: list[str] = []
    for path in sorted(_PACKAGE_DIR.glob("test_*.py")):
        stem = path.stem
        if stem.startswith("_"):
            continue
        names.append(f"{__name__}.{stem}")
    return names


def run_doctests(
    modules: Iterable[str] | None = None,
    *,
    verbose: bool = False,
    raise_on_error: bool = False,
) -> bool:
    """Run every doctest in this package and return ``True`` on success.

    Args:
        modules: Optional iterable of dotted module names to test.  When
            ``None`` (the default), :func:`list_doctest_modules` is used.
        verbose: If ``True``, print a summary for each tested module.
        raise_on_error: If ``True``, re-raise an ``AssertionError`` instead
            of returning ``False`` when any doctest fails.

    Returns:
        ``True`` when every doctest passes; ``False`` otherwise.
    """
    targets = list(modules) if modules is not None else list_doctest_modules()
    if not targets:
        return True

    finder = doctest.DocTestFinder()
    runner_class = doctest.DebugRunner if verbose else doctest.DocTestRunner
    overall_ok = True

    for dotted_name in targets:
        module = importlib.import_module(dotted_name)
        runner = runner_class(verbose=verbose)
        tests = finder.find(module, name=dotted_name)
        for test in tests:
            result = runner.run(test)
            if result.failed:
                overall_ok = False
                break

        if verbose:
            print(f"  {dotted_name}: {runner.tries} tried, {runner.failures} failed")

        if not overall_ok and raise_on_error:
            raise AssertionError(f"doctests failed in {dotted_name!r}")

    return overall_ok


if __name__ == "__main__":
    success = run_doctests(verbose=True)
    sys.exit(0 if success else 1)
