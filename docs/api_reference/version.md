# Version Utilities

The version utilities provide a small, focused API for representing,
parsing, and comparing the package's own version triple
``(major, minor, patch)`` programmatically.

The module lives at `_errortools.version` and is re-exported from the
top-level `errortools` package so that downstream code can do::

    from errortools import VersionInfo, get_version_tuple

```{toctree}
---
maxdepth: 2
caption: Contents
---
```


## Module-level constants

The `_errortools.version` module exposes the current release in three
forms, each duplicated under both a dunder name (PEP 396 / packaging
convention) and a lower-case alias:

| Constant        | Type                | Description                                      |
| --------------- | ------------------- | ------------------------------------------------ |
| `__version__`   | `str`               | Dotted-decimal string such as ``"3.5.1"``.       |
| `version`       | `str`               | Lower-case alias of `__version__` (same object). |
| `__version_tuple__` | `tuple[int, int, int]` | ``(major, minor, patch)`` triple.           |
| `version_tuple` | `tuple[int, int, int]` | Lower-case alias of `__version_tuple__`.     |
| `__commit_id__` | `str \| None`       | Git commit hash for source builds, else `None`. |
| `commit_id`     | `str \| None`       | Lower-case alias of `__commit_id__`.             |

The lower-case names refer to the *same* objects as their dunder
counterparts, so identity-based assertions (`x is y`) hold.

```python
>>> import errortools
>>> errortools.version is errortools.__version__
True
>>> errortools.version_tuple is errortools.__version_tuple__
True
>>> errortools.commit_id is errortools.__commit_id__
True
>>> errortools.__version_tuple__
(3, 5, 1)
```


## `VersionInfo`

```{eval-rst}
.. autoclass:: errortools.VersionInfo
   :members:
   :undoc-members:
   :show-inheritance:
```

### Overview

`VersionInfo` is a small `@dataclass` (with `__slots__`) that holds
three integer components — `major`, `minor`, `patch` — and makes them
fully comparable and hashable.

```python
>>> from errortools import VersionInfo
>>> v = VersionInfo(3, 5, 1)
>>> v
VersionInfo(major=3, minor=5, patch=1)
>>> str(v)
'3.5.1'
```

### Construction

The dataclass accepts any three integers; the values are stored
verbatim (no range validation is performed):

```python
>>> VersionInfo(3, 5, 1)
VersionInfo(major=3, minor=5, patch=1)
>>> VersionInfo(0, 0, 0)
VersionInfo(major=0, minor=0, patch=0)
```

The `from_str` classmethod parses a dotted-decimal string into a
`VersionInfo`:

```python
>>> VersionInfo.from_str("3.5.1")
VersionInfo(major=3, minor=5, patch=1)
>>> VersionInfo.from_str("3.2")            # missing patch -> 0
VersionInfo(major=3, minor=2, patch=0)
>>> VersionInfo.from_str("3")              # missing minor/patch -> 0/0
VersionInfo(major=3, minor=0, patch=0)
>>> VersionInfo.from_str("1.2.3.4.5")      # extra components discarded
VersionInfo(major=1, minor=2, patch=3)
```

A `ValueError` is raised for empty strings, trailing dots, or any
non-numeric component:

```python
>>> VersionInfo.from_str("")
Traceback (most recent call last):
...
ValueError: Invalid version string: ''
>>> VersionInfo.from_str("3.2.")
Traceback (most recent call last):
...
ValueError: Invalid version string: '3.2.'
>>> VersionInfo.from_str("3.2.a")
Traceback (most recent call last):
...
ValueError: Invalid version string: '3.2.a'
```

### Conversion

`to_tuple()` returns the components as a plain `(major, minor, patch)`
tuple of `int`s:

```python
>>> VersionInfo(3, 5, 1).to_tuple()
(3, 5, 1)
```

### Equality and hashing

Two `VersionInfo` instances are equal iff their three components are
equal. Because the class defines `__hash__`, instances can be used as
dictionary keys or stored in sets:

```python
>>> VersionInfo(3, 5, 1) == VersionInfo(3, 5, 1)
True
>>> VersionInfo(3, 5, 1) != VersionInfo(3, 5, 2)
True
>>> {VersionInfo(1, 0, 0), VersionInfo(1, 0, 0), VersionInfo(2, 0, 0)}
{VersionInfo(major=1, minor=0, patch=0), VersionInfo(major=2, minor=0, patch=0)}
>>> mapping = {VersionInfo(1, 0, 0): "v1", VersionInfo(2, 0, 0): "v2"}
>>> mapping[VersionInfo(2, 0, 0)]
'v2'
```

Equality against an unrelated type returns `False` (Python's standard
fallback when both `__eq__` methods return `NotImplemented`):

```python
>>> VersionInfo(1, 0, 0) == "1.0.0"
False
>>> VersionInfo(1, 0, 0) == (1, 0, 0)
False
```

### Ordering

`VersionInfo` is totally ordered, component by component, the same way
Python compares integer tuples:

| Operator | Meaning                                         |
| -------- | ----------------------------------------------- |
| `<`      | strictly less (lexicographic on components)     |
| `<=`     | less than or equal                              |
| `>`      | strictly greater (lexicographic on components)  |
| `>=`     | greater than or equal                           |

```python
>>> VersionInfo(1, 9, 9) < VersionInfo(2, 0, 0)        # by major
True
>>> VersionInfo(1, 2, 9) < VersionInfo(1, 3, 0)        # by minor
True
>>> VersionInfo(1, 2, 3) < VersionInfo(1, 2, 4)        # by patch
True
```

This makes `VersionInfo` work directly with the standard library:

```python
>>> versions = [
...     VersionInfo(2, 0, 0),
...     VersionInfo(1, 1, 5),
...     VersionInfo(1, 2, 0),
...     VersionInfo(1, 2, 3),
... ]
>>> sorted(versions)
[VersionInfo(major=1, minor=1, patch=5), VersionInfo(major=1, minor=2, patch=0), VersionInfo(major=1, minor=2, patch=3), VersionInfo(major=2, minor=0, patch=0)]
>>> min(versions)
VersionInfo(major=1, minor=1, patch=5)
>>> max(versions)
VersionInfo(major=2, minor=0, patch=0)
```

### Memory layout

`VersionInfo` declares `__slots__` so instances do not carry a
`__dict__`. This makes the class a good fit for representing versions
in hot paths or in large in-memory collections:

```python
>>> VersionInfo(1, 2, 3).__slots__
('major', 'minor', 'patch')
```


## `get_version_tuple`

```{eval-rst}
.. autofunction:: errortools.get_version_tuple
```

### Overview

`get_version_tuple` is the parsing function that powers
`VersionInfo.from_str`. It is exposed on its own so callers that only
need the integer triple can skip the dataclass overhead.

```python
>>> from errortools import get_version_tuple
>>> get_version_tuple("3.5.1")
(3, 5, 1)
>>> get_version_tuple("3.2")            # missing patch -> 0
(3, 2, 0)
>>> get_version_tuple("3")              # missing minor/patch -> 0/0
(3, 0, 0)
>>> get_version_tuple("1.2.3.4.5")      # extra components discarded
(1, 2, 3)
```

### Error handling

A `ValueError` is raised when the input cannot be parsed. The error
message includes the offending input for easier debugging:

```python
>>> get_version_tuple("")
Traceback (most recent call last):
...
ValueError: Invalid version string: ''
>>> get_version_tuple("3.2.")
Traceback (most recent call last):
...
ValueError: Invalid version string: '3.2.'
>>> get_version_tuple("3.2.a")
Traceback (most recent call last):
...
ValueError: Invalid version string: '3.2.a'
>>> get_version_tuple("a.b.c")
Traceback (most recent call last):
...
ValueError: Invalid version string: 'a.b.c'
```


## When to use which?

- **Need the live package version?** Use `errortools.__version__`,
  `errortools.__version_tuple__`, or `errortools.__commit_id__`.
- **Need to parse an external version string?** Use
  `get_version_tuple` (raw triple) or `VersionInfo.from_str`
  (object form, comparable / hashable).
- **Need to compare or sort a collection of versions?** Use
  `VersionInfo` directly so you can rely on `==`, `<`, `<=`, `>`,
  `>=`, `sorted()`, `min()`, `max()`, and hashable containers.


## See also

- [PEP 396 – Module version numbers](https://peps.python.org/pep-0396/)
  — the convention followed by `__version__` and friends.
- [PEP 440 – Version Identification and Dependency Specification](https://peps.python.org/pep-0440/)
  — the broader versioning scheme used by ``setuptools`` and ``pip``.
  `VersionInfo` is intentionally simpler (only the integer triple) and
  does **not** attempt to parse pre-release / post-release / dev
  segments.
