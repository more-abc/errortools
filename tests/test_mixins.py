"""Tests for _errortools/methods/ — attribute error mixin classes.

Covers:
  - ErrorAttrMixin       (__getattr__ → __errorattr__)
  - ErrorAttrDeletionMixin (__delattr__ → __errordelattr__)
  - ErrorAttrCheckMixin  (__errorhasattr__)
  - ErrorSetAttrMixin    (__setattr__ → __errorsetattr__)
  - ErrorAttrable ABC    (registration and subclasshook)
"""

import pytest

from _errortools.methods.errorattr import ErrorAttrMixin
from _errortools.methods.errordelattr import ErrorAttrDeletionMixin
from _errortools.methods.errorhasattr import ErrorAttrCheckMixin
from _errortools.methods.errorsetattr import ErrorSetAttrMixin

# NOTE: To maintain compatibility, I won't
# move its test code to a separate file for now.
from _errortools.classes.abc import ErrorAttrable

# =============================================================================
# ErrorAttrMixin
# =============================================================================


class TestErrorAttrMixin:
    def test_access_missing_attr_raises_attribute_error(self):
        class Obj(ErrorAttrMixin):
            pass

        obj = Obj()
        with pytest.raises(AttributeError, match="does not exist"):
            _ = obj.nonexistent

    def test_access_missing_attr_message_contains_class_name(self):
        class MyClass(ErrorAttrMixin):
            pass

        obj = MyClass()
        with pytest.raises(AttributeError, match="MyClass"):
            _ = obj.missing

    def test_access_existing_attr_works(self):
        class Obj(ErrorAttrMixin):
            x = 42

        obj = Obj()
        assert obj.x == 42

    def test_custom_errorattr_override(self):
        class Custom(ErrorAttrMixin):
            def __errorattr__(self, name):  # type: ignore
                return f"custom:{name}"

        obj = Custom()
        assert obj.whatever == "custom:whatever"

    def test_instance_attr_access_works(self):
        class Obj(ErrorAttrMixin):
            pass

        obj = Obj()
        obj.value = 99  # type: ignore # set an instance attribute
        assert obj.value == 99


# =============================================================================
# ErrorAttrDeletionMixin
# =============================================================================


class TestErrorAttrDeletionMixin:
    def test_delete_existing_attr_works(self):
        class Obj(ErrorAttrDeletionMixin):
            pass

        obj = Obj()
        obj.x = 1  # type: ignore
        del obj.x  # should succeed
        assert not hasattr(obj, "x")

    def test_delete_missing_attr_raises_attribute_error(self):
        class Obj(ErrorAttrDeletionMixin):
            pass

        obj = Obj()
        with pytest.raises(AttributeError, match="Cannot delete"):
            del obj.nonexistent

    def test_delete_missing_attr_message_contains_class_name(self):
        class MyClass(ErrorAttrDeletionMixin):
            pass

        obj = MyClass()
        with pytest.raises(AttributeError, match="MyClass"):
            del obj.missing

    def test_custom_errordelattr_override(self):
        deleted = []

        class Custom(ErrorAttrDeletionMixin):
            def __errordelattr__(self, name):  # type: ignore
                deleted.append(name)

        obj = Custom()
        del obj.ghost  # triggers custom handler
        assert "ghost" in deleted


# =============================================================================
# ErrorAttrCheckMixin
# =============================================================================


class TestErrorAttrCheckMixin:
    def test_existing_attr_returns_true(self):
        class Obj(ErrorAttrCheckMixin):
            x = 10

        obj = Obj()
        result = obj.__errorhasattr__("x")
        assert result == {"x": True}

    def test_missing_attr_returns_false(self):
        class Obj(ErrorAttrCheckMixin):
            pass

        obj = Obj()
        result = obj.__errorhasattr__("nonexistent")
        assert result == {"nonexistent": False}

    def test_mixed_attrs(self):
        class Obj(ErrorAttrCheckMixin):
            a = 1

        obj = Obj()
        result = obj.__errorhasattr__("a", "b")
        assert result == {"a": True, "b": False}

    def test_no_args_raises_value_error(self):
        class Obj(ErrorAttrCheckMixin):
            pass

        obj = Obj()
        with pytest.raises(ValueError):
            obj.__errorhasattr__()

    def test_multiple_existing_attrs(self):
        class Obj(ErrorAttrCheckMixin):
            pass

        obj = Obj()
        obj.p = 1  # type: ignore
        obj.q = 2  # type: ignore
        result = obj.__errorhasattr__("p", "q")
        assert result == {"p": True, "q": True}


# =============================================================================
# ErrorSetAttrMixin
# =============================================================================


class TestErrorSetAttrMixin:
    def test_normal_assignment_works(self):
        class Obj(ErrorSetAttrMixin):
            _forbidden_attrs: list = []

        obj = Obj()
        obj.value = 42
        assert obj.value == 42  # type: ignore

    def test_forbidden_attr_raises_attribute_error(self):
        class Obj(ErrorSetAttrMixin):
            _forbidden_attrs = ["locked"]

        obj = Obj()
        with pytest.raises(AttributeError, match="Cannot assign"):
            obj.locked = 99

    def test_forbidden_attr_message_contains_attr_name(self):
        class Obj(ErrorSetAttrMixin):
            _forbidden_attrs = ["secret"]

        obj = Obj()
        with pytest.raises(AttributeError, match="secret"):
            obj.secret = "leak"

    def test_allowed_attr_not_blocked(self):
        class Obj(ErrorSetAttrMixin):
            _forbidden_attrs = ["locked"]

        obj = Obj()
        obj.allowed = "ok"  # should not raise
        assert obj.allowed == "ok"  # type: ignore

    def test_custom_errorsetattr_override(self):
        blocked = []

        class Custom(ErrorSetAttrMixin):
            _forbidden_attrs = ["x"]

            def __errorsetattr__(self, name, value):  # type: ignore
                blocked.append((name, value))

        obj = Custom()
        obj.x = 123
        assert ("x", 123) in blocked


# =============================================================================
# ErrorAttrable ABC
# =============================================================================


class TestErrorAttrableABC:
    def test_mixin_classes_registered(self):
        """All four mixin classes should be virtual subclasses."""
        assert issubclass(ErrorAttrMixin, ErrorAttrable)
        assert issubclass(ErrorAttrDeletionMixin, ErrorAttrable)
        assert issubclass(ErrorAttrCheckMixin, ErrorAttrable)
        assert issubclass(ErrorSetAttrMixin, ErrorAttrable)

    def test_subclasshook_recognises_errorattr(self):
        """Any class with __errorattr__ is recognised as ErrorAttrable."""

        class HasErrorAttr:
            def __errorattr__(self, name):
                raise AttributeError(name)

        assert issubclass(HasErrorAttr, ErrorAttrable)

    def test_subclasshook_rejects_without_errorattr(self):
        """Classes without __errorattr__ are NOT ErrorAttrable."""

        class NoErrorAttr:
            pass

        assert not issubclass(NoErrorAttr, ErrorAttrable)

    def test_cannot_instantiate_abstract_base(self):
        """ErrorAttrable is abstract and cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ErrorAttrable()  # type: ignore

    def test_concrete_implementation(self):
        """A concrete subclass that implements __errorattr__ can be instantiated."""

        class Concrete(ErrorAttrable):
            def __errorattr__(self, name):
                raise AttributeError(f"no attr: {name}")

        obj = Concrete()
        with pytest.raises(AttributeError, match="no attr: foo"):
            _ = obj.foo
