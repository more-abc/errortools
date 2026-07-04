"""Fixture: every violation is suppressed by a bare ``# eg: ignore`` directive."""


def everything_ignored(logger):  # eg: ignore
    try:
        risky()
    except Exception:
        pass


def everything_ignored_long_form(logger):  # errongreat: ignore
    try:
        risky()
    except ValueError:
        pass


def everything_ignored_typo(logger):  # errnogreat: ignore
    try:
        risky()
    except BaseException:
        pass


def standalone_directive():
    # eg: ignore
    try:
        risky()
    except Exception:
        pass


def standalone_directive_ruff_style():
    # errongreat: ignore
    logger.error("trailing statement")
