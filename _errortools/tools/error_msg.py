from typing import TypeAlias

ErrorMsg: TypeAlias = str

IgnoreUseKeyboardInterruptErrorMessage: ErrorMsg = "You can't ignore KeyboardInterrupt!"
IgnoreUseSystemExitErrorMessage: ErrorMsg = "You can't ignore SystemExit!"
IgnoreUseBaseExceptionErrorMessage: ErrorMsg = "You can't ignore BaseException! It's the base class of all exceptions!"
IgnoreSubClassUseBaseExceptionErrorMessage: ErrorMsg = "You can't ignore BaseException's subclass! It's the base class of all exceptions!"