"""Logging tests for record."""

from _errortools.logging.level import Level
from _errortools.logging.record import Record


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
