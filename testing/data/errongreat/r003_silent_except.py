"""Fixture: triggers R003 — silent except blocks (no log/print/raise)."""


def silent_pass(logger):
    try:
        risky()
    except ValueError:
        pass


def silent_return(logger):
    try:
        risky()
    except ValueError:
        return None


def silent_empty(logger):
    try:
        risky()
    except ValueError:
        ...


def not_silent_raise():
    try:
        risky()
    except ValueError:
        raise


def not_silent_print():
    try:
        risky()
    except ValueError:
        print("error")


def not_silent_logger_method(logger):
    try:
        risky()
    except ValueError:
        logger.exception("boom")


def nested_def_does_not_save(logger):
    try:
        risky()
    except ValueError:

        def helper():
            raise RuntimeError

        helper()
