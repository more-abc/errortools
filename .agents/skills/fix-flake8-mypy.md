---
name: fix-flake8-mypy
description: Fix linting (flake8, mypy, autoflake, autopep8) errors.
when_to_use:
  - "fix flake8"
  - "fix mypy"
  - "lint clean-up"
  - "make CI green"
version: 0.1.0
applies_to: [errortools >= 3.5]
---

## Goal

Make `flake8`, `mypy`, `autoflake`, and `autopep8` exit `0` on the
files you touched without regressing any other file.

## Prerequisites

- [ ] `pip install black flake8 mypy autoflake autopep8 pyflakes flake8-comprehensions flake8-bugbear pytest pytest-mypy-plugins`
- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md) §5.4 and
      [`.flake8`](../../.flake8).
- [ ] Identify the exact error code(s) reported by the linter.

## Procedure

1. **Run the linters to capture the error codes.** Pipe the output to a
   file so you can search it later.

   ```bash
   black . > /dev/null
   flake8 . 2>&1 | tee /tmp/flake8.txt
   mypy _errortools/ 2>&1 | tee /tmp/mypy.txt
   python -m pyflakes _errortools/ 2>&1 | tee /tmp/pyflakes.txt
   flake8 --max-complexity 8 --select C901 _errortools/ 2>&1 | tee /tmp/c901.txt
   ```

2. **Triage.** Most `flake8` complaints are fixable automatically:

   ```bash
   black .                              # formatting
   autoflake --remove-all-unused-imports \
             --remove-unused-variables \
             --ignore-init-module-imports -r -i .
   autopep8 . --recursive --in-place --pep8-passes 2000
   ```

3. **For the remaining errors**, fix them by hand using the table
   below. Re-run the relevant linter after every edit so you do not
   mask one error with another.

4. **For `mypy` errors**:
   - Reuse the project's existing type aliases
     (`ExceptionType`, `WarningType`, `PureBaseExceptionType`,
     `BaseErrorCodesType`, `AnyErrorCode`, `TracebackType`,
     `FrameType`).
   - Avoid `# type: ignore` unless there is a real reason; if you must
     use it, add a one-line comment.
   - For Python 3.8 / 3.9 compat, **never** use `X | Y` in runtime
     code; use `Union[X, Y]`.
   - For Python 3.10 compat, gate `TypeAlias` behind
     `if sys.version_info <= (3, 10):`.

5. **For cyclomatic complexity (C901)** errors, factor the offending
   function into smaller helpers. The threshold is **8** (see
   `code-complexity.yml`).

6. **For `per-file-ignores`** in `.flake8`, only the file
   `_errortools/classes/protocol.py` is allowed to violate
   `E704`/`W504` — do not extend the ignore list.

7. **For `B042` (deprecated `except X, Y:` syntax)**, replace
   `except X, Y:` with `except (X, Y):` (real example: the
   `_errortools/errno.py` v3.1.1 / v3.1.2 fixes).

8. **For `B027` (empty method in abstract base)**, add a `noqa: B027`
   inline on the method *if* the method is intentionally empty (e.g.
   `BaseSink.close`).

## Common error codes — quick fix table

| Code | What it means | Fix |
|------|---------------|-----|
| `E501` | Line too long | Wrap / extract; project limit is 120, but `E501` is in the ignore list. Only watch for `B950` (flake8-bugbear) equivalents if they show up. |
| `E704` | Multiple statements on one line | Split. (Ignored in `protocol.py` only.) |
| `W503` | Line break before binary operator | Use natural wrapping; the project ignores it. |
| `W504` | Line break after binary operator | Same; ignored in `protocol.py`. |
| `B027` | Empty method in abstract base | Add `noqa: B027` inline if intentionally empty. |
| `B042` | Deprecated `except X, Y:` syntax | Use `except (X, Y):`. |
| `C901` | Function too complex (>8) | Factor into helpers. |
| `F401` | Module imported but unused | Remove the import (or `__all__` it). |
| `E402` | Import not at top of file | Move it; if it must stay, add `# noqa: E402`. |
| `F811` | Re-imported name in same scope | Rename the inner name. |
| `W293` | Whitespace on blank line | Remove. |

## Examples

### Real example — fixing `B042` from `ChangeLog.md`

```diff
--- a/_errortools/errno.py
+++ b/_errortools/errno.py
-        except AttributeError, TypeError:
+        except (AttributeError, TypeError):
             pass
```

```diff
--- a/_errortools/errno.py
+++ b/_errortools/errno.py
-    except ValueError, OSError:
+    except (ValueError, OSError):
         raise ValueError(f"Unknown error code: {code}")
```

### Real example — fixing `C901`

A long `main()` was split into a `_FLAG_ACTIONS` dispatch dict plus
named `_show_*` helpers — see the v3.4.9 entry in `ChangeLog.md` and
the resulting `_errortools/cli.py`.

## Verification

```bash
# All four linters must exit 0
black . && flake8 && mypy _errortools/ && \
    python -m pyflakes _errortools/ && \
    flake8 --max-complexity 8 --select C901 _errortools/

# Tests still pass
pytest testing
pytest --doctest-modules --no-cov
```

## Common pitfalls

- ❌ **Mass-applying `noqa` to silence errors.** `# noqa` is acceptable
  only when there is a *documented* reason. The bar is "is this
  exception listed in `.flake8` per-file-ignores?".
- ❌ **Disabling a rule globally in `.flake8`.** That hides future
  regressions; prefer fixing the code.
- ❌ **Using `cast(...)` to silence mypy.** Casts move the burden to
  runtime; prefer fixing the type or annotating more precisely.
- ❌ **Forgetting `flake8 --doctests`.** Doctests in source files
  must also be lint-clean.
- ❌ **Letting `autopep8` re-introduce formatting `black` disagrees
  with.** Run `black .` *after* `autopep8` so black is the final
  authority.

## Related skills

- [`add-public-api.md`](add-public-api.md) — if the lint fix changes the
  public surface.
