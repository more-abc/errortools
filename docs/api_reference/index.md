# API Reference

Complete reference documentation for every public symbol in
**errortools**.  The pages below are generated from the docstrings in
the source tree using {mod}`sphinx.ext.autodoc`; if you spot anything
missing or inaccurate, please open an issue on GitHub.

```{toctree}
---
maxdepth: 2
caption: Contents
---

version
```

## Package layout

errortools is shipped as a single ``errortools`` package that re-exports
the contents of its submodules.  The reference below follows the same
layout — every page corresponds to one subpackage or module.

```{toctree}
---
maxdepth: 1
caption: Subpackages
glob:
---

../api_*
```

## Conventions

Every documented object follows the same conventions as the standard
library and the [pytest](https://docs.pytest.org/) API reference:

* Type hints use modern {pep}`585` syntax (``list[int]``,
  ``type[Exception]``) where possible.
* Docstrings follow the
  [Google style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html);
  sections like `Args`, `Returns`, `Raises`, and `Example` are
  rendered as a structured parameter list.
* Cross-references use Sphinx roles — ``{func}`~errortools.ignore.ignore```,
  ``{class}`~errortools.classes.PureBaseException```, etc.  They
  resolve to the corresponding entry on this page.

## Exception handling

### {mod}`errortools.ignore`

Context managers and decorators that suppress exceptions and warnings.

```{eval-rst}
.. automodule:: errortools.ignore
   :members:
   :undoc-members:
   :show-inheritance:
```

### {mod}`errortools.raises`

Helpers for raising one or many exceptions at once.

```{eval-rst}
.. automodule:: errortools.raises
   :members:
   :undoc-members:
   :show-inheritance:
```

## Decorators

### {mod}`errortools.decorator`

Call-stack wrappers — retry, timeout, cache, and deprecation.

```{eval-rst}
.. automodule:: errortools.decorator
   :members:
   :undoc-members:
   :show-inheritance:
```

### {mod}`errortools.descriptor`

Error-aware descriptors used to attach metadata to exceptions.

```{eval-rst}
.. automodule:: errortools.descriptor
   :members:
   :undoc-members:
   :show-inheritance:
```

## Custom exceptions

### {mod}`errortools.classes`

Structured exception and warning classes, plus the
{class}`~errortools.classes.BaseErrorCodes` factory.

```{eval-rst}
.. automodule:: errortools.classes
   :members:
   :undoc-members:
   :show-inheritance:
```

## Future module

### {mod}`errortools.future`

Zero-overhead exception handling for hot paths.

```{eval-rst}
.. automodule:: errortools.future
   :members:
   :undoc-members:
   :show-inheritance:
```

## Logging

### {mod}`errortools.logging`

A Loguru-inspired structured logger with no external dependencies.

```{eval-rst}
.. automodule:: errortools.logging
   :members:
   :undoc-members:
   :show-inheritance:
```

## Type aliases

The following aliases are exposed in {mod}`errortools.typing` and
{mod}`errortools.classes` for IDE-friendly code.

```{eval-rst}
.. autodata:: errortools.typing.ExceptionType
   :no-value:
```

```{eval-rst}
.. autodata:: errortools.typing.WarningType
   :no-value:
```

```{eval-rst}
.. autodata:: errortools.typing.AnyErrorCode
   :no-value:
```

## Protocols

Lightweight {pep}`544` protocols describing duck-typed exception
contracts.

```{eval-rst}
.. automodule:: errortools.classes.protocol
   :members:
   :undoc-members:
   :show-inheritance:
```

## Version utilities

Lightweight helpers for representing, parsing, and comparing the
package's own ``(major, minor, patch)`` version triple programmatically.

- {class}`~errortools.version.VersionInfo` — a hashable, totally-ordered
  dataclass for an individual version triple.
- {func}`~errortools.version.get_version_tuple` — parse a
  dotted-decimal version string into a ``(major, minor, patch)`` tuple.

See {doc}`version` for the full reference, or read the source-level
documentation:

```{eval-rst}
.. automodule:: errortools.version
   :members:
   :undoc-members:
   :show-inheritance:
```
