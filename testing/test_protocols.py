"""Tests for exception related runtime-checkable Protocols."""

import sys

import pytest

from _errortools.classes.protocol import (
    ExceptionLike,
    SystemExitLike,
    StopIterationLike,
    OSErrorLike,
    AttributeErrorLike,
    NameErrorLike,
    ImportErrorLike,
    SyntaxErrorLike,
    BlockingIOErrorLike,
    UnicodeDecodeErrorLike,
    UnicodeEncodeErrorLike,
    UnicodeTranslateErrorLike,
    BaseExceptionGroupLike,
    ExceptionGroupLike,
    GroupErrorsLike,
)

# ------------------------------
# Helper Classes
# ------------------------------
class DummyGroupError:
    def __init__(self, group_msg: str) -> None:
        self.group_msg = group_msg
        self._errors = []

    @property
    def errors(self):
        return self._errors

    def clear(self) -> None:
        self._errors.clear()

    def raise_group(self) -> None:
        raise Exception(self.group_msg)

# ------------------------------
# Tests for ExceptionLike
# ------------------------------
def test_exception_like_isinstance_check():
    exc_val = ValueError("test value error")
    exc_base = BaseException("base exception")
    exc_generic = Exception("generic exception")

    assert isinstance(exc_val, ExceptionLike)
    assert isinstance(exc_base, ExceptionLike)
    assert isinstance(exc_generic, ExceptionLike)
    assert not isinstance(object(), ExceptionLike)


def test_exception_like_standard_attributes():
    exc = RuntimeError("attribute check")
    assert hasattr(exc, "args")
    assert hasattr(exc, "__cause__")
    assert hasattr(exc, "__context__")
    assert hasattr(exc, "__suppress_context__")
    assert hasattr(exc, "__traceback__")


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires Python 3.11+ for __notes__ and add_note")
def test_exception_like_notes_feature_py311_plus():
    exc = Exception()
    test_note = "custom exception note"
    exc.add_note(test_note)

    assert hasattr(exc, "__notes__")
    assert isinstance(exc.__notes__, list)
    assert exc.__notes__ == [test_note]

# ------------------------------
# Tests for SystemExitLike
# ------------------------------
def test_system_exit_like_protocol():
    exit_ok = SystemExit(0)
    exit_err = SystemExit(1)

    assert isinstance(exit_ok, SystemExitLike)
    assert isinstance(exit_err, SystemExitLike)
    assert hasattr(exit_ok, "code")
    assert exit_ok.code == 0
    assert exit_err.code == 1

# ------------------------------
# Tests for StopIterationLike
# ------------------------------
def test_stop_iteration_like_protocol():
    exc1 = StopIteration()
    exc2 = StopIteration(42)

    assert isinstance(exc1, StopIterationLike)
    assert isinstance(exc2, StopIterationLike)
    assert hasattr(exc1, "value")
    assert exc1.value is None
    assert exc2.value == 42

# ------------------------------
# Tests for OSErrorLike
# ------------------------------
def test_os_error_like_basic():
    exc = OSError(2, "No such file or directory", "test.txt")
    assert isinstance(exc, OSErrorLike)
    assert hasattr(exc, "errno")
    assert hasattr(exc, "strerror")
    assert hasattr(exc, "filename")
    assert hasattr(exc, "filename2")

    assert exc.errno == 2
    assert exc.strerror == "No such file or directory"
    assert exc.filename == "test.txt"


@pytest.mark.skipif(sys.platform != "win32", reason="Win32 only ")
def test_os_error_like_win32_extra_attr():
    exc = OSError(13, "Permission denied")
    assert hasattr(exc, "winerror")

# ------------------------------
# Tests for AttributeErrorLike (Python 3.10+)
# ------------------------------
@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10+")
def test_attribute_error_like():
    exc = AttributeError("missing attr", name="foo", obj=object())
    assert isinstance(exc, AttributeErrorLike)
    assert hasattr(exc, "name")
    assert hasattr(exc, "obj")
    assert exc.name == "foo"

# ------------------------------
# Tests for NameErrorLike (Python 3.10+)
# ------------------------------
@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10+")
def test_name_error_like():
    exc = NameError("name not found", name="bar")
    assert isinstance(exc, NameErrorLike)
    assert hasattr(exc, "name")
    assert exc.name == "bar"

# ------------------------------
# Tests for ImportErrorLike
# ------------------------------
def test_import_error_like():
    exc = ImportError("cannot import module", name="missing_mod", path="/usr/lib")
    assert isinstance(exc, ImportErrorLike)
    assert hasattr(exc, "name")
    assert hasattr(exc, "path")
    assert hasattr(exc, "msg")
    assert exc.name == "missing_mod"
    assert exc.path == "/usr/lib"


@pytest.mark.skipif(sys.version_info < (3, 12), reason="Requires Python 3.12+ for name_from")
def test_import_error_like_name_from_py312_plus():
    exc = ImportError("import failed")
    assert hasattr(exc, "name_from")

# ------------------------------
# Tests for SyntaxErrorLike
# ------------------------------
def test_syntax_error_like():
    exc = SyntaxError("invalid syntax", ("test.py", 10, 2, "bad code"))
    assert isinstance(exc, SyntaxErrorLike)
    assert hasattr(exc, "msg")
    assert hasattr(exc, "filename")
    assert hasattr(exc, "lineno")
    assert hasattr(exc, "offset")
    assert hasattr(exc, "text")
    assert hasattr(exc, "print_file_and_line")

    assert exc.msg == "invalid syntax"
    assert exc.filename == "test.py"
    assert exc.lineno == 10

# ------------------------------
# Tests for BlockingIOErrorLike
# ------------------------------
def test_blocking_io_error_like():
    exc = BlockingIOError(11, "Resource temporarily unavailable")
    exc.characters_written = 5
    assert isinstance(exc, BlockingIOErrorLike)
    assert hasattr(exc, "characters_written")
    assert exc.characters_written == 5

# ------------------------------
# Tests for Unicode Error Protocols
# ------------------------------
def test_unicode_decode_error_like():
    exc = UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid byte")
    assert isinstance(exc, UnicodeDecodeErrorLike)
    assert hasattr(exc, "encoding")
    assert hasattr(exc, "object")
    assert hasattr(exc, "start")
    assert hasattr(exc, "end")
    assert hasattr(exc, "reason")


def test_unicode_encode_error_like():
    exc = UnicodeEncodeError("ascii", "😀", 0, 1, "ordinal not in range")
    assert isinstance(exc, UnicodeEncodeErrorLike)


def test_unicode_translate_error_like():
    exc = UnicodeTranslateError("test str", 1, 2, "translate failed")
    assert isinstance(exc, UnicodeTranslateErrorLike)
    assert exc.encoding is None

# ------------------------------
# Tests for Exception Group Protocols (Python 3.11+)
# ------------------------------
@pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires Python 3.11+ for ExceptionGroup")
def test_base_exception_group_like():
    inner_exc = ValueError("inner error")
    group = BaseExceptionGroup("group msg", [inner_exc])
    assert isinstance(group, BaseExceptionGroupLike)
    assert hasattr(group, "message")
    assert hasattr(group, "exceptions")


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires Python 3.11+ for ExceptionGroup")
def test_exception_group_like():
    inner_exc = KeyError("missing key")
    group = ExceptionGroup("exception group", [inner_exc])
    assert isinstance(group, ExceptionGroupLike)
    assert isinstance(group, BaseExceptionGroupLike)

# ------------------------------
# Tests for GroupErrorsLike
# ------------------------------
def test_group_errors_like():
    dummy = DummyGroupError("group message")
    assert isinstance(dummy, GroupErrorsLike)
    assert hasattr(dummy, "errors")
    assert hasattr(dummy, "clear")
    assert hasattr(dummy, "raise_group")

    dummy._errors.append(Exception("test"))
    assert len(dummy.errors) == 1
    dummy.clear()
    assert len(dummy.errors) == 0

    with pytest.raises(Exception):
        dummy.raise_group()
