# PHILOSOPHY.md

> The values, tradeoffs, and opinions that shape `errortools`.
>
> Read this if you are deciding **whether** to make a change, not
> **how** to make it. For the latter, see
> [`.agents/AGENTS_PREVIEW.md`](.agents/AGENTS_PREVIEW.md) and
> [`.agents/AGENTS_CHECK_LIST.md`](.agents/AGENTS_CHECK_LIST.md).
> For reusable playbooks, see [`.agents/skills/`](.agents/skills/).
>
> For human contributors, see
> [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md).

> Something need change or refactor? Contact email <errortools.docs@proton.me>

---

## 1. Why this project exists

`errortools` exists to make Python's most over-loaded primitive — the
`try` / `except` block — a less hostile interface for the people who
have to write, read, and debug it.

Three concrete pain points motivate every design decision:

1. **Standard-library ergonomics are limited.** `contextlib.suppress`
   is silent and featureless; `raise … from …` is verbose; the
   `warnings` module is good but disconnected from the rest of the
   runtime; `logging` is configurable but heavy. We provide opinionated
   variants that pick a side.
2. **"Just catch `Exception`" leaks.** Code that swallows
   `BaseException` indiscriminately hides bugs. We make the narrow
   pattern (explicit tuples, subclass-aware suppression) the
   *default* pattern.
3. **Hot paths pay an unfair tax.** The CPython interpreter is fast,
   but every extra frame in a critical loop is real money. We ship a
   `__slots__`-only, C-accelerated path for users who measure and
   care.

If you only need the standard library, you do not need us. That is
fine.

---

## 2. Core principles

These are non-negotiable. If a change violates one of them, it does
not go in, even if it is technically clever.

### 2.1 Backward compatibility is a feature

- We never silently delete a public name. The deprecation pipeline
  (`_DEPRECATED_NAMES` in
  [`errortools/__init__.py`](errortools/__init__.py)) is the only
  blessed way to retire a symbol, and even then the symbol remains
  importable until the documented removal version.
- We never change a documented signature in a backward-incompatible
  way inside a major version. New parameters are always keyword-only
  with sensible defaults.
- We do not "fix" typos in the public API. The typo is part of the
  contract.

### 2.2 Explicit is better than implicit

- `ignore(Exception)` rejects non-`Exception` arguments with
  `TypeError`. A bare `ignore()` is a programming error, not a
  feature.
- `BaseErrorCodes` factories require you to call them as classmethods
  (`BaseErrorCodes.not_found("user #42")`), not as constructors.
  The form is part of the contract.
- `retry(times=-1)` is a `ValueError`, not a silent infinite loop.

### 2.3 Narrower is better

- A bare `except:` is a code smell. We always narrow to a tuple.
- A bare `except BaseException` is a code smell. Same treatment.
- The C extension never widens an exception match; it only narrows
  it.

### 2.4 The user owns their data

- The project has **zero runtime dependencies** beyond
  `namebyauthor` and `typing_extensions`. We will not add `requests`,
  `colorama`, `rich`, or anything else to make our lives easier at
  the cost of yours.
- `logger` does not configure the root logger. It owns its own
  sink registry. Users opt in.
- The plugin registry (`_REGISTRY` in
  [`_errortools/plugins.py`](_errortools/plugins.py)) is a plain
  `dict` with no thread-safety claims. Consumers who need safety wrap
  it; we do not impose a `threading.Lock` on every reader.

### 2.5 Lazy by default

- `errortools.future`, `errortools.logging`, and `errortools.partial`
  are loaded through `__getattr__` so a `import errortools` does
  **not** pay the cost of importing the logger machinery.
- A new submodule is added to the `__getattr__` whitelist the day
  it is created, not later.

### 2.6 The simplest correct implementation wins

- `_errortools/__init__.py` is one line of comment for a reason: it
  has nothing to do. We do not pre-emptively fill it with re-exports
  or convenience shims.
- `BaseSink.close` is intentionally empty with a `# noqa: B027` —
  the method is a hook, not a bug.
- The whole logger is ~460 lines. The whole C extension is ~280
  lines. We are not building a framework.

---

## 3. Design tradeoffs

Every non-trivial design choice is a tradeoff. We list the ones we
have made explicitly so future maintainers can revisit them with
context.

### 3.1 Two-package layout (`errortools/` and `_errortools/`)

- **We chose:** a thin public re-export package in front of a private
  implementation package.
- **We gave up:** the ability to put public-facing helpers in the
  package whose name users import.
- **Why it is worth it:** it lets us refactor internals (rename
  `_errortools/ignore.py` → `_errortools/suppress.py`) without
  changing `import errortools` paths. The public shim's
  `__init__.py` is the single source of truth for `__all__` and the
  `__getattr__` deprecation machinery.

### 3.2 Pure-Python fallback for every C helper

- **We chose:** a `try: from _errortools._speedup …  except ImportError:
  def …` pattern in every module that uses a C helper.
- **We gave up:** a few extra lines of code in every importing module.
- **Why it is worth it:** a missing C build (mismatch Python, musl
  libc, sdist install) must not break `import errortools`. The
  fallback has identical observable behaviour, only slower.

### 3.3 Two-dep policy

- **We chose:** only `namebyauthor` and `typing_extensions`.
- **We gave up:** ergonomic niceties (pretty tracebacks, ANSI
  helpers, structured date parsing, etc.).
- **Why it is worth it:** every dependency we add is a version-pin
  every user must satisfy. Our job is exception handling, not
  terminal colouring. If you need a third-party dep, write a
  plugin (see [`_errortools/plugins.py`](_errortools/plugins.py)).

### 3.4 Python 3.8 minimum

- **We chose:** `requires-python = ">=3.8"` (see
  [`pyproject.toml`](pyproject.toml)).
- **We gave up:** `match` statements, PEP 604 union syntax in
  runtime code, `typing.Self`, and the cleaner `datetime.UTC`.
- **Why it is worth it:** the broader the supported floor, the more
  users can adopt us without a virtualenv dance. The cost is
  `Union[X, Y]` in annotations and explicit
  `if sys.version_info <= (3, 10):` blocks for `TypeAlias`.

### 3.5 Context-bundled metadata (`ErrorIgnoreWrapper`)

- **We chose:** a context manager that captures `name`, `count`,
  `exception`, and `traceback` on the way out.
- **We gave up:** zero-overhead suppression. The metadata
  collection calls `traceback.format_exception`, which is not free.
- **Why it is worth it:** most users do not measure their exception
  handler overhead, and they almost always want the traceback later.
  The `super_fast_*` family in
  [`_errortools/future.py`](_errortools/future.py) covers the
  measured-and-cares case.

### 3.6 `super_fast_*` is intentionally minimal

- **We chose:** no `repr`, no `__enter__` value, no `__exit__`
  parameters beyond the required ones, no `super().__init__()`
  chain.
- **We gave up:** the ability to print a meaningful `repr` in
  tracebacks.
- **Why it is worth it:** every `__dict__` lookup and method
  resolution step is overhead. The "no metadata, no allocation"
  promise is the *point*.

### 3.7 Custom error codes, not just `class MyError(Exception)`

- **We chose:** a three-layer hierarchy (`PureBaseException` →
  `ContextException` → `BaseErrorCodes`) with numeric `code`s.
- **We gave up:** the simplicity of just inheriting from `Exception`.
- **Why it is worth it:** the `code` lets a single handler route
  multiple error families. The `trace_id` and `with_context(**)`
  give observability for free. The cost is a one-time learning
  curve for the user.

### 3.8 Structured logger, not `logging.config.dictConfig`

- **We chose:** a `BaseLogger` whose API is loguru-shaped
  (`logger.add`, `logger.bind`, `logger.catch`).
- **We gave up:** interop with the standard `logging` ecosystem at
  import time. Users who need std-lib compatibility can add a
  `logging.Handler` adapter themselves.
- **Why it is worth it:** the loguru API is the de-facto standard
  for application-level structured logging. We do not want to
  re-educate the user; we want to give them a more focused
  implementation.

---

## 4. What we are **not**

This list is just as important as the principles.

- **We are not a logging framework.** `errortools.logging` is
  intentionally small (~460 lines) and lacks features that a
  general-purpose library would have: rotation by time, async sinks,
  structured JSON by default. Use `loguru` if you need those.
- **We are not an error-reporting service.** We do not phone home,
  we do not integrate with Sentry, we do not upload tracebacks. We
  give you the metadata; what you do with it is your business.
- **We are not a typing library.** We expose the type aliases we use
  internally (`ExceptionType`, `WarningType`, etc.) because they
  are useful, but we do not maintain a comprehensive
  `Annotated`-style exception-typing framework.
- **We are not a `monkeypatching_exception` toolkit.** We do not
  override `BaseException.__init__`, we do not install
  `sys.excepthook`, we do not wrap `raise` in a context manager.
  Each of those is a footgun in someone else's code.
- **We are not a benchmark suite.** `testing/benchmark/` is a
  smoke test for regressions, not a public leaderboard.

---

## 5. Public surface philosophy

The public API is a contract. Treat it as such.

### 5.1 What "public" means

- A name is public if it appears in `errortools.__all__`
  ([source](errortools/__init__.py)) or in the `__all__` of a
  submodule reachable from the top-level package
  (`errortools.future`, `errortools.logging`, `errortools.partial`).
- Everything in `_errortools/` is **not** public. The leading
  underscore is a load-bearing character, not a stylistic choice.
- "Public" does not mean "stable forever". It means "stable within
  the documented SemVer window".

### 5.2 What we guarantee

- **Within a major version:** no removal, no signature change, no
  type-hint narrowing that would break a correct caller.
- **Across patch versions:** no behaviour change for documented
  behaviour. Bug fixes that change edge cases get a ChangeLog
  bullet and a `versionchanged` directive.
- **Across minor versions:** new symbols, new optional parameters,
  new deprecations. No removals.
- **Across major versions:** we may break things. The deprecation
  pipeline is the runway.

### 5.3 What we do not guarantee

- The exact `__repr__` of any object (other than the documented
  `__str__` / format strings).
- The contents of `Record.extras`, `IgnoredError.traceback`, and
  other "for humans" attributes.
- The order of items in `LEVELS`, `list_all()`, etc. We sort
  internally but reserve the right to change the order.
- The fact that `errortools` and `_errortools` import paths resolve
  to the same files in CI and on a user machine. They will, but we
  do not promise that you can `import _errortools` from a third
  party.

---

## 6. Error-handling philosophy

This is the core of the project, so it gets its own section.

### 6.1 Exceptions are data, not control flow

- An exception object is a *value*. It carries information about
  what went wrong and where. Our
  [`ContextException`](_errortools/classes/errorcodes.py) family
  makes this explicit: `trace_id`, `context`, `with_cause(...)`.
- We do not recommend catching an exception to inspect it and
  re-raising as the same type. Use `with_cause` or `from` instead.

### 6.2 Suppression is a tool, not a default

- A `with ignore(SomeError):` block is a statement that *this site*
  has decided to recover from `SomeError`. It is not a free pass
  for unknown code.
- If you find yourself writing `ignore(Exception)`, stop and decide
  what you actually want. The standard library's
  `contextlib.suppress(Exception)` is fine for that case; we do not
  need to provide it.

### 6.3 Conversion is preservation

- `reraise(KeyError, ValueError)` and `@convert(KeyError, ValueError)`
  chain the original via `from`. The original traceback is never
  lost.
- Do not catch and `raise SomeOther(...)` without `from`. The
  traceback is the debugging story; you owe it to the next reader.

### 6.4 Retry is for *transient* failures

- `@retry` is for `ConnectionError`, `TimeoutError`, and other
  "this might work in a second" cases. It is **not** for
  `ValueError`, `KeyError`, or other "your input is wrong" cases —
  those will not get better on retry.
- `times` is the *retry* count, not the total attempt count. Total
  attempts = `times + 1`. We document this prominently in
  [`_errortools/decorator/retry.py`](_errortools/decorator/retry.py)
  because the alternative is a confusing `times=0` bug.

### 6.5 Warnings are for humans, not for control flow

- A `Warning` is a *suggestion* that something is unusual. The
  `BaseWarning` family exists so that a single
  `warnings.filterwarnings("error", category=PerformanceWarning)`
  can turn "this is slow" into a CI failure.
- We never use `Warning` for control flow. If a function needs to
  tell the caller "you might not want to do that", it returns a
  value, not a warning.

### 6.6 Logging is for ops, not for users

- `logger` is for events that have *operational* significance:
  "request received", "DB down", "deployment finished". It is not
  for "this branch was taken" (use a counter, not a log line).
- `logger.exception` is the right tool for "I am about to raise,
  here is the traceback". It does not swallow the exception.

---

## 7. Performance philosophy

- **Measure first.** Every optimization in the project has a
  benchmark to back it up. We do not optimize on intuition.
- **Optimize the hot path, not the warm path.** The
  `super_fast_*` family exists because we measured that the
  metadata-collection in `ignore()` was a bottleneck in real
  workloads. The same logic does not apply to e.g. `retry`, which
  is not a per-iteration primitive.
- **The default path is the readable path.** `ignore()` is the
  documented, Google-style, decorated, doctested default. It is
  not deprecated in favour of `super_fast_ignore`. Use whichever
  fits your measurement.
- **The C extension is optional.** If a user cannot build the C
  extension (sdist install, musl, s390x), the pure-Python fallback
  must give them the same observable behaviour. The performance
  goal is a bonus, not a requirement.

---

## 8. Documentation philosophy

- **The docstring is the API.** If the docstring says one thing and
  the code does another, the docstring wins (and the code is the
  bug).
- **The user guide is the textbook.** `docs/user_guide/` is read
  top-to-bottom by a new user. Order matters: install →
  exception-handling → decorators → logging → custom exceptions →
  future module.
- **The examples are tests.** Every `>>>` block in
  `docs/examples/` is also a doctest that runs in CI. If the
  example does not run, it does not ship.
- **The whatsnew is the changelog.** `docs/whatsnew/<X>_<Y>.md` is
  the human-readable counterpart of `ChangeLog.md`. The former
  explains the *why*; the latter lists the *what*.

---

## 9. Agent philosophy

This project welcomes AI agents as first-class contributors. We
treat them the same way we treat human contributors: with clear
expectations, no special pleading, and the same review bar.

- **Read the docs first.** `AGENTS_PREVIEW.md` is the
  orientation. `AGENTS_CHECK_LIST.md` is the gate. The
  `.agents/skills/` library is the playbook. The order is fixed.
- **Local verification is non-optional.** The §16 command list in
  `AGENTS_CHECK_LIST.md` must exit 0 on the agent's machine before
  the change ships. CI is the second opinion, not the first.
- **The public surface is sacred.** The `__all__` list,
  `_DEPRECATED_NAMES`, and the `__getattr__` whitelist are the
  agent's *only* legitimate places to touch the public shim.
  Everything else in `errortools/` is off-limits.
- **Cite your work.** Every claim in the final report should be
  backed by a file path, a function name, or a command. The
  reviewer is reading diffs, not vibes.

See [`.agents/README.md`](.agents/README.md) for the directory
layout and [`.agents/skills/README.md`](.agents/skills/README.md)
for the per-task playbooks.

---

## 10. Project lifecycle

A short note on what success looks like for `errortools`:

- **We win** when a new user writes `from errortools import ignore,
  retry, suppress` and is productive in under five minutes.
- **We win** when a maintainer can review a 200-line PR and ship
  it in under an hour because the contribution meets every item in
  `AGENTS_CHECK_LIST.md`.
- **We win** when the C extension is built, the pure-Python
  fallback works, the docs build, the tests pass, the lint is
  clean, and the public surface is intact — *all of the time*,
  not just on the maintainer's machine.

We do not need to be the most popular exception-handling library.
We need to be the one that does not surprise its users.

---

## 11. See also

- [`.agents/AGENTS_PREVIEW.md`](.agents/AGENTS_PREVIEW.md) — project
  snapshot for agents.
- [`.agents/AGENTS_CHECK_LIST.md`](.agents/AGENTS_CHECK_LIST.md) —
  pre-completion verification checklist.
- [`.agents/skills/`](.agents/skills/) — per-task playbooks.
- [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md) — human
  contributor guide.
- [`README.md`](README.md) — public-facing introduction.
- [`ChangeLog.md`](ChangeLog.md) — release-by-release history.

---

*This document is opinionated and slow-moving. Update it when the
project's *values* change, not when a particular decision changes.
If you find yourself editing `PHILOSOPHY.md` to justify a single
PR, write the justification in the PR description instead.*
