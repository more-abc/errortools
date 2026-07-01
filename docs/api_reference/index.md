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

## Conventions

Every documented object follows the same conventions as the standard
library and the [pytest](https://docs.pytest.org/) API reference:

* Type hints use modern {pep}`585` syntax (``list[int]``,
  ``type[Exception]``) where possible.
* Docstrings follow the
  [Google style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html);
  sections like `Args`, `Returns`, `Raises`, and `Example` are
  rendered as a structured parameter list.
* Cross-references use Sphinx roles — ``{func}`~errortoolsignore```,
  ``{class}`~errortools.PureBaseException```, etc.  They
  resolve to the corresponding entry on this page.


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


```{eval-rst}
.. autodata:: errortools.ExceptionType
   :no-value:
```

```{eval-rst}
.. autodata:: errortools.WarningType
   :no-value:
```

```{eval-rst}
.. autodata:: errortools.AnyErrorCode
   :no-value:
```


## Version utilities

Lightweight helpers for representing, parsing, and comparing the
package's own ``(major, minor, patch)`` version triple programmatically.

- {class}`~errortools.VersionInfo` — a hashable, totally-ordered
  dataclass for an individual version triple.
- {func}`~errortools.get_version_tuple` — parse a
  dotted-decimal version string into a ``(major, minor, patch)`` tuple.
