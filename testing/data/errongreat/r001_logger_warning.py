"""Fixture: triggers R001 for direct ``logger.warning(...)`` calls."""


def emit_warning(logger):
    logger.warning("first warning")


def emit_warn_alias(logger):
    logger.warn("warn alias — not flagged, only error/warning are")
