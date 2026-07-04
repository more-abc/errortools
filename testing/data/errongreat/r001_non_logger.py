"""Fixture: must NOT trigger R001 — proves the visitor is name-narrow.

The scanner only matches the literal name ``logger``. Calls on
``self.logger``, ``logging.error``, ``LOG.error`` or any other variant
must be silently ignored.
"""

import logging


class Worker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def do_work(self):
        self.logger.error("attached attribute — not flagged")
        self.logger.warning("attached attribute — not flagged")


def use_module_logger():
    logging.error("module-level logger — not flagged")
    logging.warning("module-level logger — not flagged")


def use_caps_logger(LOG):
    LOG.error("uppercase name — not flagged")
    LOG.warning("uppercase name — not flagged")
