"""Fixture: empty scoped ignore is a no-op — violations still fire."""


def empty_scope_does_not_save(logger):  # eg: ignore[]
    logger.error("still flagged, no rule IDs supplied")
    try:
        risky()
    except Exception:
        pass


def bare_comment():
    # eg: ignore -- a comment, not a directive
    pass
