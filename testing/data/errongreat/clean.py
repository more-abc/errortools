"""Fixture: completely clean source — must produce zero violations."""


def add(a, b):
    return a + b


class Calculator:
    def divide(self, x, y):
        try:
            return x / y
        except ZeroDivisionError as exc:
            raise ValueError("division by zero") from exc


def log_info(logger):
    logger.info("informational only — not flagged")
    logger.debug("debug payload")
    return None
