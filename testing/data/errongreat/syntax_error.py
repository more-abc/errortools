# fmt: off
# autopep8: off
"""Fixture: deliberately broken syntax — exercises the SyntaxError fallback.

This file is intentionally not valid Python so the scanner must surface
an R000 (syntax-error) violation instead of silently dropping it.
"""


def oops(:  # type: ignore
    return  # type: ignore
# type: ignore
