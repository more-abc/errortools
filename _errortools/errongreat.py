"""Errongreat — a zero-dependency static scanner for errortools.

Errongreat is a small, self-contained static-analysis tool for the
errortools project.  It walks Python source files via the standard
library's :mod:`ast` module and reports violations of three project-wide
coding rules:

``R001`` — :data:`R001_NO_DIRECT_LOGGER_ERROR_WARNING`
    Direct calls to ``logger.error(...)`` / ``logger.warning(...)`` are
    forbidden.  Use :func:`errortools.exception` (or a typed wrapper)
    instead so the log line is enriched with the active exception.

``R002`` — :data:`R002_NO_BARE_OR_TOO_BROAD_EXCEPT`
    Bare ``except:`` clauses and direct catches of :class:`Exception`
    or :class:`BaseException` (including ``except (Exception, ...):``
    tuples) are forbidden.  Catch a specific subclass instead.

``R003`` — :data:`R003_NO_SILENT_EXCEPT`
    Every ``except`` block must contain at least one logging call, a
    ``print(...)`` call, or a ``raise`` statement.  Silent exception
    swallowing is forbidden.

The scanner has **no** runtime dependency on Flake8, ``pluggy`` or any
other third-party plugin loader — only :mod:`ast`, :mod:`pathlib` and
the rest of the standard library.

Public API
----------
* :class:`Violation` — a frozen dataclass describing a single finding.
* :data:`RULE_IDS` — the tuple of rule IDs recognised by the scanner.
* :func:`scan_source` — scan an in-memory source string.
* :func:`scan_file` — scan a single file on disk.
* :func:`scan_path` — scan a file or directory.
* :func:`main` — the ``python -m _errortools.errongreat`` entry point.

The module also doubles as a command-line tool::

    python -m _errortools.errongreat path/to/code
    python -m _errortools.errongreat --format json path/to/code
    python -m _errortools.errongreat --rule R001 path/to/code
"""

from __future__ import annotations

import argparse
import ast
import configparser
import fnmatch
import json
import pathlib
import re
import sys
from dataclasses import asdict, dataclass, field
from typing import Final, Iterable, Mapping, Sequence, Union

__all__ = [
    "Violation",
    "RULE_IDS",
    "R001_NO_DIRECT_LOGGER_ERROR_WARNING",
    "R002_NO_BARE_OR_TOO_BROAD_EXCEPT",
    "R003_NO_SILENT_EXCEPT",
    "scan_source",
    "scan_file",
    "scan_path",
    "main",
]


# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

R001_NO_DIRECT_LOGGER_ERROR_WARNING: Final[str] = "R001"
R002_NO_BARE_OR_TOO_BROAD_EXCEPT: Final[str] = "R002"
R003_NO_SILENT_EXCEPT: Final[str] = "R003"

RULE_IDS: Final[tuple[str, ...]] = (
    R001_NO_DIRECT_LOGGER_ERROR_WARNING,
    R002_NO_BARE_OR_TOO_BROAD_EXCEPT,
    R003_NO_SILENT_EXCEPT,
)


# ---------------------------------------------------------------------------
# Internal constants
# ---------------------------------------------------------------------------

_LOGGER_NAMES: Final[frozenset[str]] = frozenset({"logger"})

_LOG_METHODS: Final[frozenset[str]] = frozenset(
    {
        "debug",
        "info",
        "warning",
        "warn",
        "error",
        "critical",
        "exception",
        "log",
        "fatal",
    }
)

_FORBIDDEN_EXCEPT_NAMES: Final[frozenset[str]] = frozenset({"Exception", "BaseException"})

_PY_SUFFIXES: Final[tuple[str, ...]] = (".py",)

_INTERNAL_RULE_ID: Final[str] = "R000"


# ---------------------------------------------------------------------------
# Ignore directives
# ---------------------------------------------------------------------------
#
# Source code may opt out of a finding by placing a directive comment on
# either the line that triggers the violation (trailing comment) or the
# line immediately above (standalone comment).  The supported spellings
# are::
#
#     # errongreat: ignore
#     # errongreat: ignore[R001,R002]
#     # eg: ignore                # short alias
#     # eg: ignore[R003]          # short alias, scoped to R003
#
# The directive's ``[...]`` part, when present, restricts the suppression
# to the listed rule IDs; when absent, the suppression covers every rule.
# A directive may appear on the same line as the violation (Flake8-style
# trailing comment) or on the line directly above (Ruff-style standalone
# comment).  Other placements are intentionally ignored so that comments
# far away from the violation cannot silently silence it.


#: Regex used to recognise an Errongreat ignore directive inside a comment.
#: Group 1, when present, holds the comma-separated list of rule IDs;
#: when the directive is bare (``# eg: ignore``), group 1 is ``None``.
_IGNORE_COMMENT_RE: Final[re.Pattern[str]] = re.compile(
    r"#\s*(?:errongreat|errnogreat|eg)\s*:\s*ignore(?:\s*\[([^\]]*)\])?",
    re.IGNORECASE,
)

#: Sentinel value used as a directive's rule set to mean
#: "ignore every rule".  A bare ``# eg: ignore`` comment produces
#: this set; a scoped ``# eg: ignore[R001,R002]`` produces a regular
#: frozenset of rule IDs.  Because real rule IDs never contain a
#: ``"*"``, the sentinel is unambiguous.
_IGNORE_ALL_RULES: Final[frozenset[str]] = frozenset({"*"})


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Violation:
    """A single rule violation reported by the scanner.

    Attributes:
        file: Path of the file that triggered the violation, or a
            synthetic label such as ``"<string>"`` for in-memory scans.
        line: 1-based line number of the violation site.
        col: 0-based column offset of the violation site.
        rule_id: One of :data:`RULE_IDS`, or :data:`_INTERNAL_RULE_ID`
            for infrastructure findings.
        rule_name: Stable snake-case identifier of the rule.
        message: Human-readable explanation suitable for printing.
    """

    file: str
    line: int
    col: int
    rule_id: str
    rule_name: str
    message: str

    def format(self) -> str:
        """Return the violation rendered in the ``path:line:col:`` shape
        that most editors and CI pipelines understand as a quickfix
        target.
        """
        return f"{self.file}:{self.line}:{self.col}: [{self.rule_id}] {self.message}"


# ---------------------------------------------------------------------------
# Visitor base class
# ---------------------------------------------------------------------------
#
# :class:`ast.NodeVisitor` does not declare a ``violations`` slot, so a
# static type checker cannot know that every concrete visitor in this
# module exposes one.  We bridge the gap with a tiny private base class
# that fixes the attribute's type and initialises it to an empty list.


class _BaseVisitor(ast.NodeVisitor):
    """Shared base class for Errongreat's AST visitors.

    Concrete subclasses accumulate findings in :attr:`violations`
    while :meth:`ast.NodeVisitor.visit` walks the tree.
    """

    violations: list[Violation]

    def __init__(self, file_path: str) -> None:
        super().__init__()
        self._file = file_path
        self.violations = []


# ---------------------------------------------------------------------------
# R001 — no direct logger.error / logger.warning
# ---------------------------------------------------------------------------


class _LoggerErrorWarningVisitor(_BaseVisitor):
    """Detect direct calls to ``logger.error(...)`` or ``logger.warning(...)``.

    The match is intentionally narrow: only the literal name
    ``logger`` followed by ``.error`` or ``.warning`` triggers R001.
    Other shapes such as ``self.logger.error(...)``,
    ``logging.getLogger().error(...)`` or ``LOGGER.error(...)`` are
    deliberately ignored — they are either out of scope (logging
    framework) or non-canonical (attributes, different capitalisation).
    """

    RULE_ID: Final[str] = R001_NO_DIRECT_LOGGER_ERROR_WARNING
    RULE_NAME: Final[str] = "no-direct-logger-error-warning"
    _FORBIDDEN_ATTRS: Final[frozenset[str]] = frozenset({"error", "warning"})

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and func.attr in self._FORBIDDEN_ATTRS
            and isinstance(func.value, ast.Name)
            and func.value.id in _LOGGER_NAMES
        ):
            kind = func.attr
            self.violations.append(
                Violation(
                    file=self._file,
                    line=node.lineno,
                    col=node.col_offset,
                    rule_id=self.RULE_ID,
                    rule_name=self.RULE_NAME,
                    message=(
                        f"Direct call to `logger.{kind}(...)` is forbidden; "
                        "use errortools.exception(...) or a typed wrapper."
                    ),
                )
            )
        self.generic_visit(node)


# ---------------------------------------------------------------------------
# R002 — no bare except, no direct Exception / BaseException
# ---------------------------------------------------------------------------


class _BadExceptVisitor(_BaseVisitor):
    """Detect bare ``except:`` and direct ``Exception`` / ``BaseException`` catches."""

    RULE_ID: Final[str] = R002_NO_BARE_OR_TOO_BROAD_EXCEPT
    RULE_NAME: Final[str] = "no-bare-or-too-broad-except"

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.type is None:
            self.violations.append(
                Violation(
                    file=self._file,
                    line=node.lineno,
                    col=node.col_offset,
                    rule_id=self.RULE_ID,
                    rule_name=self.RULE_NAME,
                    message=("Bare `except:` clause is forbidden; " "catch a specific exception type."),
                )
            )
        else:
            self._inspect_type(node.type)
        self.generic_visit(node)

    def _inspect_type(self, type_node: ast.expr) -> None:
        """Inspect the expression that follows ``except``.

        Handles three common shapes:

        * ``Name``      — ``except Exception:``
        * ``Tuple``     — ``except (Exception, ValueError):``
        * ``Attribute`` — ``except mod.Exception:`` (rare but valid)
        """
        if isinstance(type_node, ast.Name):
            if type_node.id in _FORBIDDEN_EXCEPT_NAMES:
                self._report(type_node, type_node.id)
            return
        if isinstance(type_node, ast.Tuple):
            for elt in type_node.elts:
                if isinstance(elt, ast.Name) and elt.id in _FORBIDDEN_EXCEPT_NAMES:
                    self._report(elt, elt.id)
                elif isinstance(elt, ast.Attribute) and elt.attr in _FORBIDDEN_EXCEPT_NAMES:
                    self._report(elt, elt.attr)
            return
        if isinstance(type_node, ast.Attribute) and type_node.attr in _FORBIDDEN_EXCEPT_NAMES:
            self._report(type_node, type_node.attr)

    def _report(self, node: ast.expr, name: str) -> None:
        self.violations.append(
            Violation(
                file=self._file,
                line=node.lineno,
                col=node.col_offset,
                rule_id=self.RULE_ID,
                rule_name=self.RULE_NAME,
                message=(f"Catching `{name}` directly is forbidden; " "catch a more specific subclass."),
            )
        )


# ---------------------------------------------------------------------------
# R003 — no silent except
# ---------------------------------------------------------------------------


class _SilentExceptVisitor(_BaseVisitor):
    """Detect ``except`` blocks that contain no log/print/raise statement.

    "Silent" here means *no visible side-effect*: a bare ``pass``, an
    unconditional ``return`` from a try/except used purely for control
    flow, or an empty body all qualify.  Conversely, an ``except`` block
    that ends with ``raise`` (re-raise) is **not** silent — the
    original exception is preserved and propagated.
    """

    RULE_ID: Final[str] = R003_NO_SILENT_EXCEPT
    RULE_NAME: Final[str] = "no-silent-except"

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if not _block_outputs(node.body):
            self.violations.append(
                Violation(
                    file=self._file,
                    line=node.lineno,
                    col=node.col_offset,
                    rule_id=self.RULE_ID,
                    rule_name=self.RULE_NAME,
                    message=(
                        "`except` block contains no log/print/raise "
                        "statement; exceptions will be swallowed silently."
                    ),
                )
            )
        self.generic_visit(node)


def _block_outputs(body: Sequence[ast.stmt]) -> bool:
    """Return ``True`` if *body* contains at least one logging call,
    a ``print(...)`` call, or a ``raise`` statement.

    Nested function / class definitions are skipped on purpose: their
    bodies are evaluated lazily and a ``raise`` inside ``def helper():``
    does **not** log the surrounding ``except``.  Nested ``try`` blocks
    *are* walked — a ``raise`` inside a nested ``except`` does count as
    output for the outer block, because the outer ``except`` has
    decided to do something with the failure.
    """
    for stmt in body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            # Own scope — does not "log" the outer except block.
            continue
        for sub in ast.walk(stmt):
            if isinstance(sub, ast.Raise):
                return True
            if isinstance(sub, ast.Call):
                func = sub.func
                if isinstance(func, ast.Name) and func.id == "print":
                    return True
                if isinstance(func, ast.Attribute) and func.attr in _LOG_METHODS:
                    return True
    return False


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
#
# Errongreat reads its runtime configuration from one of three optional
# files: ``errongreat.ini``, ``errongreat.cfg`` or ``pyproject.toml``
# (under the ``[tool.errongreat]`` section).  The schema is intentionally
# small — five keys, no nested sections required — so the parser can
# stay stdlib-only and work on every supported Python version.
#
# Schema::
#
#     select = R001,R002          # rule IDs to enable (default: all)
#     ignore = R003               # rule IDs to disable (subtractive)
#     exclude = tests/*,docs/*    # glob patterns to skip entirely
#     extend-exclude = *.pyc      # extra patterns appended to ``exclude``
#     per-file-ignores =          # one ``pattern: R1,R2`` per line
#         tests/legacy.py: R003
#
# INI files use ``,`` as a separator and continuation lines for
# ``per-file-ignores``.  ``pyproject.toml`` uses TOML syntax: lists for
# string-valued keys and an inline table for ``per-file-ignores``.


#: Filenames searched (in this order) when no explicit ``--config`` is
#: supplied.  INI files win over ``pyproject.toml`` so that projects
#: that already carry an Errongreat-specific file are not forced to
#: also write a TOML section.
_CONFIG_FILENAMES: Final[tuple[str, ...]] = (
    "errongreat.ini",
    "errongreat.cfg",
    "pyproject.toml",
)


@dataclass(frozen=True)
class Config:
    """Resolved Errongreat configuration.

    A ``Config`` instance is the *fully merged* view of all settings —
    defaults, the loaded config file, and any CLI overrides applied by
    :func:`main`.  Downstream code should treat the dataclass as
    read-only.

    Attributes:
        select: Set of rule IDs that may fire.  Defaults to every rule
            in :data:`RULE_IDS`.
        ignore: Set of rule IDs to subtract from *select*.  Applied
            *after* per-file ignores so that CLI ``--ignore`` flags can
            broaden the suppression set without re-listing the per-file
            exceptions.
        exclude: Glob patterns of files to skip during a directory
            scan.  Each pattern is matched against the file's absolute
            path *and* its relative path from the project root, so
            both ``tests/*`` and ``**/tests/*`` work as expected.
        extend_exclude: Extra exclude patterns appended to *exclude*.
        per_file_ignores: Mapping of glob patterns to rule IDs that are
            *additionally* disabled when a file matches the pattern.
            This mirrors Ruff's ``[tool.ruff.per-file-ignores]``.
        source_path: Path of the config file the values were loaded
            from, or ``None`` when only defaults are in effect.
    """

    select: frozenset[str] = field(default_factory=lambda: frozenset(RULE_IDS))
    ignore: frozenset[str] = field(default_factory=frozenset)
    exclude: tuple[str, ...] = ()
    extend_exclude: tuple[str, ...] = ()
    per_file_ignores: "Mapping[str, frozenset[str]]" = field(default_factory=dict)
    source_path: Union[str, None] = None

    @property
    def enabled_rules(self) -> frozenset[str]:
        """Set of rule IDs enabled globally.

        Equivalent to ``self.select - self.ignore``; recomputed on every
        access because both sets are tiny and the dataclass is frozen.
        """
        return self.select - self.ignore

    @property
    def all_excludes(self) -> tuple[str, ...]:
        """Tuple of every exclude pattern (regular + extended)."""
        return self.exclude + self.extend_exclude

    def enabled_rules_for(self, file_path: str) -> frozenset[str]:
        """Return the set of rule IDs enabled for *file_path*.

        Starts from :attr:`enabled_rules` and subtracts the rule IDs
        associated with every ``per-file-ignores`` pattern that matches
        the path.
        """
        result = self.enabled_rules
        if not self.per_file_ignores:
            return result
        for pattern, ignored in self.per_file_ignores.items():
            if _glob_match(pattern, file_path):
                result = result - ignored
        return result

    def is_excluded(self, file_path: str) -> bool:
        """Return ``True`` when *file_path* matches any exclude pattern."""
        for pattern in self.all_excludes:
            if _glob_match(pattern, file_path):
                return True
        return False

    def merged_with(
        self,
        *,
        select: Union[Iterable[str], None] = None,
        ignore: Union[Iterable[str], None] = None,
        exclude: Union[Iterable[str], None] = None,
        extend_exclude: Union[Iterable[str], None] = None,
    ) -> "Config":
        """Return a copy of *self* with the given CLI overrides applied.

        * ``select`` and ``ignore`` **replace** the corresponding
          fields when supplied.  This is the same semantics as the
          ``--select`` / ``--ignore`` CLI flags, which let the user
          override the file-driven defaults wholesale.
        * ``exclude`` and ``extend_exclude`` **replace** their fields
          when supplied; pass an empty list to clear them.
        """
        return Config(
            select=frozenset(select) if select is not None else self.select,
            ignore=frozenset(ignore) if ignore is not None else self.ignore,
            exclude=tuple(exclude) if exclude is not None else self.exclude,
            extend_exclude=tuple(extend_exclude) if extend_exclude is not None else self.extend_exclude,
            per_file_ignores=self.per_file_ignores,
            source_path=self.source_path,
        )


def _glob_match(pattern: str, path: str) -> bool:
    """Return ``True`` when *path* matches *pattern*.

    :meth:`pathlib.PurePath.match` is used because it correctly restricts
    the ``*`` wildcard to a single path segment (``*`` does **not** cross
    ``/`` boundaries), which matches the intuitive semantics of exclusion
    patterns.
    """
    return pathlib.PurePath(path).match(pattern)


# ---------------------------------------------------------------------------
# INI / cfg parser
# ---------------------------------------------------------------------------


def _parse_csv_list(raw: str) -> tuple[str, ...]:
    """Split a comma-separated config value into a tuple of stripped tokens.

    Empty tokens (caused by trailing commas or double separators) are
    silently dropped so callers do not have to pre-sanitise their input.
    """
    if not raw:
        return ()
    return tuple(token.strip() for token in raw.split(",") if token.strip())


def _parse_ini_config(path: pathlib.Path) -> Config:
    """Parse an ``errongreat.ini`` / ``errongreat.cfg`` file."""
    parser = configparser.ConfigParser(allow_no_value=True, delimiters=("=",))
    parser.read(path, encoding="utf-8")
    if not parser.has_section("errongreat"):
        return Config(source_path=str(path))

    section = parser["errongreat"]
    select = _parse_csv_list(section.get("select", ""))
    ignore = _parse_csv_list(section.get("ignore", ""))
    exclude = _parse_csv_list(section.get("exclude", ""))
    extend_exclude = _parse_csv_list(section.get("extend-exclude", ""))

    per_file_ignores: dict[str, frozenset[str]] = {}
    if parser.has_option("errongreat", "per-file-ignores"):
        # ``configparser`` keeps multi-line values as embedded ``\n``.
        raw = section.get("per-file-ignores", "")
        for line in raw.splitlines():
            entry = line.strip()
            if not entry or ":" not in entry:
                continue
            pattern, rules = entry.split(":", 1)
            rule_set = frozenset(_parse_csv_list(rules))
            if rule_set:
                per_file_ignores[pattern.strip()] = rule_set

    return Config(
        select=frozenset(select) if select else frozenset(RULE_IDS),
        ignore=frozenset(ignore),
        exclude=exclude,
        extend_exclude=extend_exclude,
        per_file_ignores=per_file_ignores,
        source_path=str(path),
    )


# ---------------------------------------------------------------------------
# Minimal pyproject.toml extractor
# ---------------------------------------------------------------------------
#
# The project supports Python 3.8+, which predates :mod:`tomllib`
# (added in 3.11).  Rather than take on a runtime dependency we
# implement a small regex-based extractor that understands the
# subset of TOML we actually use: simple ``key = "string"`` pairs,
# ``key = ["a", "b"]`` lists, and ``key = { "p" = ["R1"] }`` inline
# tables for ``per-file-ignores``.


_TOML_SECTION_HEADER_RE: Final[re.Pattern[str]] = re.compile(
    r"^\[(?P<path>[^\]]+)\]\s*$",
    re.MULTILINE,
)
_TOML_STRING_VALUE_RE: Final[re.Pattern[str]] = re.compile(
    r'^\s*(?P<key>[A-Za-z_][\w\-]*)\s*=\s*"(?P<value>[^"\\]*(?:\\.[^"\\]*)*)"\s*(?:#[^\n]*)?$',
)
_TOML_LIST_VALUE_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*(?P<key>[A-Za-z_][\w\-]*)\s*=\s*\[(?P<body>[^\[\]]*)\]\s*$",
)
_TOML_INLINE_TABLE_VALUE_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*(?P<key>[A-Za-z_][\w\-]*)\s*=\s*\{(?P<body>[^{}]*)\}\s*$",
)
_TOML_LIST_ITEM_RE: Final[re.Pattern[str]] = re.compile(r'"((?:[^"\\]|\\.)*)"')


def _split_toml_sections(text: str) -> dict[str, list[str]]:
    """Group *text* into ``section_path -> list_of_body_lines``.

    The result keeps the body lines verbatim so the per-section parsers
    can apply the right regex against each line.
    """
    sections: dict[str, list[str]] = {}
    matches = list(_TOML_SECTION_HEADER_RE.finditer(text))
    for index, match in enumerate(matches):
        path = match.group("path").strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].splitlines()
        sections.setdefault(path, []).extend(body)
    return sections


def _extract_string_list(body: Sequence[str], key: str) -> tuple[str, ...]:
    """Return the list value bound to *key* in *body*, or ``()``."""
    for line in body:
        match = _TOML_LIST_VALUE_RE.match(line)
        if match and match.group("key") == key:
            return tuple(_TOML_LIST_ITEM_RE.findall(match.group("body")))
    return ()


def _extract_string(body: Sequence[str], key: str) -> Union[str, None]:
    """Return the string value bound to *key* in *body*, or ``None``."""
    for line in body:
        match = _TOML_STRING_VALUE_RE.match(line)
        if match and match.group("key") == key:
            return match.group("value")
    return None


def _extract_inline_table_of_lists(body: Sequence[str], key: str) -> dict[str, frozenset[str]]:
    """Parse ``key = { "pat" = ["R1", "R2"], ... }`` from *body*.

    Returns an empty dict when the key is absent or malformed.  Malformed
    entries (missing list, unbalanced braces) are skipped silently — we
    would rather ignore a config typo than crash the scan.
    """
    for line in body:
        match = _TOML_INLINE_TABLE_VALUE_RE.match(line)
        if not match or match.group("key") != key:
            continue
        body_text = match.group("body")
        result: dict[str, frozenset[str]] = {}
        # Each entry looks like ``"pattern" = ["R1", "R2"]``.
        entry_re = re.compile(r'"((?:[^"\\]|\\.)*)"\s*=\s*\[((?:[^][]|\[[^][]*\])*)\]')
        for entry_match in entry_re.finditer(body_text):
            pattern = entry_match.group(1)
            inner = entry_match.group(2)
            rules = _TOML_LIST_ITEM_RE.findall(inner)
            if pattern and rules:
                result[pattern] = frozenset(rules)
        return result
    return {}


def _parse_toml_config(path: pathlib.Path) -> Config:
    """Parse the ``[tool.errongreat]`` section of a ``pyproject.toml``."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return Config(source_path=str(path))

    sections = _split_toml_sections(text)
    body = sections.get("tool.errongreat") or sections.get("tool .errongreat") or []
    if not body:
        return Config(source_path=str(path))

    select = _extract_string_list(body, "select")
    ignore = _extract_string_list(body, "ignore")
    exclude = _extract_string_list(body, "exclude")
    extend_exclude = _extract_string_list(body, "extend-exclude")
    per_file_ignores = _extract_inline_table_of_lists(body, "per-file-ignores")

    return Config(
        select=frozenset(select) if select else frozenset(RULE_IDS),
        ignore=frozenset(ignore),
        exclude=tuple(exclude),
        extend_exclude=tuple(extend_exclude),
        per_file_ignores=per_file_ignores,
        source_path=str(path),
    )


# ---------------------------------------------------------------------------
# Config discovery
# ---------------------------------------------------------------------------


def load_config(
    path: Union[str, pathlib.Path, None] = None,
    *,
    search_dirs: Union[Iterable[pathlib.Path], None] = None,
) -> Config:
    """Return the resolved :class:`Config`.

    Args:
        path: Optional explicit config file.  When supplied it is the
            only file consulted; missing files raise :class:`FileNotFoundError`.
        search_dirs: Iterable of directories to search.  Defaults to
            ``[pathlib.Path.cwd()]``.

    Returns:
        The parsed :class:`Config`.  When neither *path* nor any file
        in *search_dirs* yields a config, an empty ``Config`` (every
        rule enabled, no exclusions) is returned.

    Raises:
        FileNotFoundError: when *path* is supplied but does not exist.
        ValueError: when *path* has an unsupported extension.
    """
    if path is not None:
        candidate = pathlib.Path(path)
        if not candidate.is_file():
            raise FileNotFoundError(f"Config file not found: {candidate}")
        return _parse_config_file(candidate)

    dirs = list(search_dirs) if search_dirs is not None else [pathlib.Path.cwd()]
    for directory in dirs:
        for name in _CONFIG_FILENAMES:
            candidate = directory / name
            if candidate.is_file():
                return _parse_config_file(candidate)
    return Config()


def _parse_config_file(path: pathlib.Path) -> Config:
    """Dispatch to the right parser based on *path*'s name."""
    if path.name == "pyproject.toml":
        return _parse_toml_config(path)
    if path.suffix in {".ini", ".cfg"}:
        return _parse_ini_config(path)
    # Fall back to INI for files literally named ``errongreat.config`` etc.
    return _parse_ini_config(path)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def _make_visitors(file_path: str) -> list[_BaseVisitor]:
    """Return a fresh visitor triple for *file_path*."""
    return [
        _LoggerErrorWarningVisitor(file_path),
        _BadExceptVisitor(file_path),
        _SilentExceptVisitor(file_path),
    ]


# ---------------------------------------------------------------------------
# Ignore-directive parsing
# ---------------------------------------------------------------------------


def _is_pure_comment_line(line: str) -> bool:
    """Return ``True`` when *line* is blank or a pure ``#`` comment.

    Used by :func:`_scan_ignore_comments` to skip past blank lines and
    unrelated comments while looking for the next "real" code line that
    a directive should attach to.
    """
    stripped = line.lstrip()
    return not stripped or stripped.startswith("#")


def _next_code_line(lines: Sequence[str], after_lineno: int) -> Union[int, None]:
    """Return the 1-based line number of the next non-comment line after *after_lineno*.

    Returns ``None`` when the directive sits at the end of the file.
    """
    for idx in range(after_lineno, len(lines)):
        if not _is_pure_comment_line(lines[idx]):
            return idx + 1  # convert 0-based index to 1-based line number
    return None


def _line_node_map(tree: ast.AST) -> dict[int, ast.AST]:
    """Return a ``lineno -> AST node`` mapping for every node in *tree*.

    When several nodes share the same ``lineno`` the *outermost* node
    wins, because :func:`ast.walk` visits nodes in document order and
    the outermost node is always enumerated before any of its children.
    """
    mapping: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        lineno = getattr(node, "lineno", None)
        if lineno is None:
            continue
        mapping.setdefault(lineno, node)
    return mapping


def _covered_lines_for_directive(
    directive_lineno: int,
    start_lineno: int,
    node_at_start: Union[ast.AST, None],
    node_at_directive: Union[ast.AST, None] = None,
) -> frozenset[int]:
    """Return the set of line numbers a directive at *directive_lineno* suppresses.

    Coverage rules:

    1. The directive's own line is always covered (Flake8-style
       trailing comment).
    2. The line immediately following the directive is covered when
       it is the next non-blank line (Ruff-style standalone comment).
    3. When the next non-blank line starts a :class:`ast.Try` statement,
       the coverage is **extended** to every ``except:`` / ``finally:``
       handler line belonging to that ``try``.  This is what lets a
       directive placed above ``try:`` also silence R002/R003 violations
       reported on the corresponding ``except:`` line.
    4. When the directive sits on the same line as a ``def`` / ``class``
       definition, the coverage is extended to every line inside the
       block so that a single trailing comment can silence an entire
       function or class.
    """
    covered: set[int] = {directive_lineno}
    if start_lineno == directive_lineno + 1:
        covered.add(start_lineno)
    if isinstance(
        node_at_directive,
        (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
    ):
        end = getattr(node_at_directive, "end_lineno", None)
        if end is not None:
            covered.update(range(directive_lineno, end + 1))
    elif isinstance(node_at_start, ast.Try):
        for handler in node_at_start.handlers:
            if handler is not None:
                covered.add(handler.lineno)
    return frozenset(covered)


def _scan_ignore_comments(
    source: str,
    tree: ast.AST,
) -> dict[int, tuple[frozenset[str], frozenset[int]]]:
    """Return a ``directive_line -> (rule_set, covered_lines)`` mapping.

    The returned mapping contains an entry for every line whose source
    text matches :data:`_IGNORE_COMMENT_RE`.  For each directive we
    record the set of rule IDs it suppresses (or :data:`_IGNORE_ALL_RULES`
    when the directive is bare) together with the set of source lines
    the directive is allowed to suppress.

    Empty scoped directives (``# eg: ignore[]``) are silently treated
    as no-ops and never appear in the mapping.
    """
    lines = source.splitlines()
    line_to_node = _line_node_map(tree)
    directives: dict[int, tuple[frozenset[str], frozenset[int]]] = {}

    for lineno, line in enumerate(lines, start=1):
        match = _IGNORE_COMMENT_RE.search(line)
        if match is None:
            continue
        start_lineno = _next_code_line(lines, lineno)
        if start_lineno is None:
            continue
        node_at_start = line_to_node.get(start_lineno)
        node_at_directive = line_to_node.get(lineno)
        covered = _covered_lines_for_directive(lineno, start_lineno, node_at_start, node_at_directive)

        rules_str = match.group(1)
        if rules_str is None:
            rule_set: frozenset[str] = _IGNORE_ALL_RULES
        else:
            rule_set = frozenset(r.strip() for r in rules_str.split(",") if r.strip())
        if not rule_set:
            # ``frozenset()`` would mean "ignore nothing" — treat as no-op.
            continue
        directives[lineno] = (rule_set, covered)

    return directives


def _is_violation_ignored(
    violation: Violation,
    directives: dict[int, tuple[frozenset[str], frozenset[int]]],
) -> bool:
    """Return ``True`` when *violation* is suppressed by a directive.

    A directive suppresses a violation when:

    * the violation's line falls inside the directive's coverage set,
      **and**
    * the directive's rule set covers :attr:`Violation.rule_id` (either
      explicitly or via the :data:`_IGNORE_ALL_RULES` sentinel).
    """
    for _directive_line, (rule_set, covered) in directives.items():
        if violation.line not in covered:
            continue
        if rule_set == _IGNORE_ALL_RULES or violation.rule_id in rule_set:
            return True
    return False


def _apply_directives(
    violations: Sequence[Violation],
    directives: dict[int, tuple[frozenset[str], frozenset[int]]],
) -> list[Violation]:
    """Return *violations* with every directive-suppressed entry removed."""
    if not directives:
        return list(violations)
    return [v for v in violations if not _is_violation_ignored(v, directives)]


def scan_source(source: str, *, file_path: str = "<string>") -> list[Violation]:
    """Scan a Python source *source* string.

    Args:
        source: The Python source code to analyse.
        file_path: Label used to identify the source in :class:`Violation`
            records.  Defaults to ``"<string>"``.

    Returns:
        A list of :class:`Violation` objects sorted by ``(line, col,
        rule_id)``.  The list is empty when the source is clean.
    """
    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as exc:
        # Surface a SyntaxError as an R000 (infrastructure) finding so
        # callers can present it alongside rule violations instead of
        # silently dropping it.
        print(
            f"errongreat: SyntaxError in {file_path}: {exc.msg}",
            file=sys.stderr,
        )
        return [
            Violation(
                file=file_path,
                line=exc.lineno or 0,
                col=exc.offset or 0,
                rule_id=_INTERNAL_RULE_ID,
                rule_name="syntax-error",
                message=f"SyntaxError: {exc.msg}",
            )
        ]
    violations: list[Violation] = []
    for visitor in _make_visitors(file_path):
        visitor.visit(tree)
        violations.extend(visitor.violations)
    # Apply ``# eg: ignore[...]`` / ``# errongreat: ignore[...]``
    # directives *after* the visitors have produced every finding so
    # that a directive placed on a multi-statement block is consulted
    # exactly once per suppressed violation.
    directives = _scan_ignore_comments(source, tree)
    violations = _apply_directives(violations, directives)
    violations.sort(key=lambda v: (v.line, v.col, v.rule_id))
    return violations


def scan_file(path: Union[str, pathlib.Path]) -> list[Violation]:
    """Scan a single file on disk.

    Args:
        path: Path to the ``.py`` file to analyse.  Non-UTF-8 contents
            are reported as an R000 violation rather than raising.

    Returns:
        The list of :class:`Violation` objects found in the file.  An
        empty list means the file is clean.
    """
    path = pathlib.Path(path)
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(
            f"errongreat: cannot read {path}: {exc!r}",
            file=sys.stderr,
        )
        return [
            Violation(
                file=str(path),
                line=0,
                col=0,
                rule_id=_INTERNAL_RULE_ID,
                rule_name="file-read-error",
                message=f"Cannot read file: {exc!r}",
            )
        ]
    except UnicodeDecodeError as exc:
        print(
            f"errongreat: cannot decode {path} as UTF-8: {exc!r}",
            file=sys.stderr,
        )
        return [
            Violation(
                file=str(path),
                line=0,
                col=0,
                rule_id=_INTERNAL_RULE_ID,
                rule_name="file-read-error",
                message=f"Cannot decode file as UTF-8: {exc!r}",
            )
        ]
    return scan_source(source, file_path=str(path))


def _apply_config_to_violations(
    violations: Sequence[Violation],
    enabled_rules: frozenset[str],
) -> list[Violation]:
    """Drop every violation whose rule is not in *enabled_rules*.

    Infrastructure findings (R000) always survive — they describe the
    scanner's own state, not the source code, and silencing them would
    hide genuine problems in the file-under-analysis.
    """
    if not enabled_rules:
        return list(violations)
    return [v for v in violations if v.rule_id == _INTERNAL_RULE_ID or v.rule_id in enabled_rules]


def scan_path(
    path: Union[str, pathlib.Path],
    *,
    recursive: bool = True,
    config: Union[Config, None] = None,
) -> list[Violation]:
    """Scan a file or directory.

    Args:
        path: A file or directory path.  When *path* points to a
            directory, every ``*.py`` file inside it (and, when
            *recursive* is true, every ``*.py`` file beneath it) is
            scanned.
        recursive: When ``True`` (the default), descend into
            subdirectories.  When ``False``, only the top-level
            directory is scanned.
        config: Optional :class:`Config`.  When supplied it is used to
            (a) skip files matching ``exclude`` / ``extend-exclude``,
            (b) restrict the rules reported per file according to
            ``select`` / ``ignore`` / ``per-file-ignores``.  When
            ``None`` every rule is enabled and no files are excluded.

    Returns:
        A flat list of :class:`Violation` objects across every file
        examined, sorted by file name then by ``(line, col, rule_id)``.
        When *path* does not exist, a single ``path-not-found``
        violation is returned.
    """
    path = pathlib.Path(path)
    config = config or Config()
    if path.is_file():
        return _apply_config_to_violations(scan_file(path), config.enabled_rules_for(str(path)))
    if not path.is_dir():
        return [
            Violation(
                file=str(path),
                line=0,
                col=0,
                rule_id=_INTERNAL_RULE_ID,
                rule_name="path-not-found",
                message=f"Path not found: {path}",
            )
        ]

    if recursive:
        candidates: Iterable[pathlib.Path] = (p for p in path.rglob("*") if p.suffix in _PY_SUFFIXES and p.is_file())
    else:
        candidates = (p for p in path.iterdir() if p.suffix in _PY_SUFFIXES and p.is_file())
    results: list[Violation] = []
    for py_file in sorted(candidates):
        if config.is_excluded(str(py_file)):
            continue
        enabled = config.enabled_rules_for(str(py_file))
        results.extend(_apply_config_to_violations(scan_file(py_file), enabled))
    results.sort(key=lambda v: (v.file, v.line, v.col, v.rule_id))
    return results


# ---------------------------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------------------------


_PROG: Final[str] = "python -m _errortools.errongreat"
_DESCRIPTION: Final[str] = "Errongreat — a zero-dependency static scanner for errortools."


def _build_parser() -> argparse.ArgumentParser:
    """Construct the :mod:`argparse` parser for the CLI.

    The ``color=True`` keyword is only supported from Python 3.14, so
    it is supplied conditionally to remain compatible with the
    project's ``requires-python = ">=3.8"`` baseline.
    """
    if sys.version_info >= (3, 14):
        parser = argparse.ArgumentParser(
            prog=_PROG,
            description=_DESCRIPTION,
            color=True,
        )
    else:
        parser = argparse.ArgumentParser(prog=_PROG, description=_DESCRIPTION)

    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="File or directory to scan.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        default=True,
        help="Recurse into subdirectories (default: enabled).",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_false",
        dest="recursive",
        help="Disable directory recursion.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--rule",
        action="append",
        default=None,
        metavar="RULE_ID",
        help=("Limit the report to the specified rule ID.  " "Repeat the flag to keep several rules."),
    )
    parser.add_argument(
        "--config",
        default=None,
        metavar="PATH",
        help=(
            "Path to a config file.  When omitted, Errongreat looks for "
            "errongreat.ini / errongreat.cfg / pyproject.toml in the "
            "current working directory."
        ),
    )
    parser.add_argument(
        "--select",
        action="append",
        default=None,
        metavar="RULE_ID",
        help=(
            "Rule IDs to enable.  Overrides the ``select`` value from the "
            "config file when supplied; repeat to enable several rules."
        ),
    )
    parser.add_argument(
        "--ignore",
        action="append",
        default=None,
        metavar="RULE_ID",
        help=(
            "Rule IDs to disable.  Overrides the ``ignore`` value from the "
            "config file when supplied; repeat to disable several rules."
        ),
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=None,
        metavar="PATTERN",
        help=(
            "Glob pattern to skip during directory scans.  Replaces the "
            "config-file ``exclude`` list when supplied; repeat to add "
            "more patterns."
        ),
    )
    parser.add_argument(
        "--extend-exclude",
        action="append",
        default=None,
        metavar="PATTERN",
        help=("Glob pattern to append to the config-file ``exclude`` list.  " "Repeat to add several patterns."),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress the summary line emitted when no violations are found.",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help=("Print the resolved `Config` (after applying all CLI " "overrides) and exit without scanning."),
    )
    return parser


def _format_text(violations: Sequence[Violation], target: str) -> str:
    """Render *violations* in the human-readable text format."""
    if not violations:
        return f"{target}: no violations"
    return "\n".join(v.format() for v in violations)


def _format_json(violations: Sequence[Violation]) -> str:
    """Render *violations* as a pretty-printed JSON array."""
    payload = [asdict(v) for v in violations]
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _filter_by_rules(
    violations: Sequence[Violation],
    requested: Union[Sequence[str], None],
) -> list[Violation]:
    """Filter *violations* by *requested* rule IDs.

    Unknown rule IDs are silently ignored so that shell pipelines can
    pass through user-supplied filters without crashing the CLI.
    """
    if not requested:
        return list(violations)
    wanted = set(requested)
    return [v for v in violations if v.rule_id in wanted]


def _resolve_config(args: argparse.Namespace) -> Config:
    """Load the config file from disk and merge every CLI override on top."""
    config = load_config(args.config)

    # ``--select`` / ``--ignore`` / ``--exclude`` *replace* the file values
    # wholesale (this is the same semantics as ``--select`` in Ruff).
    # ``--extend-exclude`` *appends* to the file-driven list.  Each branch
    # calls ``merged_with`` independently so that the type checker keeps
    # the precise ``Iterable[str]`` shape of every parameter.
    if args.select is not None:
        select = [token.strip() for token in args.select if token.strip()]
        config = config.merged_with(select=select)
    if args.ignore is not None:
        ignore = [token.strip() for token in args.ignore if token.strip()]
        config = config.merged_with(ignore=ignore)
    if args.exclude is not None:
        exclude = [token.strip() for token in args.exclude if token.strip()]
        config = config.merged_with(exclude=exclude)
    if args.extend_exclude:
        extra = tuple(token.strip() for token in args.extend_exclude if token.strip())
        config = config.merged_with(extend_exclude=config.extend_exclude + extra)
    return config


def _format_config(config: Config) -> str:
    """Render *config* as a human-readable multi-line string."""
    lines = [
        f"source_path    = {config.source_path or '<defaults>'}",
        f"select         = {','.join(sorted(config.select))}",
        f"ignore         = {','.join(sorted(config.ignore))}",
        f"enabled_rules  = {','.join(sorted(config.enabled_rules))}",
        f"exclude        = {','.join(config.exclude) if config.exclude else '<none>'}",
        f"extend_exclude = {','.join(config.extend_exclude) if config.extend_exclude else '<none>'}",
    ]
    if config.per_file_ignores:
        lines.append("per-file-ignores:")
        for pattern in sorted(config.per_file_ignores):
            rules = ",".join(sorted(config.per_file_ignores[pattern]))
            lines.append(f"  {pattern}: {rules}")
    else:
        lines.append("per-file-ignores = <none>")
    return "\n".join(lines)


def main(argv: Union[Sequence[str], None] = None) -> int:
    """Entry point for ``python -m _errortools.errongreat``.

    Args:
        argv: Optional sequence of command-line arguments.  When
            ``None`` (the default), :data:`sys.argv` is consulted.

    Returns:
        ``0`` when no violations match the filter, ``1`` when at least
        one violation is reported, and ``2`` when an internal error
        surfaces to the CLI.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        config = _resolve_config(args)

        if args.show_config:
            print(_format_config(config))
            return 0

        if args.path is None:
            parser.error("the following arguments are required: path")
            return 2

        violations = scan_path(args.path, recursive=args.recursive, config=config)
        violations = _filter_by_rules(violations, args.rule)
        if args.format == "json":
            print(_format_json(violations))
        else:
            print(_format_text(violations, args.path))
            if violations:
                count_by_rule: dict[str, int] = {}
                for v in violations:
                    count_by_rule[v.rule_id] = count_by_rule.get(v.rule_id, 0) + 1
                summary = ", ".join(f"{rule}={count_by_rule[rule]}" for rule in sorted(count_by_rule))
                print(
                    f"\n{args.path}: {len(violations)} violation(s) — {summary}",
                    file=sys.stderr,
                )
        return 1 if violations else 0
    except FileNotFoundError as exc:
        sys.stderr.write(f"errongreat: {exc}\n")
        return 2
    except Exception as exc:  # pragma: no cover - defensive
        sys.stderr.write(f"errongreat: unexpected error: {exc!r}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
