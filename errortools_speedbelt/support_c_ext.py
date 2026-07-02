"""Detect whether the current Python environment can build and load
the C extension shipped with :mod:`errortools_speedbelt`.

The detection result is exposed as the boolean
:data:`ERRORTOOLS_SUPPORTS_C_EXTENSIONS`.  The detection runs **once**
at import time and is then cached on the module — every subsequent
read of the constant is a cheap attribute lookup.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from shutil import which
from typing import Final

# --- Tunables ---------------------------------------------------------------

#: The Windows Store / WindowsApps install of Python lives in a
#: read-only folder under ``%LOCALAPPDATA%\\Microsoft\\WindowsApps``.
#: That interpreter cannot run a compiler, so we always treat it as
#: "C extensions unsupported".
_WINDOWS_STORE_PYTHON_SUFFIX: Final[str] = "windowsapps\\python.exe"

#: Markers that indicate the process is a static-analysis or
#: language-server run.  When any of these are present in
#: :data:`sys.argv` (case-insensitive substring) — or in the
#: environment for non-interactive processes — we skip the C
#: extension build to keep the host editor responsive.
_STATIC_ANALYZER_MARKERS: Final[tuple[str, ...]] = (
    "mypy",  # Mypy driver
    "pyright",  # Pyright CLI / Pylance
    "pylsp",  # python-lsp-server
    "pylance",  # Pylance language server
)

#: Recognised C compiler executables, in the order they are
#: searched on :data:`PATH`.  ``cc`` is the POSIX-mandated default
#: and is checked last so platforms that already found a more
#: specific name do not pay for an extra ``which`` call.
_KNOWN_C_COMPILERS: Final[tuple[str, ...]] = (
    "gcc",
    "clang",
    "cl.exe",  # Microsoft Visual C++
    "cc",  # POSIX generic
)


# --- Detection helpers ------------------------------------------------------
#
# Each helper is a single, testable predicate.  Splitting the
# detection up this way makes the policy easy to read and even
# easier to unit-test in isolation.


def _is_windows_store_python() -> bool:
    # Return ``True`` when running on the read-only Windows Store Python.

    # The Store variant is installed under
    # ``%LOCALAPPDATA%\\Microsoft\\WindowsApps`` and has a read-only
    # filesystem, so no compiler invocation can succeed there.

    return sys.executable.lower().endswith(_WINDOWS_STORE_PYTHON_SUFFIX)


def _has_ctypes() -> bool:
    # Return ``True`` if :mod:`ctypes` is importable in this interpreter.

    # :mod:`ctypes` is part of the standard library on every
    # CPython / PyPy release we support, but stripped-down
    # embedded distributions occasionally drop it.  Without
    # :mod:`ctypes` the compiled ``.so`` / ``.pyd`` cannot be
    # loaded.

    return importlib.util.find_spec("ctypes") is not None


def _looks_like_static_analysis_run() -> bool:
    # Return ``True`` when the process looks like a type-checker
    # or language-server invocation.

    # Two heuristics are combined:

    # 1. A known static-analysis marker is present anywhere in
    #    :data:`sys.argv` (case-insensitive substring match).
    # 2. The process has no controlling TTY and one of the markers
    #    appears in the environment — this catches the common case
    #    where an editor launches its language server as a
    #    detached subprocess (so :data:`sys.stdin` is not a TTY)
    #    and exports the server name as an environment variable.

    argv_blob = " ".join(sys.argv).lower()
    if any(marker in argv_blob for marker in _STATIC_ANALYZER_MARKERS):
        return True
    if not sys.stdin.isatty():
        lowered_env = {k.lower() for k in os.environ}
        if any(marker in lowered_env for marker in _STATIC_ANALYZER_MARKERS):
            return True
    return False


def _has_c_compiler() -> bool:
    # Return ``True`` if a known C compiler is discoverable on ``PATH``.

    # :func:`shutil.which` can raise :class:`OSError` or
    # :class:`ValueError` on Windows in pathological
    # configurations (e.g. broken ``PATHEXT`` or an
    # undecodable ``PATH`` entry).  We treat any such failure
    # as "no compiler found" rather than crashing the
    # import-time detection.
    for compiler in _KNOWN_C_COMPILERS:
        try:
            if which(compiler) is not None:
                return True
        except (OSError, ValueError):
            # Skip this compiler and keep looking.  If none
            # of them are reachable we will fall through to
            # ``return False`` below.
            continue
    return False


def _detect_c_ext_support() -> bool:
    # Return ``True`` if the current Python environment can build
    # and load the :mod:`errortools_speedbelt._speedup` C extension.

    # The check is intentionally conservative: any single failure
    # short-circuits to ``False`` so that the rest of the package
    # falls back to the pure-Python implementation in
    # :mod:`_errortools.future`.

    # Returns:
    #     ``True`` only when *all* of the following hold:

    #     * the interpreter is **not** the Windows Store Python;
    #     * :mod:`ctypes` is importable;
    #     * the process does **not** look like a static-analysis
    #       or language-server run;
    #     * a C compiler is on ``PATH``.

    if _is_windows_store_python():
        return False
    if not _has_ctypes():
        return False
    if _looks_like_static_analysis_run():
        return False
    if not _has_c_compiler():
        return False
    return True


#: ``True`` if the running interpreter can compile and load the
#: :mod:`errortools_speedbelt._speedup` C extension, ``False``
#: otherwise.
#:
#: This is a *one-shot* evaluation that happens at import time:
#: it caches the result of :func:`_detect_c_ext_support` so that
#: the rest of the package can ask the simple question
#: ``ERRORTOOLS_SUPPORTS_C_EXTENSIONS`` without paying the
#: detection cost on every lookup.
#:
#: Downstream code should treat this as read-only — rebinding
#: the name (e.g. from a test) will not re-run the detection.
ERRORTOOLS_SUPPORTS_C_EXTENSIONS: Final[bool] = _detect_c_ext_support()
"""A constant that detect whether the current Python environment can build and load
the C extension shipped with :mod:`errortools_speedbelt`.

The companion module :mod:`errortools_speedbelt._speedup` is a small
C extension that speeds up the hot paths in
:mod:`_errortools.future`.  It can only be built and loaded on
interpreters that meet *all* of the following:

* Running on a real OS install of CPython — not the
  `Windows Store / WindowsApps
  <https://learn.microsoft.com/en-us/windows/python/faqs#why-am-i-getting-an-error-when-i-pip-install-a-package-on-the-windows-store-version-of-python>`_
  variant, where the filesystem is read-only and no compiler can run.
* :mod:`ctypes` is importable (the runtime loader for the compiled
  ``.so`` / ``.pyd`` artifact).
* The current process is *not* a static-analysis runner
  (Mypy / Pyright / Pylance / ``python-lsp-server``) or a
  language-server subprocess.  In those cases the overhead of
  building a C extension is not worth the modest speedup and
  would visibly slow the host editor.
* A C compiler is discoverable on ``PATH`` (``gcc``, ``clang``,
  the MSVC ``cl.exe``, or the POSIX-mandated ``cc``).
"""
