"""Fixture: triggers R002 for direct ``except Exception`` / ``BaseException``."""


def parse_int_exception(text):
    try:
        return int(text)
    except Exception:
        return 0


def parse_int_base(text):
    try:
        return int(text)
    except BaseException:
        return 0


def parse_int_tuple(text):
    try:
        return int(text)
    except (Exception, ValueError):
        return 0


def parse_int_specific(text):
    try:
        return int(text)
    except ValueError:
        return 0


def parse_int_specific_tuple(text):
    try:
        return int(text)
    except (ValueError, TypeError):
        return 0
