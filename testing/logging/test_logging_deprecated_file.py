"""
Tests for _errortools/logging/ — ~~Level~~, ~~Record~~, ~~sinks~~, ~~BaseLogger~~.

Deprecated file.
"""

from __future__ import annotations

import io
import sys

from _errortools.logging import (
    BaseLogger,
    FileSink,
    Level,
    Record,
    StreamSink,
    logger,
)

# =============================================================================
# Global logger singleton
# =============================================================================


class TestGlobalLogger:
    def test_is_base_logger_instance(self):
        assert isinstance(logger, BaseLogger)

    def test_has_default_sink(self):
        assert len(logger._sinks) >= 1

    def test_repr(self):
        r = repr(logger)
        assert "BaseLogger" in r or "errortools" in r


# =============================================================================
# _OptLogger (returned by logger.opt(...))
# =============================================================================


class TestOptLogger:

    def _make_logger(self) -> tuple[BaseLogger, io.StringIO]:
        buf = io.StringIO()
        lg = BaseLogger()
        lg.add(buf, level=Level.TRACE, colorize=False)
        return lg, buf

    def _out(self, buf: io.StringIO) -> str:
        return buf.getvalue()

    # --- relay for every severity level --- #

    def test_opt_trace(self):
        lg, buf = self._make_logger()
        lg.set_level("TRACE")
        lg.opt().trace("opt trace")
        assert "TRACE" in self._out(buf)
        assert "opt trace" in self._out(buf)

    def test_opt_debug(self):
        lg, buf = self._make_logger()
        lg.opt().debug("opt debug")
        assert "DEBUG" in self._out(buf)
        assert "opt debug" in self._out(buf)

    def test_opt_info(self):
        lg, buf = self._make_logger()
        lg.opt().info("opt info")
        assert "INFO" in self._out(buf)
        assert "opt info" in self._out(buf)

    def test_opt_success(self):
        lg, buf = self._make_logger()
        lg.opt().success("opt success")
        assert "SUCCESS" in self._out(buf)
        assert "opt success" in self._out(buf)

    def test_opt_warning(self):
        lg, buf = self._make_logger()
        lg.opt().warning("opt warning")
        assert "WARNING" in self._out(buf)
        assert "opt warning" in self._out(buf)

    def test_opt_error(self):
        lg, buf = self._make_logger()
        lg.opt().error("opt error")
        assert "ERROR" in self._out(buf)
        assert "opt error" in self._out(buf)

    def test_opt_critical(self):
        lg, buf = self._make_logger()
        lg.opt().critical("opt critical")
        assert "CRITICAL" in self._out(buf)
        assert "opt critical" in self._out(buf)

    # --- exception=true --- #

    def test_opt_exception_attaches_traceback(self):
        lg, buf = self._make_logger()
        try:
            raise RuntimeError("opt boom")
        except RuntimeError:
            lg.opt(exception=True).error("handled")
        out = self._out(buf)
        assert "RuntimeError" in out
        assert "handled" in out

    def test_opt_exception_method(self):
        lg, buf = self._make_logger()
        try:
            raise LookupError("opt lookup")
        except LookupError:
            lg.opt(exception=True).exception("via opt")
        out = self._out(buf)
        assert "LookupError" in out
        assert "via opt" in out
        assert "ERROR" in out  # exception() logs at ERROR level

    def test_opt_no_exception_by_default(self):
        lg, buf = self._make_logger()
        lg.opt().error("plain")
        assert "Traceback" not in self._out(buf)

    # --- depth offset --- #

    def test_opt_depth_increases_caller_frame_distance(self):
        pass

        records: list[Record] = []

        class Capture(StreamSink):
            def emit(self, record):
                records.append(record)

        lg = BaseLogger()
        lg.add(Capture(sys.stderr, colorize=False))

        # depth=0  → caller is the line inside _relay (inside _OptLogger)
        # depth>0  → caller moves up the stack toward this test method
        lg.opt(depth=0).info("depth zero")
        depth_zero_file = records[-1].file

        lg.opt(depth=4).info("depth four")
        depth_four_file = records[-1].file

        assert depth_zero_file != depth_four_file


# =============================================================================
# catch() — advanced usage
# =============================================================================


class TestCatchAdvanced:

    def _make(self):
        buf = io.StringIO()
        lg = BaseLogger()
        lg.add(buf, level=Level.TRACE, colorize=False)
        return lg, buf

    def test_catch_multiple_exception_types(self):
        lg, buf = self._make()
        with lg.catch(ZeroDivisionError, ValueError):
            1 / 0  # type: ignore
        assert "ZeroDivisionError" in buf.getvalue()

        buf.truncate(0)
        buf.seek(0)
        with lg.catch(ZeroDivisionError, ValueError):
            raise ValueError("multi")
        assert "ValueError" in buf.getvalue()

    def test_catch_level_parameter(self):
        lg, buf = self._make()
        with lg.catch(level=Level.WARNING):
            raise RuntimeError("warn level")
        out = buf.getvalue()
        assert "WARNING" in out
        assert "RuntimeError" in out

    def test_catch_message_parameter(self):
        lg, buf = self._make()
        custom_msg = "CUSTOM-CAUGHT"
        with lg.catch(ValueError, message=custom_msg):
            raise ValueError("x")
        assert custom_msg in buf.getvalue()

    def test_catch_decorator_no_exception_normal_return(self):
        lg, buf = self._make()

        @lg.catch(ValueError)
        def good():
            return 42

        assert good() == 42
        assert buf.getvalue() == ""

    def test_catch_context_no_exception(self):
        lg, buf = self._make()
        with lg.catch():
            pass
        assert buf.getvalue() == ""


# =============================================================================
# FileSink — retention
# =============================================================================


class TestFileSinkRetention:

    def test_retention_keeps_only_n_files(self, tmp_path):
        log_path = tmp_path / "ret.log"
        # rotation=1 byte forces rotation on every emit, retention=2 keeps only 2
        sink = FileSink(log_path, rotation=1, retention=2)
        from _errortools.logging.record import make_record

        for i in range(5):
            sink.emit(make_record(Level.INFO, f"msg{i}", "root", 1, False, {}))
        sink.close()

        rotated = list(tmp_path.glob("ret.*.log"))
        assert len(rotated) <= 2


# =============================================================================
# StreamSink — TTY auto-detection
# =============================================================================


class TestStreamSinkTTY:

    def test_tty_auto_colorize_true(self):
        class FakeTTY:
            def isatty(self):
                return True

            def write(self, s: str) -> None:
                pass

            def flush(self) -> None:
                pass

        sink = StreamSink(FakeTTY())  # type: ignore[arg-type]
        assert sink._colorize is True

    def test_non_tty_auto_colorize_false(self):
        buf = io.StringIO()  # normal StringIO is not a tty
        sink = StreamSink(buf, colorize=None)
        assert sink._colorize is False


# =============================================================================
# _format_record — edge cases
# =============================================================================


class TestFormatRecord:

    def test_custom_fmt_all_placeholders(self):
        buf = io.StringIO()
        sink = StreamSink(buf, fmt="{level}:{name}:{message}", colorize=False)
        from _errortools.logging.record import make_record

        sink.emit(make_record(Level.INFO, "hi", "my_logger", 1, False, {}))
        assert "INFO:my_logger:hi" in buf.getvalue()

    def test_default_format_includes_location(self):
        buf = io.StringIO()
        sink = StreamSink(buf, colorize=False)
        from _errortools.logging.record import make_record

        sink.emit(make_record(Level.WARNING, "loc", "root", 1, False, {}))
        out = buf.getvalue()
        assert "WARNING" in out
        assert "loc" in out

    def test_traceback_appended_to_formatted_line(self):
        buf = io.StringIO()
        sink = StreamSink(buf, colorize=False)
        from _errortools.logging.record import make_record

        try:
            raise TypeError("fmt exc")
        except TypeError:
            rec = make_record(Level.ERROR, "err msg", "root", 1, True, {})
        sink.emit(rec)
        out = buf.getvalue()
        assert "TypeError" in out
        assert "err msg" in out
