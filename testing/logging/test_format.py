"""Logging tests for format log messages."""

import io

from _errortools.logging import (
    Level,
    StreamSink,
)

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
