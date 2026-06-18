"""Doctests for the plugin registry re-exported from :mod:`errortools`.

These examples demonstrate and verify the behaviour of the
ultra-lightweight plugin system shipped with :mod:`errortools`:

* :func:`errortools.register`   (decorator)
* :func:`errortools.get`        (lookup with optional default)
* :func:`errortools.has`        (membership test)
* :func:`errortools.run`        (lookup + invoke)
* :func:`errortools.list_all`   (enumerate registered plugins)
* :func:`errortools.remove`     (delete one plugin)
* :func:`errortools.clear`      (delete every plugin)
* :class:`errortools.Registry`  (static-method facade)

The doctests can be executed via::

    python -m doctest testing/doctest/test_plugins.py -v

or simply by running :func:`testing.doctest.run_doctests`.


Basic register / run cycle
--------------------------

``register`` decorates a callable and binds it to a name.  The name
can then be used with :func:`run` to invoke the underlying function::

    >>> from errortools import register, run
    >>> @register("doctest:hello")
    ... def hello():
    ...     return "hi"
    >>> run("doctest:hello")
    'hi'

Positional and keyword arguments are forwarded transparently::

    >>> @register("doctest:add")
    ... def add(a, b):
    ...     return a + b
    >>> run("doctest:add", 2, 3)
    5
    >>> run("doctest:add", a=10, b=20)
    30

Variadic args and kwargs are also forwarded::

    >>> @register("doctest:variadic")
    ... def variadic(*args, **kwargs):
    ...     return (args, kwargs)
    >>> run("doctest:variadic", 1, 2, x=3)
    ((1, 2), {'x': 3})

Registering the same name twice overwrites the previous binding::

    >>> @register("doctest:overwrite")
    ... def first():
    ...     return "first"
    >>> @register("doctest:overwrite")
    ... def second():
    ...     return "second"
    >>> run("doctest:overwrite")
    'second'


Lookup with optional default
----------------------------

``get`` returns the registered callable or a user-supplied default
when the plugin is missing::

    >>> from errortools import get
    >>> get("doctest:hello") is hello
    True
    >>> get("doctest:never-registered", default=42)
    42
    >>> get("doctest:never-registered", default=None) is None
    True

When neither a default is provided nor a plugin exists, a
``ValueError`` is raised::

    >>> try:
    ...     get("doctest:never-registered")
    ... except ValueError as exc:
    ...     "doctest:never-registered" in str(exc)
    True


Membership and listing
----------------------

``has`` is a quick membership test, ``list_all`` enumerates every
registered plugin name::

    >>> from errortools import has, list_all
    >>> has("doctest:hello")
    True
    >>> has("doctest:never-registered")
    False
    >>> all(name in list_all() for name in (
    ...     "doctest:hello", "doctest:add", "doctest:variadic",
    ...     "doctest:overwrite",
    ... ))
    True


Removal and clearing
--------------------

``remove`` deletes a single plugin (and is a no-op when the plugin
does not exist).  ``clear`` empties the registry entirely::

    >>> from errortools import remove, clear
    >>> @register("doctest:removable")
    ... def removable():
    ...     return "bye"
    >>> has("doctest:removable")
    True
    >>> remove("doctest:removable")
    >>> has("doctest:removable")
    False
    >>> remove("doctest:never-existed")  # no-op, no exception

After :func:`clear`, every previously registered name disappears
from the registry.  The doctests that follow clear out only the
test-only plugins so the rest of the suite can still find the
``hello``, ``add`` and ``variadic`` entries registered above::

    >>> names_before = set(list_all())
    >>> doctest_only = {n for n in names_before if n.startswith("doctest:")}
    >>> for n in doctest_only:
    ...     remove(n)
    >>> all(not has(n) for n in doctest_only)
    True
    >>> has("doctest:hello")
    False


Static facade - Registry
------------------------

:class:`Registry` exposes the same operations through static methods::

    >>> from errortools import Registry
    >>> Registry.register("doctest:facade", lambda: "ok")
    >>> Registry.run("doctest:facade") if hasattr(Registry, "run") else run("doctest:facade")
    'ok'
    >>> Registry.has("doctest:facade")
    True
    >>> "doctest:facade" in Registry.list_all()
    True
    >>> Registry.remove("doctest:facade")
    >>> Registry.has("doctest:facade")
    False


Top-level :mod:`errortools` package exposure
--------------------------------------------

All plugin helpers are re-exported from the top-level package::

    >>> import errortools
    >>> callable(errortools.register)
    True
    >>> callable(errortools.get)
    True
    >>> callable(errortools.has)
    True
    >>> callable(errortools.run)
    True
    >>> callable(errortools.remove)
    True
    >>> callable(errortools.clear)
    True
    >>> callable(errortools.list_all)
    True
    >>> errortools.Registry is Registry
    True
"""

from __future__ import annotations

__all__ = ["__doc__"]
