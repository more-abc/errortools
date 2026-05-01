"""Tests for _errortools/classes/group.py — GroupErrors and BaseGroup."""

import sys

import pytest

from _errortools.classes.group import GroupErrors, BaseGroup
from . import HAS_PYTEST

if not HAS_PYTEST:
    print("pytest is required to run these tests, skip run test_groups.py")
    exit(0)

# =============================================================================
# GroupErrors — collect / raise_group / clear
# =============================================================================


if sys.version_info >= (3, 11):

    class TestGroupErrors:
        def test_starts_empty(self):
            g = GroupErrors()
            assert len(g) == 0
            assert not g

        def test_collect_adds_exception(self):
            g = GroupErrors()
            g.collect(ValueError("v"))
            assert len(g) == 1

        def test_collect_multiple(self):
            g = GroupErrors()
            g.collect(ValueError("v"))
            g.collect(TypeError("t"))
            g.collect(KeyError("k"))
            assert len(g) == 3

        def test_bool_true_when_not_empty(self):
            g = GroupErrors()
            g.collect(RuntimeError("r"))
            assert bool(g) is True

        def test_bool_false_when_empty(self):
            assert bool(GroupErrors()) is False

        def test_errors_returns_copy(self):
            g = GroupErrors()
            e = ValueError("v")
            g.collect(e)
            snapshot = g.errors
            snapshot.clear()  # mutating the copy must not affect the group
            assert len(g) == 1

        def test_raise_group_raises_exception_group(self):
            g = GroupErrors()
            g.collect(ValueError("v"))
            g.collect(TypeError("t"))
            with pytest.raises(ExceptionGroup) as exc_info:
                g.raise_group()
            assert len(exc_info.value.exceptions) == 2

        def test_raise_group_uses_group_msg(self):
            g = GroupErrors("my errors")
            g.collect(ValueError("v"))
            with pytest.raises(ExceptionGroup) as exc_info:
                g.raise_group()
            assert exc_info.value.message == "my errors"

        def test_raise_group_default_msg(self):
            g = GroupErrors()
            g.collect(ValueError("v"))
            with pytest.raises(ExceptionGroup) as exc_info:
                g.raise_group()
            assert exc_info.value.message == "multiple errors"

        def test_raise_group_does_nothing_when_empty(self):
            g = GroupErrors()
            g.raise_group()  # should not raise

        def test_clear_removes_all_exceptions(self):
            g = GroupErrors()
            g.collect(ValueError("v"))
            g.collect(TypeError("t"))
            g.clear()
            assert len(g) == 0

        def test_clear_then_raise_group_noop(self):
            g = GroupErrors()
            g.collect(ValueError("v"))
            g.clear()
            g.raise_group()  # no raise — nothing collected

        def test_repr_contains_msg_and_count(self):
            g = GroupErrors("test group")
            g.collect(ValueError("v"))
            r = repr(g)
            assert "GroupErrors" in r
            assert "test group" in r

        def test_sub_exception_types_preserved(self):
            g = GroupErrors()
            v = ValueError("val")
            t = TypeError("type")
            g.collect(v)
            g.collect(t)
            with pytest.raises(ExceptionGroup) as exc_info:
                g.raise_group()
            exc_types = {type(e) for e in exc_info.value.exceptions}
            assert exc_types == {ValueError, TypeError}


# =============================================================================
# BaseGroup — abstract interface
# =============================================================================


class TestBaseGroupAbstract:
    def test_base_group_has_abstract_methods(self):
        abstract = BaseGroup.__abstractmethods__
        assert "errors" in abstract
        assert "collect" in abstract
        assert "clear" in abstract
        assert "raise_group" in abstract

    def test_concrete_subclass_is_valid(self):
        g = GroupErrors()
        assert isinstance(g, BaseGroup)

    def test_group_errors_satisfies_abstract_interface(self):
        abstract = BaseGroup.__abstractmethods__
        for method in abstract:
            assert hasattr(GroupErrors, method), f"GroupErrors missing: {method}"
