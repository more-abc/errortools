"""Logging tests for levels."""

import io

from _errortools.logging import LEVELS, BaseLogger, Level, get_level

import pytest

from testing.logging.helper import _make_logger

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
