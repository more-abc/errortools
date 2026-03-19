from typing import NoReturn, TypeVar, Union

from _errortools.tools.error_msg import (
    IgnoreUseKeyboardInterruptErrorMessage as KeyboardInterruptMsg,
    IgnoreUseSystemExitErrorMessage as SystemExitMsg,
    IgnoreUseBaseExceptionErrorMessage as BaseExceptionMsg,
    IgnoreSubClassUseBaseExceptionErrorMessage as SubClassBaseExceptionMsg
)

if __name__ != "__main__":
    from ..ignore import ignore, ignore_subclass

Exceptiontype = TypeVar("Exceptiontype", bound=BaseException)

@ignore.register # type: ignore[misc]
def _(error_type: Union[type[KeyboardInterrupt], type[Exception]]) -> NoReturn:
    raise ValueError(KeyboardInterruptMsg)

@ignore.register # type: ignore[misc]
def _(error_type: Union[type[SystemExit], type[Exception]]) -> NoReturn:
    raise ValueError(SystemExitMsg)

@ignore.register  # type: ignore[misc]
def _(error_type: type[BaseException]) -> NoReturn:
    raise ValueError(BaseExceptionMsg)

@ignore_subclass.register  # type: ignore[misc]
def _(base_type: type[BaseException]) -> NoReturn:
    raise ValueError(SubClassBaseExceptionMsg)