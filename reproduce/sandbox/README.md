> Something need change or refactor? Contact email <errortools.docs@proton.me>

This directory contains "issue reproducers" which are short scripts that reproduce a specific bug report filed against `errortools`.

Write a self-contained script that triggers the bug with the minimum amount of setup.

like
```python
# reproduce_issue_xxx.py
"""Reproduce #xxx: ignore(KeyError) wrongly suppresses KeyboardInterrupt."""
from errortools import ignore

with ignore(KeyError) as err:
    raise KeyboardInterrupt
assert err.be_ignore is False
```

### How should reproducer files be named?

The filename consists of three suffix segments:
    1. The first segment is the GitHub issue number.
    2. The second segment is the literal word `issue`.
    3. The third segment is the issue title slugified to a stable identifier.
    4. The final segment is the Python file extension.
