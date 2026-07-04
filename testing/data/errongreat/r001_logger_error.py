"""Fixture: triggers R001 for direct ``logger.error(...)`` calls."""


def emit_error(logger):
    logger.error("first violation")
    logger.error("second violation")


def emit_error_with_args(logger):
    logger.error("third %s", "violation")
