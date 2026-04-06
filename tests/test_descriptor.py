"""Tests for _errortools/descriptor — ErrorMsg/NonBlankErrorMsg descriptor."""

import pytest

from _errortools.descriptor.errormsg import ErrorMsg
from _errortools.descriptor.nonblankmsg import NonBlankErrorMsg

# =============================================================================
# ErrorMsg Descriptor
# =============================================================================


class TestErrorMsg:
    def test_returns_preset_message_when_accessed(self):

        class MyClass:
            msg = ErrorMsg("Read-only attribute")

        obj = MyClass()
        assert obj.msg == "Read-only attribute"
        assert MyClass.msg == "Read-only attribute"

    def test_modification_raises_attribute_error(self):

        class MyClass:
            attr = ErrorMsg("Cannot modify")

        obj = MyClass()
        with pytest.raises(
            AttributeError, match="Modification of this attribute is not allowed!"
        ):
            obj.attr = "new value"

    def test_deletion_raises_attribute_error(self):
        class MyClass:
            attr = ErrorMsg("Cannot delete")

        obj = MyClass()
        with pytest.raises(
            AttributeError, match="Deletion of this attribute is not allowed!"
        ):
            del obj.attr

    def test_multiple_instances_hold_own_messages(self):

        class MyClass:
            info = ErrorMsg("Information only")
            warning = ErrorMsg("Warning only")

        obj = MyClass()
        assert obj.info == "Information only"
        assert obj.warning == "Warning only"

    def test_instance_and_class_access_return_same_message(self):
        msg_text = "Consistent message"

        class MyClass:
            data = ErrorMsg(msg_text)

        assert MyClass.data == msg_text
        assert MyClass().data == msg_text


# =============================================================================
# NonBlankErrorMsg Descriptor
# =============================================================================


class TestNonBlankErrorMsg:
    def test_accepts_valid_non_blank_string(self):

        class MyClass:
            msg = NonBlankErrorMsg("Error message")

        obj = MyClass()
        obj.msg = "  Valid error message  "
        assert obj.msg == "Valid error message"

    def test_raises_value_error_for_blank_string(self):

        class MyClass:
            msg = NonBlankErrorMsg("Error message")

        obj = MyClass()
        with pytest.raises(
            ValueError,
            match="Error message can't be blank, must provide a valid error message",
        ):
            obj.msg = ""

        with pytest.raises(
            ValueError,
            match="Error message can't be blank, must provide a valid error message",
        ):
            obj.msg = "   "

        with pytest.raises(
            ValueError,
            match="Error message can't be blank, must provide a valid error message",
        ):
            obj.msg = "\t\n  \t"

    def test_raises_value_error_for_non_string_type(self):

        class MyClass:
            msg = NonBlankErrorMsg("Error message")

        obj = MyClass()
        with pytest.raises(ValueError, match="Error message must be a string type"):
            obj.msg = None

        with pytest.raises(ValueError, match="Error message must be a string type"):
            obj.msg = 123

        with pytest.raises(ValueError, match="Error message must be a string type"):
            obj.msg = []

    def test_strips_whitespace_from_valid_input(self):

        class MyClass:
            msg = NonBlankErrorMsg("Error message")

        obj = MyClass()
        obj.msg = "  Hello World  "
        assert obj.msg == "Hello World"
        assert obj.msg != "  Hello World  "

    def test_deletion_raises_attribute_error(self):

        class MyClass:
            msg = NonBlankErrorMsg("Error message")

        obj = MyClass()
        with pytest.raises(
            AttributeError, match="Deletion of this attribute is not allowed!"
        ):
            del obj.msg

    def test_multiple_instances_work_independently(self):

        class MyClass:
            error1 = NonBlankErrorMsg("First error")
            error2 = NonBlankErrorMsg("Second error")

        obj = MyClass()
        obj.error1 = "  Database connection failed  "
        obj.error2 = "  Invalid input parameter  "

        assert obj.error1 == "Database connection failed"
        assert obj.error2 == "Invalid input parameter"
