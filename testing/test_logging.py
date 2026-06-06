"""Tests for _errortools/logging/ — Level, Record, sinks, BaseLogger."""

from __future__ import annotations

import datetime
import io
import os
import sys
import threading
from pathlib import Path

import pytest

from _errortools.logging import (
    BaseLogger,
    CallableSink,
    FileSink,
    Level,
    Record,
    StreamSink,
    get_level,
    logger,
    LEVELS,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_logger(*args, **kwargs) -> tuple[BaseLogger, io.StringIO]:
    buf = io.StringIO()
    lg = BaseLogger(*args, **kwargs)
    lg.add(buf, level=Level.TRACE, colorize=False)
    return lg, buf


# =============================================================================
# Level
# =============================================================================


class TestLevel:
    def test_predefined_levels_exist(self):
        for attr in (
            "TRACE",
            "DEBUG",
            "INFO",
            "SUCCESS",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ):
            assert hasattr(Level, attr)

    def test_level_ordering(self):
        assert Level.TRACE < Level.DEBUG
        assert Level.DEBUG < Level.INFO
        assert Level.INFO < Level.SUCCESS
        assert Level.SUCCESS < Level.WARNING
        assert Level.WARNING < Level.ERROR
        assert Level.ERROR < Level.CRITICAL

    def test_level_comparison_operators(self):
        assert Level.DEBUG <= Level.DEBUG
        assert Level.ERROR >= Level.WARNING
        assert Level.INFO > Level.TRACE
        assert not Level.CRITICAL < Level.ERROR

    def test_level_str(self):
        assert str(Level.INFO) == "INFO"
        assert str(Level.CRITICAL) == "CRITICAL"

    def test_levels_tuple_ordered(self):
        nos = [lv.no for lv in LEVELS]
        assert nos == sorted(nos)

    def test_get_level_by_name(self):
        assert get_level("info") is Level.INFO
        assert get_level("DEBUG") is Level.DEBUG
        assert get_level("WARNING") is Level.WARNING

    def test_get_level_by_number(self):
        assert get_level(20) is Level.INFO
        assert get_level(50) is Level.CRITICAL

    def test_get_level_unknown_name_raises(self):
        with pytest.raises(KeyError):
            get_level("VERBOSE")

    def test_get_level_unknown_number_raises(self):
        with pytest.raises(KeyError):
            get_level(99)

    def test_level_has_color_and_icon(self):
        for lv in LEVELS:
            assert isinstance(lv.color, str) and lv.color
            assert isinstance(lv.icon, str) and lv.icon

    def test_level_frozen(self):
        with pytest.raises(Exception):
            Level.INFO.name = "CHANGED"  # type: ignore[misc]


# =============================================================================
# BaseLogger — level methods
# =============================================================================


class TestBaseLoggerLevelMethods:
    def setup_method(self):
        self.lg, self.buf = _make_logger()
        self.lg.set_level(Level.TRACE)

    def _out(self) -> str:
        return self.buf.getvalue()

    def test_trace(self):
        self.lg.trace("trace line")
        assert "TRACE" in self._out()
        assert "trace line" in self._out()

    def test_debug(self):
        self.lg.debug("debug line")
        out = self._out()
        assert "⚙ DEBUG" in out
        assert "debug line" in out

    def test_info(self):
        self.lg.info("info line")
        assert "INFO" in self._out()

    def test_success(self):
        self.lg.success("success line")
        assert "SUCCESS" in self._out()

    def test_warning(self):
        self.lg.warning("warning line")
        assert "WARNING" in self._out()

    def test_error(self):
        self.lg.error("error line")
        assert "ERROR" in self._out()

    def test_critical(self):
        self.lg.critical("critical line")
        assert "CRITICAL" in self._out()


# =============================================================================
# BaseLogger — message formatting
# =============================================================================


class TestMessageFormatting:
    def test_positional_placeholder(self):
        lg, buf = _make_logger()
        lg.info("hello {}", "world")
        assert "hello world" in buf.getvalue()

    def test_keyword_placeholder(self):
        lg, buf = _make_logger()
        lg.info("user={name}", name="alice")
        assert "user=alice" in buf.getvalue()

    def test_multiple_placeholders(self):
        lg, buf = _make_logger()
        lg.info("{} + {} = {}", 1, 2, 3)
        assert "1 + 2 = 3" in buf.getvalue()

    def test_format_spec(self):
        lg, buf = _make_logger()
        lg.info("{val:.2f}", val=3.14159)
        assert "3.14" in buf.getvalue()

    def test_no_placeholders_unchanged(self):
        lg, buf = _make_logger()
        lg.info("plain message")
        assert "plain message" in buf.getvalue()


# =============================================================================
# BaseLogger — level filtering
# =============================================================================


class TestLevelFiltering:
    def test_messages_below_logger_level_dropped(self):
        lg, buf = _make_logger()
        lg.set_level(Level.WARNING)
        lg.debug("should be dropped")
        assert "should be dropped" not in buf.getvalue()

    def test_messages_at_logger_level_emitted(self):
        lg, buf = _make_logger()
        lg.set_level(Level.WARNING)
        lg.warning("at threshold")
        assert "at threshold" in buf.getvalue()

    def test_messages_above_logger_level_emitted(self):
        lg, buf = _make_logger()
        lg.set_level(Level.WARNING)
        lg.error("above threshold")
        assert "above threshold" in buf.getvalue()

    def test_sink_level_filters_independently(self):
        lg = BaseLogger()
        buf = io.StringIO()
        lg.add(buf, level=Level.ERROR, colorize=False)
        lg.warning("should not reach sink")
        lg.error("should reach sink")
        out = buf.getvalue()
        assert "should not reach sink" not in out
        assert "should reach sink" in out

    def test_set_level_by_name(self):
        lg, buf = _make_logger()
        lg.set_level("ERROR")
        lg.warning("dropped")
        assert "dropped" not in buf.getvalue()

    def test_set_level_by_number(self):
        lg, buf = _make_logger()
        lg.set_level(40)  # ERROR
        lg.info("dropped")
        assert "dropped" not in buf.getvalue()

    def test_level_property(self):
        lg, _ = _make_logger()
        lg.set_level(Level.SUCCESS)
        assert lg.level is Level.SUCCESS


# =============================================================================
# BaseLogger — sink management
# =============================================================================


class TestSinkManagement:
    def test_add_returns_integer_id(self):
        lg = BaseLogger()
        sid = lg.add(io.StringIO(), colorize=False)
        assert isinstance(sid, int)

    def test_multiple_sinks_all_receive_records(self):
        lg = BaseLogger()
        b1, b2 = io.StringIO(), io.StringIO()
        lg.add(b1, colorize=False)
        lg.add(b2, colorize=False)
        lg.info("broadcast")
        assert "broadcast" in b1.getvalue()
        assert "broadcast" in b2.getvalue()

    def test_remove_by_id(self):
        lg = BaseLogger()
        buf = io.StringIO()
        sid = lg.add(buf, colorize=False)
        lg.remove(sid)
        lg.info("after remove")
        assert "after remove" not in buf.getvalue()

    def test_remove_all(self):
        lg = BaseLogger()
        b1, b2 = io.StringIO(), io.StringIO()
        lg.add(b1, colorize=False)
        lg.add(b2, colorize=False)
        lg.remove()
        lg.info("after remove all")
        assert "after remove all" not in b1.getvalue()
        assert "after remove all" not in b2.getvalue()

    def test_remove_nonexistent_id_no_error(self):
        lg = BaseLogger()
        lg.remove(999)  # should not raise

    def test_add_callable_sink(self):
        received = []
        lg = BaseLogger()
        lg.add(received.append)
        lg.info("callable")
        assert any("callable" in m for m in received)

    def test_add_invalid_sink_raises(self):
        lg = BaseLogger()
        with pytest.raises(TypeError):
            lg.add(42)  # type: ignore[arg-type]

    def test_ids_are_unique_and_incrementing(self):
        lg = BaseLogger()
        ids = [lg.add(io.StringIO(), colorize=False) for _ in range(5)]
        assert ids == sorted(set(ids))


# =============================================================================
# BaseLogger — bind()
# =============================================================================


class TestBind:
    def test_bind_returns_new_logger(self):
        lg, _ = _make_logger()
        child = lg.bind(user="alice")
        assert child is not lg

    def test_bind_does_not_mutate_parent(self):
        lg, _ = _make_logger()
        lg.bind(user="alice")
        assert "user" not in lg._extra

    def test_bound_extra_in_record(self):
        records: list[Record] = []
        lg = BaseLogger()
        lg.add(lambda _: None)  # dummy sink to satisfy dispatch

        # Use a real sink that captures the record object
        class CaptureSink(StreamSink):
            def emit(self, record: Record) -> None:
                records.append(record)

        from _errortools.logging.sink import BaseSink

        class RawCapture(BaseSink):
            def emit(self, r: Record) -> None:  # type: ignore
                records.append(r)

        lg2 = BaseLogger()

        lg2._sinks[0] = RawCapture()
        child = lg2.bind(request_id="xyz")
        child.info("check extra")
        assert records and records[-1].extra.get("request_id") == "xyz"

    def test_bind_inherits_sinks(self):
        buf = io.StringIO()
        lg = BaseLogger()
        lg.add(buf, colorize=False)
        child = lg.bind(env="test")
        child.info("from child")
        assert "from child" in buf.getvalue()

    def test_bind_stacking(self):
        records: list[Record] = []
        from _errortools.logging.sink import BaseSink as BS

        class Capture(BS):
            def emit(self, r: Record) -> None:  # type: ignore
                records.append(r)

        lg = BaseLogger()
        lg._sinks[0] = Capture()
        child = lg.bind(a=1).bind(b=2)
        child.info("stacked")
        assert records[-1].extra == {"a": 1, "b": 2}


# =============================================================================
# BaseLogger — exception capture
# =============================================================================


class TestExceptionCapture:
    def test_exception_method_captures_traceback(self):
        lg, buf = _make_logger()
        try:
            1 / 0  # type: ignore
        except ZeroDivisionError:
            lg.exception("math error")
        out = buf.getvalue()
        assert "ZeroDivisionError" in out
        assert "math error" in out

    def test_log_with_exception_true(self):
        lg, buf = _make_logger()
        try:
            raise ValueError("oops")
        except ValueError:
            lg.log(Level.ERROR, "caught", exception=True)
        assert "ValueError" in buf.getvalue()

    def test_opt_exception(self):
        lg, buf = _make_logger()
        try:
            raise RuntimeError("boom")
        except RuntimeError:
            lg.opt(exception=True).error("opt error")
        assert "RuntimeError" in buf.getvalue()

    def test_no_exception_when_flag_false(self):
        lg, buf = _make_logger()
        lg.error("plain error")
        out = buf.getvalue()
        # No traceback block
        assert "Traceback" not in out


# =============================================================================
# BaseLogger — catch()
# =============================================================================


class TestCatch:
    def test_catch_suppresses_and_logs_exception(self):
        lg, buf = _make_logger()
        with lg.catch(ZeroDivisionError):
            1 / 0  # type: ignore
        out = buf.getvalue()
        assert "ZeroDivisionError" in out

    def test_catch_default_catches_exception(self):
        lg, buf = _make_logger()
        with lg.catch():
            raise ValueError("default catch")
        assert "ValueError" in buf.getvalue()

    def test_catch_unrelated_exception_propagates(self):
        lg, buf = _make_logger()
        with pytest.raises(KeyError):
            with lg.catch(ValueError):
                raise KeyError("unrelated")

    def test_catch_reraise(self):
        lg, buf = _make_logger()
        with pytest.raises(ZeroDivisionError):
            with lg.catch(ZeroDivisionError, reraise=True):
                1 / 0  # type: ignore
        assert "ZeroDivisionError" in buf.getvalue()

    def test_catch_as_decorator(self):
        lg, buf = _make_logger()

        @lg.catch(ValueError)
        def bad():
            raise ValueError("decorated")

        bad()
        assert "ValueError" in buf.getvalue()

    def test_catch_decorator_reraise(self):
        lg, buf = _make_logger()

        @lg.catch(ValueError, reraise=True)
        def bad():
            raise ValueError("reraise decorated")

        with pytest.raises(ValueError):
            bad()

    def test_catch_no_exception_clean_exit(self):
        lg, buf = _make_logger()
        with lg.catch():
            pass
        assert buf.getvalue() == ""


# =============================================================================
# StreamSink
# =============================================================================


class TestStreamSink:
    def test_emits_to_stream(self):
        buf = io.StringIO()
        sink = StreamSink(buf, colorize=False)
        from _errortools.logging.record import make_record

        rec = make_record(Level.INFO, "test", "root", 1, False, {})
        sink.emit(rec)
        assert "test" in buf.getvalue()

    def test_level_filter(self):
        buf = io.StringIO()
        sink = StreamSink(buf, level=Level.ERROR, colorize=False)
        from _errortools.logging.record import make_record

        sink.emit(make_record(Level.WARNING, "dropped", "root", 1, False, {}))
        sink.emit(make_record(Level.ERROR, "kept", "root", 1, False, {}))
        out = buf.getvalue()
        assert "dropped" not in out
        assert "kept" in out

    def test_colorize_false_no_ansi(self):
        buf = io.StringIO()
        sink = StreamSink(buf, colorize=False)
        from _errortools.logging.record import make_record

        sink.emit(make_record(Level.INFO, "plain", "root", 1, False, {}))
        assert "\033[" not in buf.getvalue()

    def test_colorize_true_has_ansi(self):
        buf = io.StringIO()
        sink = StreamSink(buf, colorize=True)
        from _errortools.logging.record import make_record

        sink.emit(make_record(Level.INFO, "colored", "root", 1, False, {}))
        assert "\033[" in buf.getvalue()

    def test_custom_fmt(self):
        buf = io.StringIO()
        sink = StreamSink(buf, fmt="{level}::{message}", colorize=False)
        from _errortools.logging.record import make_record

        sink.emit(make_record(Level.INFO, "hello", "root", 1, False, {}))
        assert "INFO::hello" in buf.getvalue()

    def test_thread_safety(self):
        buf = io.StringIO()
        lg = BaseLogger()
        lg.add(buf, colorize=False)
        errors: list[Exception] = []

        def worker():
            try:
                for _ in range(50):
                    lg.info("threaded")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors


# =============================================================================
# FileSink
# =============================================================================


class TestFileSink:
    def test_writes_to_file(self, tmp_path):
        log_path = tmp_path / "test.log"
        lg = BaseLogger()
        lg.add(log_path)
        lg.info("file write")
        lg.remove()
        assert "file write" in log_path.read_text(encoding="utf-8")

    def test_appends_on_reopen(self, tmp_path):
        log_path = tmp_path / "app.log"
        for msg in ("first", "second"):
            lg = BaseLogger()
            lg.add(log_path)
            lg.info(msg)
            lg.remove()
        content = log_path.read_text(encoding="utf-8")
        assert "first" in content
        assert "second" in content

    def test_creates_parent_dirs(self, tmp_path):
        log_path = tmp_path / "a" / "b" / "c.log"
        sink = FileSink(log_path)
        from _errortools.logging.record import make_record

        sink.emit(make_record(Level.INFO, "deep", "root", 1, False, {}))
        sink.close()
        assert log_path.exists()

    def test_rotation_creates_new_file(self, tmp_path):
        log_path = tmp_path / "rot.log"
        sink = FileSink(log_path, rotation=1)  # 1 byte → rotate on every write
        from _errortools.logging.record import make_record

        for i in range(3):
            sink.emit(make_record(Level.INFO, f"msg{i}", "root", 1, False, {}))
        sink.close()
        rotated = list(tmp_path.glob("rot.*.log"))
        assert len(rotated) >= 1

    def test_level_filter(self, tmp_path):
        log_path = tmp_path / "filtered.log"
        lg = BaseLogger()
        lg.add(log_path, level=Level.ERROR)
        lg.warning("dropped")
        lg.error("kept")
        lg.remove()
        content = log_path.read_text(encoding="utf-8")
        assert "dropped" not in content
        assert "kept" in content

    def test_accepts_string_path(self, tmp_path):
        log_path = str(tmp_path / "str.log")
        sink = FileSink(log_path)
        from _errortools.logging.record import make_record

        sink.emit(make_record(Level.INFO, "string path", "root", 1, False, {}))
        sink.close()
        assert "string path" in Path(log_path).read_text(encoding="utf-8")


# =============================================================================
# CallableSink
# =============================================================================


class TestCallableSink:
    def test_calls_function_with_string(self):
        received = []
        sink = CallableSink(received.append)
        from _errortools.logging.record import make_record

        sink.emit(make_record(Level.INFO, "hello", "root", 1, False, {}))
        assert len(received) == 1
        assert "hello" in received[0]

    def test_level_filter(self):
        received = []
        sink = CallableSink(received.append, level=Level.ERROR)
        from _errortools.logging.record import make_record

        sink.emit(make_record(Level.WARNING, "dropped", "root", 1, False, {}))
        sink.emit(make_record(Level.ERROR, "kept", "root", 1, False, {}))
        assert len(received) == 1
        assert "kept" in received[0]

    def test_rejects_non_callable(self):
        with pytest.raises(TypeError):
            CallableSink(42)  # type: ignore[arg-type]


# =============================================================================
# Record
# =============================================================================


class TestRecord:
    def _make(self, msg="hello", level=Level.INFO) -> Record:
        from _errortools.logging.record import make_record

        return make_record(level, msg, "test_logger", 1, False, {"k": "v"})

    def test_fields_populated(self):
        rec = self._make()
        assert rec.message == "hello"
        assert rec.level is Level.INFO
        assert rec.name == "test_logger"
        assert rec.extra == {"k": "v"}
        assert rec.exception is None
        assert isinstance(rec.thread_id, int)
        assert isinstance(rec.process_id, int)

    def test_exc_text_none_when_no_exception(self):
        rec = self._make()
        assert rec.exc_text is None

    def test_exc_text_when_exception_present(self):
        from _errortools.logging.record import make_record

        try:
            raise ValueError("test exc")
        except ValueError:
            rec = make_record(Level.ERROR, "err", "root", 1, True, {})
        assert rec.exc_text is not None
        assert "ValueError" in rec.exc_text

    def test_str_returns_message(self):
        rec = self._make("my msg")
        assert str(rec) == "my msg"


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
        assert "ERROR" in out   # exception() logs at ERROR level

    def test_opt_no_exception_by_default(self):
        lg, buf = self._make_logger()
        lg.opt().error("plain")
        assert "Traceback" not in self._out(buf)

    # --- depth offset --- #

    def test_opt_depth_increases_caller_frame_distance(self):
        from _errortools.logging.record import make_record

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
# BaseLogger.log() — direct arbitrary-level dispatch
# =============================================================================


class TestLogMethod:

    def _make(self):
        buf = io.StringIO()
        lg = BaseLogger()
        lg.add(buf, level=Level.TRACE, colorize=False)
        return lg, buf

    def test_log_by_level_name(self):
        lg, buf = self._make()
        lg.log("info", "by name")
        assert "INFO" in buf.getvalue()
        assert "by name" in buf.getvalue()

    def test_log_by_level_number(self):
        lg, buf = self._make()
        lg.log(30, "by number")   # WARNING
        assert "WARNING" in buf.getvalue()

    def test_log_by_level_object(self):
        lg, buf = self._make()
        lg.log(Level.CRITICAL, "by obj")
        assert "CRITICAL" in buf.getvalue()

    def test_log_below_threshold_is_dropped(self):
        lg, buf = self._make()
        lg.set_level(Level.ERROR)
        lg.log(Level.DEBUG, "too quiet")
        assert "too quiet" not in buf.getvalue()

    def test_log_with_positional_args(self):
        lg, buf = self._make()
        lg.log(Level.INFO, "val={}", 42)
        assert "val=42" in buf.getvalue()

    def test_log_with_keyword_args(self):
        lg, buf = self._make()
        lg.log(Level.INFO, "x={x}", x="y")
        assert "x=y" in buf.getvalue()

    def test_log_with_exception_true(self):
        lg, buf = self._make()
        try:
            raise OSError("direct log exc")
        except OSError:
            lg.log(Level.ERROR, "caught", exception=True)
        out = buf.getvalue()
        assert "OSError" in out
        assert "caught" in out


# =============================================================================
# BaseLogger — sink error handling
# =============================================================================


class TestSinkErrorHandling:

    def test_broken_sink_swallowed(self):
        class BrokenSink(StreamSink):
            def emit(self, record):  # type: ignore[override]
                raise RuntimeError("boom")

        buf = io.StringIO()
        lg = BaseLogger()
        lg.add(BrokenSink(sys.stderr, colorize=False))
        lg.add(buf, colorize=False)
        lg.info("should survive")
        assert "should survive" in buf.getvalue()

    def test_multiple_broken_sinks_all_swallowed(self):
        class Broken(StreamSink):
            def emit(self, record):  # type: ignore[override]
                raise ValueError("x")

        buf = io.StringIO()
        lg = BaseLogger()
        lg.add(Broken(sys.stderr, colorize=False))
        lg.add(Broken(sys.stderr, colorize=False))
        lg.add(buf, colorize=False)
        lg.info("multi broken")
        assert "multi broken" in buf.getvalue()


# =============================================================================
# Record — completeness checks
# =============================================================================


class TestRecordCompleteness:

    def test_record_time_is_aware_datetime(self):
        from _errortools.logging.record import make_record

        rec = make_record(Level.INFO, "t", "root", 1, False, {})
        assert isinstance(rec.time, datetime.datetime)
        assert rec.time.tzinfo is not None

    def test_record_caller_info_populated(self):
        from _errortools.logging.record import make_record

        rec = make_record(Level.INFO, "m", "root", 1, False, {})
        assert rec.file  # non-empty string
        assert rec.line >= 1
        assert rec.function

    def test_record_thread_fields(self):
        from _errortools.logging.record import make_record

        rec = make_record(Level.INFO, "m", "root", 1, False, {})
        assert rec.thread_id == threading.current_thread().ident
        assert rec.thread_name == threading.current_thread().name

    def test_record_process_id(self):
        from _errortools.logging.record import make_record

        rec = make_record(Level.INFO, "m", "root", 1, False, {})
        assert rec.process_id == os.getpid()


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
# BaseLogger.__repr__
# =============================================================================


class TestRepr:

    def test_repr_shows_name_level_sink_count(self):
        lg = BaseLogger(name="test_repr")
        r = repr(lg)
        assert "BaseLogger" in r
        assert "test_repr" in r
        assert "DEBUG" in r
        assert "sinks=0" in r

    def test_repr_shows_sink_count_after_add(self):
        lg = BaseLogger()
        lg.add(io.StringIO(), colorize=False)
        r = repr(lg)
        assert "sinks=1" in r


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
