"""Tests for the interactive logger shell (_logger_shell)."""

import logging
import sys
from unittest.mock import MagicMock, patch

from _errortools.logging import BaseLogger, logger
from _errortools._logger_shell import (
    BANNER,
    EasterEgg,
    HistoryHook,
    TEMPLATE,
    build_banner,
    build_namespace,
    easteregg,
    start_shell,
)
from _errortools._logger_shell.prelude import easteregg as prelude_easteregg

# =============================================================================
# Namespace contents
# =============================================================================


class TestLoggerShellNamespace:
    def test_namespace_has_shortcuts(self):
        with patch("_errortools._logger_shell.code.interact") as mock_interact:
            start_shell()
            namespace = mock_interact.call_args.kwargs["local"]
            assert "info" in namespace
            assert "debug" in namespace
            assert "error" in namespace
            assert "warning" in namespace
            assert "critical" in namespace
            assert "trace" in namespace
            assert "success" in namespace
            assert "exception" in namespace
            assert "catch" in namespace

    def test_namespace_has_logger_types(self):
        with patch("_errortools._logger_shell.code.interact") as mock_interact:
            start_shell()
            namespace = mock_interact.call_args.kwargs["local"]
            assert "logger" in namespace
            assert "Level" in namespace
            assert "LEVELS" in namespace
            assert "BaseLogger" in namespace
            assert "Record" in namespace
            assert "StreamSink" in namespace
            assert "FileSink" in namespace
            assert "CallableSink" in namespace

    def test_namespace_has_stdlib_logging_base_classes(self):
        with patch("_errortools._logger_shell.code.interact") as mock_interact:
            start_shell()
            namespace = mock_interact.call_args.kwargs["local"]
            assert namespace["Logger"] is logging.Logger
            assert namespace["Handler"] is logging.Handler
            assert namespace["Filter"] is logging.Filter
            assert namespace["Formatter"] is logging.Formatter

    def test_shortcuts_delegate_to_logger(self):
        mock_logger = MagicMock(spec=BaseLogger)
        with patch("_errortools._logger_shell.logger", mock_logger):
            with patch("_errortools._logger_shell.code.interact") as mock_interact:
                start_shell()
                namespace = mock_interact.call_args.kwargs["local"]
                namespace["info"]("hello")
                mock_logger.info.assert_called_once_with("hello")
                namespace["debug"]("dbg")
                mock_logger.debug.assert_called_once_with("dbg")
                namespace["error"]("err")
                mock_logger.error.assert_called_once_with("err")

    def test_banner_non_empty(self):
        with patch("_errortools._logger_shell.code.interact") as mock_interact:
            start_shell()
            banner = mock_interact.call_args.kwargs["banner"]
            assert banner
            assert "Logger Shell" in banner


# =============================================================================
# build_namespace
# =============================================================================


class TestBuildNamespace:
    def test_returns_fresh_dict(self):
        a = build_namespace()
        b = build_namespace()
        assert a is not b
        a["custom"] = 1
        assert "custom" not in b

    def test_default_contents(self):
        ns = build_namespace()
        for name in (
            "logger",
            "info",
            "debug",
            "error",
            "warning",
            "critical",
            "trace",
            "success",
            "exception",
            "catch",
            "Level",
            "LEVELS",
            "BaseLogger",
            "Record",
            "StreamSink",
            "FileSink",
            "CallableSink",
            "Logger",
            "Handler",
            "Filter",
            "Formatter",
            "easteregg",
        ):
            assert name in ns

    def test_extra_does_not_overwrite(self):
        ns = build_namespace(extra={"logger": "shadowed", "extra_name": 42})
        assert ns["logger"] is not "shadowed"
        assert ns["extra_name"] == 42

    def test_start_shell_uses_build_namespace(self):
        with patch("_errortools._logger_shell.code.interact") as mock_interact:
            start_shell()
            namespace = mock_interact.call_args.kwargs["local"]
        assert "easteregg" in namespace
        assert namespace["easteregg"] is easteregg

    def test_start_shell_accepts_custom_namespace(self):
        custom = {"x": 42, "logger": "fake"}
        with patch("_errortools._logger_shell.code.interact") as mock_interact:
            start_shell(namespace=custom, install_history_hook=False)
            namespace = mock_interact.call_args.kwargs["local"]
        assert namespace["x"] == 42


# =============================================================================
# build_banner / BANNER / TEMPLATE
# =============================================================================


class TestBanner:
    def test_template_is_string(self):
        assert isinstance(TEMPLATE, str)
        assert "Logger Shell" in TEMPLATE
        assert "{sys" in TEMPLATE  # has at least one placeholder

    def test_build_banner_non_empty(self):
        b = build_banner()
        assert isinstance(b, str)
        assert len(b) > 100
        assert "Logger Shell" in b

    def test_build_banner_with_extra(self):
        b = build_banner(extra={"errortools_version": "9.9.9"})
        # The "extra" is *not* in TEMPLATE so the placeholder is left alone.
        # We only check that the function accepts it without raising.
        assert isinstance(b, str)

    def test_module_level_BANNER_matches(self):
        # The module-level BANNER is rendered at import time; it should
        # contain the same core text as a freshly-built one.
        assert "Logger Shell" in BANNER
        assert "Pre-imported shortcuts" in BANNER


# =============================================================================
# EasterEgg
# =============================================================================


class TestLoggerShellEasterEgg:
    def test_easteregg_repr(self):
        e = EasterEgg(logger)
        assert repr(e) == "You find me! Use easteregg() to see something..."

    # def test_easteregg_call_logs_info(self):
    #     mock_logger = MagicMock()
    #     with patch("_errortools._logger_shell.logger", mock_logger):
    #         easteregg()
    #     mock_logger.info.assert_called_once()

    def test_module_easteregg_is_singleton(self):
        assert easteregg is prelude_easteregg
        assert isinstance(easteregg, EasterEgg)


# =============================================================================
# HistoryHook
# =============================================================================


class TestHistoryHook:
    def setup_method(self):
        self._original_displayhook = sys.displayhook

    def teardown_method(self):
        sys.displayhook = self._original_displayhook

    def test_initial_state(self):
        hook = HistoryHook()
        assert hook.v1 is None
        assert hook.v2 is None
        assert hook.v3 is None
        # ``original_hook`` is always the *real* default displayhook,
        # never another ``HistoryHook`` wrapper.  This holds even when
        # ``sys.displayhook`` was previously set to a ``HistoryHook``
        # (e.g. by an earlier test that did not clean up).
        assert not isinstance(hook.original_hook, HistoryHook)

    def test_rotation(self):
        hook = HistoryHook()
        sentinel = object()
        hook(sentinel)
        assert hook.v1 is sentinel
        assert hook.v2 is None
        assert hook.v3 is None

        hook("second")
        assert hook.v1 == "second"
        assert hook.v2 is sentinel
        assert hook.v3 is None

        hook("third")
        assert hook.v1 == "third"
        assert hook.v2 == "second"
        assert hook.v3 is sentinel

    def test_skips_none_value(self):
        # CPython's default displayhook is a no-op for ``None``; the
        # ``HistoryHook`` should match that behaviour and leave the
        # rotation untouched.
        hook = HistoryHook()
        hook("first")
        hook(None)
        assert hook.v1 == "first"
        assert hook.v2 is None
        assert hook.v3 is None

    def test_walks_past_existing_historyhook(self):
        # If ``sys.displayhook`` is already a ``HistoryHook`` (e.g.
        # because a prior REPL session left it installed), a new
        # ``HistoryHook`` must still delegate to the real default
        # displayhook, not to the previous wrapper.
        #
        # Probe for the real default first; ``HistoryHook.__init__``
        # already walks past any pre-existing ``HistoryHook`` chain,
        # so this works even when ``sys.displayhook`` was polluted by
        # a previous test.
        real_default = HistoryHook().original_hook
        assert not isinstance(real_default, HistoryHook)

        # Pretend a previous REPL never restored ``sys.displayhook``.
        outer = HistoryHook()
        sys.displayhook = outer
        try:
            inner = HistoryHook()
            assert inner.original_hook is real_default
            assert inner.original_hook is not outer
        finally:
            sys.displayhook = self._original_displayhook

    def test_start_shell_installs_hook_by_default(self):
        original = sys.displayhook
        with patch("_errortools._logger_shell.code.interact"):
            start_shell()
        assert isinstance(sys.displayhook, HistoryHook)
        assert sys.displayhook is not original
        # restore for other tests
        sys.displayhook = original

    def test_start_shell_can_skip_history_hook(self):
        original = sys.displayhook
        with patch("_errortools._logger_shell.code.interact"):
            start_shell(install_history_hook=False)
        assert sys.displayhook is original


# =============================================================================
# Public exports
# =============================================================================


class TestPublicExports:
    def test_all_exports_present(self):
        import _errortools._logger_shell as mod

        for name in mod.__all__:
            assert hasattr(mod, name), f"Missing exported name: {name}"

    def test_known_set(self):
        import _errortools._logger_shell as mod

        assert set(mod.__all__) == {
            "BANNER",
            "EasterEgg",
            "HistoryHook",
            "TEMPLATE",
            "banner",
            "build_banner",
            "build_namespace",
            "easteregg",
            "start_shell",
        }
