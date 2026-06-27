---
name: optimize-hot-path
description: Add a C-accelerated helper to _speedup.c with a pure-Python fallback.
when_to_use:
  - "speed up"
  - "use C extension"
  - "add __slots__"
  - "optimize hot path"
version: 0.1.0
applies_to: [errortools >= 3.5]
---

## Goal

Make a hot path faster by:

- either: adding a C function in `_errortools/_speedup.c` and exposing
  it through the Python importer with a pure-Python fallback, or
- by reducing per-instance overhead in pure-Python code
  (`__slots__`, avoiding `cast`, inlining trivial checks).

The skill is the **wrong choice** if the gain is not measurable.
Always add a benchmark.

## Prerequisites

- [ ] `pip install pytest pytest-benchmark`
- [ ] A working C toolchain on the build host (`gcc` / `clang` on
      POSIX, MSVC build tools on Windows).
- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md) §5.6.
- [ ] Read `_errortools/_speedup.c` header comments (feature-gate
      conventions).
- [ ] A baseline benchmark so you can prove the win.

## Procedure

1. **Measure first.** Add a `pytest-benchmark` test under
   `testing/benchmark/` that captures the current overhead. Save the
   baseline numbers in the PR description.

2. **Decide the shape of the optimization**:
   - If the win is in `__exit__` / `isinstance` / `list.append` on a
     hot path, a C function in `_speedup.c` is the right answer.
   - If the win is in object size or attribute lookup, add `__slots__`
     to the relevant class.
   - If the win is in an exception-type check, add a small C helper
     (see `fast_suppress_exit` / `fast_append_exception`).

3. **Write the C helper in `_errortools/_speedup.c`.** Follow the
   existing style:
   - Feature-gate modern CPython API with `#if PY_VERSION_HEX >= …`
     macros (`SPEEDUP_IS_NONE`, `SPEEDUP_NEW_REF`, etc.).
   - Provide an identity fast path before falling back to
     `PyObject_IsSubclass`.
   - Return a fresh `bool` (`Py_True` / `Py_False`) on success,
     `NULL` on error; never return `-1` directly to Python.
   - Add a `PyMethodDef` entry at the bottom and bump the module
     table size if you add a new function.

4. **Expose the helper with a pure-Python fallback** in the importing
   module. The pattern is:

   ```python
   try:
       from _errortools._speedup import (  # type: ignore[import-not-found]
           fast_append_exception,
           fast_suppress_exit,
       )
   except ImportError:

       def fast_append_exception(lst: list[BaseException], exc: BaseException) -> None:
           lst.append(exc)

       def fast_suppress_exit(
           typ: Union[type[BaseException], None],
           excs: Union[type[BaseException], tuple[type[BaseException], ...]],
       ) -> bool:
           return typ is not None and issubclass(typ, excs)
   ```

5. **Add `__slots__` to the calling class** (e.g. `super_fast_ignore`,
   `super_fast_catch`, `super_fast_reraise`, `ExceptionCollector`).
   Do not add `__dict__`; the project has zero tolerance for the
   regression that introduces it.

6. **Re-benchmark.** The C path should be measurably faster; the
   pure-Python fallback should be no slower than the previous code.

7. **Update `_errortools/__main__.py`'s `--debug` output.** The
   `_debug_info` function prints whether the C extension is loaded; if
   you add a new function, make sure that path still works.

8. **Add a benchmark** under `testing/benchmark/test_future_perf.py`
   (or a new file). Keep the benchmark deterministic: use
   `pytest-benchmark` with `disable_gc=True` and a fixed `data` set.

9. **Update `ChangeLog.md`** with a `## [Unreleased]` bullet
   describing the optimization and the measured improvement.

## Examples

### Real example — `fast_suppress_exit`

```c
static PyObject *py_fast_suppress_exit(PyObject *self, PyObject *args) {
    PyObject *typ = NULL, *excs = NULL;
    if (!PyArg_ParseTuple(args, "OO", &typ, &excs)) {
        return NULL;
    }
    int fast = identity_match(typ, excs);
    if (fast == 1) {
        Py_RETURN_TRUE;
    }
    if (fast == 0) {
        Py_RETURN_FALSE;
    }
    int result = PyObject_IsSubclass(typ, excs);
    return bool_from_issubclass(result);
}
```

### Real example — `__slots__` on `super_fast_ignore`

```python
class super_fast_ignore:
    """Ultra-lightweight context manager to suppress exceptions."""

    __slots__ = ("excs",)

    def __init__(self, *excs: _ExcType) -> None:
        self.excs = excs

    def __enter__(self) -> None:
        return

    def __exit__(self, typ: Union[_ExcType, None], *_) -> bool:
        return bool(fast_suppress_exit(typ, self.excs))
```

## Verification

```bash
# C extension builds
python -c "from _errortools._speedup import fast_append_exception, fast_suppress_exit; print('ok')"

# Pure-Python fallback also works (simulate a missing build)
python -c "
import sys, importlib
sys.modules['_errortools._speedup'] = None
import _errortools.future
print('fallback ok')
"  # this is illustrative; the project relies on the ImportError branch.

# Benchmark improved
pytest testing/benchmark/test_future_perf.py -v

# Quality gate
black .
flake8
mypy _errortools/
pytest
pytest --doctest-modules --no-cov
```

## Common pitfalls

- ❌ **Optimizing without a benchmark.** "I think it will be faster" is
  not evidence. Always measure before and after.
- ❌ **Forgetting the pure-Python fallback.** The project ships wheels
  that may not include the C build; a missing fallback breaks the
  import.
- ❌ **Adding per-instance `__dict__`.** `__slots__` is the whole point
  of the optimization; do not undo it by assigning new attributes.
- ❌ **Using `cast(...)` in the wrapper.** `cast` is pure Python
  overhead; prefer a single conditional.
- ❌ **Skipping the feature-gate comments.** `_speedup.c` supports
  Python 3.8 onward; missing `#if PY_VERSION_HEX >= …` blocks break
  the minimum-supported-version build.
- ❌ **Re-introducing `traceback.format_exception` in the hot path.**
  It is the documented "no hidden allocations" rule; ignore it and
  the win is erased.

## Related skills

- [`add-public-api.md`](add-public-api.md) — when the optimization
  changes the public surface.
- [`write-tests.md`](write-tests.md) — every new helper needs tests
  in `testing/submodules/test_future.py` or similar.
- [`update-changelog.md`](update-changelog.md) — required.
