"""Fixture: triggers R002 for bare ``except:`` clauses."""


def parse_int(text):
    try:
        return int(text)
    except:
        print("parse error")
        return 0


def read_file(path):
    try:
        return open(path).read()
    except:
        print("read error")
        return ""
