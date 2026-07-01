from __future__ import annotations

import importlib.util
import os
import sys
from unittest.mock import MagicMock


from errortools_speedbelt.support_c_ext import (
    ERRORTOOLS_SUPPORTS_C_EXTENSIONS,
    _detect_c_ext_support,
    _has_c_compiler,
    _has_ctypes,
    _is_windows_store_python,
    _looks_like_static_analysis_run,
)


class TestIsWindowsStorePython:
    def test_windows_store_python_suffix(self, monkeypatch):
        monkeypatch.setattr(
            sys, "executable", r"C:\Users\foo\AppData\Local\Microsoft\WindowsApps\python.exe"
        )
        assert _is_windows_store_python() is True

    def test_case_insensitive_suffix(self, monkeypatch):
        monkeypatch.setattr(
            sys, "executable", r"C:\Users\foo\WindowsApps\PYTHON.EXE"
        )
        assert _is_windows_store_python() is True

    def test_regular_python_executable(self, monkeypatch):
        monkeypatch.setattr(sys, "executable", r"C:\Python312\python.exe")
        assert _is_windows_store_python() is False

    def test_unix_python_executable(self, monkeypatch):
        monkeypatch.setattr(sys, "executable", "/usr/bin/python3")
        assert _is_windows_store_python() is False


class TestHasCtypes:
    def test_when_ctypes_present(self, monkeypatch):
        monkeypatch.setattr(
            importlib.util, "find_spec", lambda name: MagicMock() if name == "ctypes" else None
        )
        assert _has_ctypes() is True

    def test_when_ctypes_missing(self, monkeypatch):
        original_find_spec = importlib.util.find_spec

        def no_ctypes(name):
            if name == "ctypes":
                return None
            return original_find_spec(name)

        monkeypatch.setattr(importlib.util, "find_spec", no_ctypes)
        assert _has_ctypes() is False


class TestLooksLikeStaticAnalysisRun:
    def test_mypy_in_argv(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["python", "-m", "mypy", "src"])
        assert _looks_like_static_analysis_run() is True

    def test_pyright_in_argv(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["pyright", "--project", "."])
        assert _looks_like_static_analysis_run() is True

    def test_pylance_in_argv(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["Pylance", "--stdio"])
        assert _looks_like_static_analysis_run() is True

    def test_pylsp_in_argv(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["pylsp", "-v"])
        assert _looks_like_static_analysis_run() is True

    def test_regular_execution(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["python", "script.py"])
        assert _looks_like_static_analysis_run() is False

    def test_no_tty_and_env_marker(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["python"])
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = False
        monkeypatch.setattr(sys, "stdin", mock_stdin)
        monkeypatch.setenv("PYRIGHT_LANGSERVER", "1")
        assert _looks_like_static_analysis_run() is False

    def test_tty_no_env_marker(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["python"])
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = True
        monkeypatch.setattr(sys, "stdin", mock_stdin)
        assert _looks_like_static_analysis_run() is False

    def test_no_tty_without_env_marker(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["python"])
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = False
        monkeypatch.setattr(sys, "stdin", mock_stdin)
        for key in list(os.environ):
            if key.lower() in ("mypy", "pyright", "pylsp", "pylance"):
                monkeypatch.delenv(key, raising=False)
        assert _looks_like_static_analysis_run() is False


class TestHasCCompiler:
    def test_gcc_on_path(self, monkeypatch):
        monkeypatch.setattr(
            "errortools_speedbelt.support_c_ext.which",
            lambda cmd: "/usr/bin/gcc" if cmd == "gcc" else None,
        )
        assert _has_c_compiler() is True

    def test_clang_on_path(self, monkeypatch):
        monkeypatch.setattr(
            "errortools_speedbelt.support_c_ext.which",
            lambda cmd: "/usr/bin/clang" if cmd == "clang" else None,
        )
        assert _has_c_compiler() is True

    def test_cl_exe_on_path(self, monkeypatch):
        monkeypatch.setattr(
            "errortools_speedbelt.support_c_ext.which",
            lambda cmd: r"C:\MSVC\bin\cl.exe" if cmd == "cl.exe" else None,
        )
        assert _has_c_compiler() is True

    def test_cc_on_path(self, monkeypatch):
        monkeypatch.setattr(
            "errortools_speedbelt.support_c_ext.which",
            lambda cmd: "/usr/bin/cc" if cmd == "cc" else None,
        )
        assert _has_c_compiler() is True

    def test_no_compiler_on_path(self, monkeypatch):
        monkeypatch.setattr(
            "errortools_speedbelt.support_c_ext.which", lambda _: None
        )
        assert _has_c_compiler() is False

    def test_which_raises_oserror(self, monkeypatch):
        def raising_which(_):
            raise OSError("bad PATH")

        monkeypatch.setattr(
            "errortools_speedbelt.support_c_ext.which", raising_which
        )
        assert _has_c_compiler() is False

    def test_which_raises_valueerror(self, monkeypatch):
        def raising_which(_):
            raise ValueError("bad PATHEXT")

        monkeypatch.setattr(
            "errortools_speedbelt.support_c_ext.which", raising_which
        )
        assert _has_c_compiler() is False

    def test_first_compiler_found_short_circuits(self, monkeypatch):
        calls = []

        def tracking_which(cmd):
            calls.append(cmd)
            if cmd == "gcc":
                return "/usr/bin/gcc"
            return None

        monkeypatch.setattr(
            "errortools_speedbelt.support_c_ext.which", tracking_which
        )
        assert _has_c_compiler() is True
        assert calls == ["gcc"]


class TestDetectCExtSupport:
    def test_all_good_returns_true(self, monkeypatch):
        monkeypatch.setattr(sys, "executable", "/usr/bin/python3")
        monkeypatch.setattr(sys, "argv", ["python", "script.py"])
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = True
        monkeypatch.setattr(sys, "stdin", mock_stdin)
        monkeypatch.setattr(
            importlib.util, "find_spec", lambda name: MagicMock() if name == "ctypes" else None
        )
        monkeypatch.setattr(
            "errortools_speedbelt.support_c_ext.which",
            lambda cmd: "/usr/bin/gcc" if cmd == "gcc" else None,
        )
        assert _detect_c_ext_support() is True

    def test_windows_store_short_circuits_false(self, monkeypatch):
        monkeypatch.setattr(
            sys, "executable", r"C:\Users\foo\WindowsApps\python.exe"
        )
        assert _detect_c_ext_support() is False

    def test_missing_ctypes_short_circuits_false(self, monkeypatch):
        monkeypatch.setattr(sys, "executable", "/usr/bin/python3")
        original_find_spec = importlib.util.find_spec

        def no_ctypes(name):
            if name == "ctypes":
                return None
            return original_find_spec(name)

        monkeypatch.setattr(importlib.util, "find_spec", no_ctypes)
        assert _detect_c_ext_support() is False

    def test_static_analysis_short_circuits_false(self, monkeypatch):
        monkeypatch.setattr(sys, "executable", "/usr/bin/python3")
        monkeypatch.setattr(sys, "argv", ["python", "-m", "mypy", "src"])
        assert _detect_c_ext_support() is False

    def test_no_compiler_short_circuits_false(self, monkeypatch):
        monkeypatch.setattr(sys, "executable", "/usr/bin/python3")
        monkeypatch.setattr(sys, "argv", ["python", "script.py"])
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = True
        monkeypatch.setattr(sys, "stdin", mock_stdin)
        monkeypatch.setattr(
            importlib.util, "find_spec", lambda name: MagicMock() if name == "ctypes" else None
        )
        monkeypatch.setattr(
            "errortools_speedbelt.support_c_ext.which", lambda cmd: None
        )
        assert _detect_c_ext_support() is False


class TestErrortoolsSupportsCExtensions:
    def test_is_bool(self):
        assert isinstance(ERRORTOOLS_SUPPORTS_C_EXTENSIONS, bool)

    def test_value_matches_detect(self):
        assert ERRORTOOLS_SUPPORTS_C_EXTENSIONS == _detect_c_ext_support()
