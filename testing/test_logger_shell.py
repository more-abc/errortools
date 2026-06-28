"""Tests for the interactive logger shell (_logger_shell)."""

import logging
from unittest.mock import MagicMock, patch

from _errortools.logging import BaseLogger
from _errortools._logger_shell import start_shell, EasterEgg

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


class TestLoggerShellEasterEgg:
    def test_easteregg_repr(self):
        e = EasterEgg()
        assert repr(e) == "You find me! Use easteregg() to see something..."
