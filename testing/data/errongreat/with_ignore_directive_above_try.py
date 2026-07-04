"""Fixture: standalone ``# eg: ignore`` directive placed above a ``try``.

A standalone directive on the line above ``try:`` must silence every
handler line that belongs to that ``try`` (``except`` / ``finally``).
"""


def try_directive():
    # eg: ignore
    try:
        risky()
    except:
        pass


def try_directive_finally():
    # eg: ignore
    try:
        risky()
    except Exception:
        pass
    finally:
        cleanup()
