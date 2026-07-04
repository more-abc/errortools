"""Fixture: lives one directory down — exercises recursive directory scans."""


def deep_function(logger):
    logger.error("deep R001")
    try:
        risky()
    except Exception:
        pass


def deeper_function():
    try:
        risky()
    except:
        pass
