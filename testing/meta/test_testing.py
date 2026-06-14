"""Tests for the testing package — version, constants, and run_tests."""

import testing
from testing import run_tests as run_tests_module


def test_version_is_string():
    assert isinstance(testing.__version__, str)


def test_version_tuple_matches_string():
    parts = tuple(int(x) for x in testing.__version__.split("."))
    assert parts == testing.__version_tuple__


def test_version_tuple_has_three_components():
    assert len(testing.__version_tuple__) == 3
    assert all(isinstance(x, int) for x in testing.__version_tuple__)


def test_has_pytest_is_true():
    assert testing.HAS_PYTEST is True


def test_no_one_change_version_is_false():
    assert testing.NO_ONE_CHANGE_VERSION is False


def test_all_exports():
    for name in testing.__all__:
        assert hasattr(testing, name)


def test_run_tests_function_exists():
    assert callable(run_tests_module.run_tests)


def test_run_tests_returns_false_without_pytest(monkeypatch):
    monkeypatch.setattr(run_tests_module, "HAS_PYTEST", False)
    result = run_tests_module.run_tests()
    assert result is False
