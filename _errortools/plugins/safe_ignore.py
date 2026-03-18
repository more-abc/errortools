from typing import NoReturn

from ..ignore import ignore, ignore_subclass
from ..tools.error_msg import (IgnoreUseKeyboardInterruptErrorMessage as KeyboardInterruptMsg,
                               IgnoreUseSystemExitErrorMessage as SystemExitMsg,
                               IgnoreUseBaseExceptionErrorMessage as BaseExceptionMsg,
                               IgnoreSubClassUseBaseExceptionErrorMessage as SubClassBaseExceptionMsg)

@ignore.register
def _(error: KeyboardInterrupt) -> NoReturn:
    raise ValueError(KeyboardInterruptMsg)

@ignore.register
def _(error: SystemExit) -> NoReturn:
    raise ValueError(SystemExitMsg)

@ignore.register
def _(error: BaseException) -> NoReturn:
    raise ValueError(BaseExceptionMsg)

@ignore_subclass.register
def _(base: BaseException) -> NoReturn:
    raise ValueError(SubClassBaseExceptionMsg)

# FIXME: 4 mypy errors
#    _errortools\plugins\safe_ignore.py:10: error: Dispatch type "KeyboardInterrupt" must be subtype of fallback function first argument "type[Exception]"  [misc]
#    _errortools\plugins\safe_ignore.py:14: error: Dispatch type "SystemExit" must be subtype of fallback function first argument "type[Exception]"  [misc]
#    _errortools\plugins\safe_ignore.py:18: error: Dispatch type "BaseException" must be subtype of fallback function first argument "type[Exception]"  [misc]
#    _errortools\plugins\safe_ignore.py:22: error: Dispatch type "BaseException" must be subtype of fallback function first argument "type[Exception]"  [misc]