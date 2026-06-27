---
name: write-tests
description: Write pytest tests for a change in _errortools/.
when_to_use:
  - "add tests"
  - "cover this module"
  - "test X"
version: 0.1.0
applies_to: [errortools >= 3.5]
---

## Goal

Add a pytest test module that:

- follows the project's discovery conventions,
- covers the new behaviour including edge cases,
- is deterministic and fast (no network, no real `time.sleep`),
- runs under the existing `--doctest-modules` and `--cov=_errortools`
  defaults,
- reaches a high coverage of the touched module.

## Prerequisites

- [ ] `pip install pytest pytest-cov pytest-mypy-plugins`
- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md) §5.5.
- [ ] Find the matching test file under `testing/` (see the
      source↔test table in [`AGENTS_CHECK_LIST.md`](../AGENTS_CHECK_LIST.md#8-tests)).

## Procedure

1. **Pick the right test file** (or create a new one). The mapping
   used in this repo is:

   | Source | Test file |
   |--------|-----------|
   | `_errortools/ignore.py` | `testing/test_ignore.py` |
   | `_errortools/raises.py` | `testing/test_raises.py` |
   | `_errortools/decorator/*` | `testing/test_decorator.py` |
   | `_errortools/classes/*` | `testing/classes/test_*.py` |
   | `_errortools/logging/*` | `testing/logging/test_*.py` |
   | `_errortools/future.py` | `testing/submodules/test_future.py` |
   | `_errortools/version.py` | `testing/meta/test_version.py` + `testing/doctest/test_version.py` |
   | `_errortools/plugins.py` | `testing/test_plugins.py` |
   | `_errortools/descriptor/*` | `testing/test_descriptor.py` |
   | `_errortools/errno.py` | `testing/test_errno.py` |
   | `_errortools/typing.py` | `testing/test_typing.py` |
   | `BaseGroup` / `GroupErrors` | `testing/test_groups.py` |
   | data-driven helpers | `testing/test_data_driven.py` |

2. **Use the existing test class / function conventions.** Most tests
   are grouped under a class `Test<Feature>` (so `pytest` picks them
   up via `python_classes = ["Test*"]`). Functions are `test_<thing>`.
   No file extension other than `.py`.

3. **Mirror `testing/conftest.py` expectations.** It already adds the
   project root to `sys.path`; you do not need to touch `sys.path` in
   your tests.

4. **Write a coverage-shaped suite.** Aim for:
   - **happy path** — the documented primary use case,
   - **edge cases** — empty inputs, `None`, subclasses, large inputs,
   - **error paths** — wrong types, out-of-range values, `ValueError`
     / `TypeError` contracts,
   - **identity / equality** — `is` vs `==` only where the source
     explicitly documents it,
   - **thread-safety hooks** — a single `threading` test if the code
     claims to be safe.

5. **Avoid**:
   - real `time.sleep` / `asyncio.sleep` (mock or use `freezegun` /
     `asyncio.sleep(0)` if needed),
   - network calls (`requests`, `urllib`, `socket`),
   - reading or writing real files outside `tmp_path`,
   - relying on the global
     `filterwarnings = ["ignore::DeprecationWarning"]` — emit a
     specific subclass and assert against it.

6. **For doctests**, add `>>>` / `...` blocks to the source docstring.
   The CI runs `pytest --doctest-modules --no-cov` and will fail if the
   doctest output drifts.

7. **Run the new tests in isolation** first, then the full suite:

   ```bash
   pytest testing/<area>/test_<file>.py -v
   pytest
   pytest --doctest-modules --no-cov
   ```

8. **Update [`AGENTS_CHECK_LIST.md`](../AGENTS_CHECK_LIST.md) §8** if
   the test file is genuinely new (not in the table above).

## Examples

### Real example — `testing/test_ignore.py`

```python
import warnings
import pytest

from _errortools.ignore import (
    ignore,
    ignore_subclass,
    ignore_warns,
    fast_ignore,
)
from _errortools.wrappers.ignore import IgnoredError, ErrorIgnoreWrapper


class TestIgnore:
    def test_suppresses_specified_exception(self):
        with ignore(KeyError):
            raise KeyError("should be suppressed")

    def test_unrelated_exception_propagates(self):
        with pytest.raises(RuntimeError):
            with ignore(KeyError):
                raise RuntimeError("not suppressed")

    def test_subclass_not_suppressed(self):
        with pytest.raises(KeyError):
            with ignore(LookupError):
                raise KeyError("subclass should not be suppressed")
```

### Real example — async retry test

```python
import asyncio
import pytest

from _errortools.decorator.retry import retry


@pytest.mark.asyncio
async def test_retry_swallows_then_succeeds():
    attempts = {"n": 0}

    @retry(times=3, on=ValueError, delay=0)
    async def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise ValueError("nope")
        return "ok"

    assert await flaky() == "ok"
    assert attempts["n"] == 3
```

## Verification

```bash
# The new tests pass
pytest testing/<area>/test_<file>.py -v

# Coverage on the touched module is high
pytest --cov=_errortools --cov-report=term-missing

# Doctest still passes
pytest --doctest-modules --no-cov

# Whole suite still green
pytest
```

## Common pitfalls

- ❌ **Skipping the failure case.** Tests that only cover the happy
  path are a regression hazard.
- ❌ **Using real `time.sleep`.** A 1-second test × 50 tests × 3 CI
  jobs is a CI tax; fake it.
- ❌ **Asserting on `repr()` strings.** They are not part of the public
  contract; assert on documented attributes instead.
- ❌ **Mutating global state without cleanup.** Plugin registry,
  `logger` sinks, and the deprecated-name path all leak across tests
  if you do not reset them in a `fixture` or `teardown`.
- ❌ **Importing from `errortools` (the public shim) when you should
  import from `_errortools`.** Tests are the right place to lock in the
  internal layout; use the public shim only in a smoke test.

## Related skills

- [`add-public-api.md`](add-public-api.md) — for the new symbol
  itself.
- [`add-decorator.md`](add-decorator.md) — when the symbol is a
  decorator (async/sync branching needs special tests).
- [`add-exception-class.md`](add-exception-class.md) — when the symbol
  is an exception.
- [`optimize-hot-path.md`](optimize-hot-path.md) — when the new tests
  must also cover a benchmark regression.
