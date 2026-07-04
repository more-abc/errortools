"""Fixture: triggers every rule at once, with no suppression."""


def everything_wrong(logger):
    logger.error("direct error -- R001")
    logger.warning("direct warning -- R001")
    try:
        risky()
    except:
        pass
    try:
        risky()
    except Exception:
        pass
    try:
        risky()
    except BaseException:
        pass


def tuple_with_broad_exc():
    try:
        risky()
    except (Exception, ValueError):
        pass


def attribute_exc(mod):
    try:
        risky()
    except mod.Exception:
        pass
