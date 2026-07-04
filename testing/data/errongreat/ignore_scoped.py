"""Fixture: scoped ignore directives only silence the listed rules."""


def r001_only_disabled(logger):  # eg: ignore[R001]
    logger.error("this is silenced")
    logger.warning("and this too")
    try:
        risky()
    except Exception:
        pass


def r002_and_r003_disabled():  # eg: ignore[R002,R003]
    try:
        risky()
    except Exception:
        pass


def r003_only_disabled(logger):
    try:
        risky()
    except ValueError:
        pass  # eg: ignore[R003]


def scoped_then_bare(logger):  # eg: ignore[R001]
    logger.error("scoped above")
    try:
        risky()
    except BaseException:
        pass  # eg: ignore
