"""Tests for _errortools/error_msg.py — ErrorMsg descriptor."""

import pytest

from _errortools.descriptor.errormsg import ErrorMsg

# =============================================================================
# ErrorMsg Descriptor
# =============================================================================


class TestErrorMsg:
    def test_returns_preset_message_when_accessed(self):
        """Accessing the attribute returns the predefined message."""

        class MyClass:
            msg = ErrorMsg("Read-only attribute")

        obj = MyClass()
        assert obj.msg == "Read-only attribute"
        assert MyClass.msg == "Read-only attribute"

    def test_modification_raises_attribute_error(self):
        """Attempting to modify the attribute raises AttributeError."""

        class MyClass:
            attr = ErrorMsg("Cannot modify")

        obj = MyClass()
        with pytest.raises(
            AttributeError, match="Modification of this attribute is not allowed!"
        ):
            obj.attr = "new value"

    def test_deletion_raises_attribute_error(self):
        """Attempting to delete the attribute raises AttributeError."""

        class MyClass:
            attr = ErrorMsg("Cannot delete")

        obj = MyClass()
        with pytest.raises(
            AttributeError, match="Deletion of this attribute is not allowed!"
        ):
            del obj.attr

    def test_multiple_instances_hold_own_messages(self):
        """Different instances have independent read-only messages."""

        class MyClass:
            info = ErrorMsg("Information only")
            warning = ErrorMsg("Warning only")

        obj = MyClass()
        assert obj.info == "Information only"
        assert obj.warning == "Warning only"

    def test_instance_and_class_access_return_same_message(self):
        """Access via class or instance yields the same message."""
        msg_text = "Consistent message"

        class MyClass:
            data = ErrorMsg(msg_text)

        assert MyClass.data == msg_text
        assert MyClass().data == msg_text
