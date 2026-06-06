"""Logging tests for sink."""

import datetime
import io
import os
from pathlib import Path
import sys
import threading

import pytest

from _errortools.logging.base import BaseLogger
from _errortools.logging.level import Level
from _errortools.logging.sink import CallableSink, FileSink, StreamSink

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
