This directory contains "newsfragments" which are short files that contain a small markdown-formatted text that will be added to the next `ChangeLog.md`.

Write a precise paragraph reproducing what this PR implements.

like
```markdown
<!-- xxx.bug.md -->
[#xxx](https://github.com/more-abc/errortools/issues/xxx) Optimize `_errortools/xxx.py` and fix type hint bug in `a` function.
```

### How should newsfragment files be named?

The filename consists of three suffix segments:
    1. The first segment is the PR number.
    2. The second segment indicates the change type, such as bug fix, documentation update, or refactor.
    3. The final segment is the Markdown file extension.
