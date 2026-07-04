"""Fixture: triggers R002 for ``except mod.Exception`` and ``except mod.BaseException``."""


def parse_module_level(mod_exc, mod_be):
    try:
        return 1
    except mod_exc.Exception:
        return 0


def parse_module_base(mod_be):
    try:
        return 1
    except mod_be.BaseException:
        return 0


def parse_module_specific(mod_ve):
    try:
        return 1
    except mod_ve.ValueError:
        return 0
