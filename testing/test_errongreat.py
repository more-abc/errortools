"""Tests for the ``errongreat`` static scanner and CLI tool.

This suite exercises every public symbol exported by
``_errortools.errongreat``:

* :class:`~_errortools.errongreat.Violation` (frozen dataclass)
* :data:`~_errortools.errongreat.RULE_IDS` and the ``R00X`` constants
* :func:`~_errortools.errongreat.scan_source`, :func:`scan_file`, :func:`scan_path`
* :class:`~_errortools.errongreat.Config` and :func:`load_config`
* the CLI entry point :func:`main`

Static source fixtures used by the suite live under
``testing/data/errongreat/`` and are exercised both directly via
``scan_path`` and via the CLI ``main`` entry point with synthesized
``argv`` sequences.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from _errortools import errongreat
from _errortools.errongreat import (
    Config,
    RULE_IDS,
    Violation,
    load_config,
    main,
    scan_file,
    scan_path,
    scan_source,
)

DATA_DIR = pathlib.Path(__file__).parent / "data" / "errongreat"


def _source(name: str) -> str:
    return (DATA_DIR / name).read_text(encoding="utf-8")


def _violations(names):
    out = []
    for name in names:
        out.extend(scan_source(_source(name), file_path=name))
    return out


def _by_rule(violations, rule_id):
    return [v for v in violations if v.rule_id == rule_id]


# =============================================================================
# Public constants & dataclass basics
# =============================================================================


class TestRuleIds:
    def test_rule_ids_tuple_is_frozen(self):
        assert isinstance(RULE_IDS, tuple)
        assert set(RULE_IDS) == {"R001", "R002", "R003"}

    def test_each_constant_is_a_string(self):
        for name in (
            "R001_NO_DIRECT_LOGGER_ERROR_WARNING",
            "R002_NO_BARE_OR_TOO_BROAD_EXCEPT",
            "R003_NO_SILENT_EXCEPT",
        ):
            value = getattr(errongreat, name)
            assert isinstance(value, str)
            assert value.startswith("R0")

    def test_module_exports_expected_names(self):
        for name in (
            "Violation",
            "RULE_IDS",
            "R001_NO_DIRECT_LOGGER_ERROR_WARNING",
            "R002_NO_BARE_OR_TOO_BROAD_EXCEPT",
            "R003_NO_SILENT_EXCEPT",
            "scan_source",
            "scan_file",
            "scan_path",
            "main",
        ):
            assert name in errongreat.__all__, name
            assert hasattr(errongreat, name), name


class TestViolationDataclass:
    def test_fields_round_trip(self):
        v = Violation(
            file="x.py",
            line=1,
            col=0,
            rule_id="R001",
            rule_name="no-direct-logger-error-warning",
            message="bad",
        )
        assert v.file == "x.py"
        assert v.line == 1
        assert v.col == 0
        assert v.rule_id == "R001"
        assert v.rule_name == "no-direct-logger-error-warning"
        assert v.message == "bad"

    def test_frozen(self):
        v = Violation(file="x.py", line=1, col=0, rule_id="R001", rule_name="r", message="m")
        with pytest.raises((AttributeError, Exception)):
            v.line = 999  # type: ignore[misc]

    def test_format_renders_location_and_rule(self):
        v = Violation(file="x.py", line=42, col=7, rule_id="R001", rule_name="r", message="bad")
        rendered = v.format()
        assert "x.py:42:7:" in rendered
        assert "R001" in rendered
        assert "bad" in rendered

    def test_dataclass_equality(self):
        v1 = Violation(file="x.py", line=1, col=0, rule_id="R001", rule_name="r", message="m")
        v2 = Violation(file="x.py", line=1, col=0, rule_id="R001", rule_name="r", message="m")
        assert v1 == v2

    def test_dataclass_hashable(self):
        v = Violation(file="x.py", line=1, col=0, rule_id="R001", rule_name="r", message="m")
        # frozen dataclasses are hashable by default
        assert hash(v) == hash(
            Violation(
                file="x.py",
                line=1,
                col=0,
                rule_id="R001",
                rule_name="r",
                message="m",
            )
        )


# =============================================================================
# scan_source — happy paths & syntax-error fallback
# =============================================================================


class TestScanSourceHappyPaths:
    def test_clean_source_returns_nothing(self):
        violations = scan_source(_source("clean.py"), file_path="clean.py")
        assert violations == []

    def test_unknown_file_label_does_not_crash(self):
        violations = scan_source("x = 1\n", file_path="<string>")
        assert violations == []

    def test_empty_source_returns_nothing(self):
        violations = scan_source("", file_path="<empty>")
        assert violations == []

    def test_results_sorted_by_line_col_rule(self):
        # Three distinct violations on three distinct lines so the sort
        # is unambiguous.  The first ``except`` handler is NOT silent
        # because it calls ``print``; only the second except block,
        # with a bare ``return``, counts as silent (R003).
        src = (
            "def f(logger):\n"  # 1
            "    logger.error('a')\n"  # 2 - R001
            "    try:\n"  # 3
            "        risky()\n"  # 4
            "    except Exception:\n"  # 5 - R002
            "        print('noisy')\n"  # 6 - prevents R003 on this handler
            "    try:\n"  # 7
            "        risky()\n"  # 8
            "    except ValueError:\n"  # 9 - R003 (silent handler)
            "        return None\n"  # 10
        )
        v = scan_source(src)
        lines = [x.line for x in v]
        assert lines == [2, 5, 9]
        assert [x.rule_id for x in v] == ["R001", "R002", "R003"]
        # The trio is sorted by ascending line number, which is the
        # contract the rest of the test-suite relies on.
        assert lines == sorted(lines)


class TestScanSourceSyntaxError:
    def test_syntax_error_surfaces_as_r000(self):
        v = scan_source(_source("syntax_error.py"), file_path="syntax_error.py")
        assert len(v) == 1
        assert v[0].rule_id == "R000"
        assert v[0].rule_name == "syntax-error"
        assert v[0].file == "syntax_error.py"

    def test_syntax_error_message_mentions_error_kind(self):
        v = scan_source(_source("syntax_error.py"), file_path="syntax_error.py")
        assert "SyntaxError" in v[0].message


# =============================================================================
# R001 — direct logger.error / logger.warning
# =============================================================================


class TestRuleR001:
    def test_direct_logger_error_is_flagged(self):
        v = scan_source(_source("r001_logger_error.py"))
        rules = _by_rule(v, "R001")
        assert len(rules) >= 2
        for violation in rules:
            assert "Direct call" in violation.message
            assert "logger.error" in violation.message

    def test_direct_logger_warning_is_flagged(self):
        v = scan_source(_source("r001_logger_warning.py"))
        rules = _by_rule(v, "R001")
        assert len(rules) == 1
        assert "logger.warning" in rules[0].message

    def test_logger_warn_alias_is_not_flagged(self):
        v = scan_source(_source("r001_logger_warning.py"))
        # ``logger.warn(...)`` is NOT in the forbidden attribute set
        # (``{"error", "warning"}``) so it must never trigger R001.  Use
        # the parenthesised form to avoid matching ``logger.warning``.
        rule_ids = {x.rule_id for x in v}
        assert rule_ids == {"R001"}
        for violation in v:
            assert "logger.warn(" not in violation.message
            # Only the error/warning methods show up as forbidden.
            assert "logger.error(" in violation.message or "logger.warning(" in violation.message

    def test_self_logger_is_not_flagged(self):
        v = scan_source(_source("r001_non_logger.py"))
        r001 = _by_rule(v, "R001")
        assert r001 == []

    def test_module_logging_call_is_not_flagged(self):
        v = scan_source(_source("r001_non_logger.py"))
        r001 = _by_rule(v, "R001")
        assert r001 == []

    def test_uppercase_logger_name_is_not_flagged(self):
        v = scan_source(_source("r001_non_logger.py"))
        r001 = _by_rule(v, "R001")
        assert r001 == []

    def test_line_and_col_reported(self):
        v = scan_source(_source("r001_logger_error.py"))
        for violation in v:
            assert violation.line > 0
            assert violation.col >= 0


# =============================================================================
# R002 — bare except / Exception / BaseException
# =============================================================================


class TestRuleR002:
    def test_bare_except_is_flagged(self):
        v = scan_source(_source("r002_bare_except.py"))
        r002 = _by_rule(v, "R002")
        assert len(r002) >= 1
        for violation in r002:
            assert "Bare `except:`" in violation.message

    def test_exception_and_baseexception_named_are_flagged(self):
        v = scan_source(_source("r002_exception_named.py"))
        r002 = _by_rule(v, "R002")
        rule_lines = sorted(x.line for x in r002)
        assert rule_lines == [7, 14, 21]

    def test_specific_exception_is_not_flagged(self):
        v = scan_source(_source("r002_exception_named.py"))
        for violation in v:
            if violation.rule_id == "R002":
                # Either the violation is for the tuple line that
                # mentions ``Exception,`` alongside ``ValueError``, or
                # it never mentions ``ValueError`` at all.
                assert "ValueError" not in violation.message or "Exception," in violation.message

    def test_tuple_with_broad_exc_flagged(self):
        v = scan_source(_source("r002_exception_named.py"))
        r002 = _by_rule(v, "R002")
        # The fixture's tuple line is ``except (Exception, ValueError):``
        # which lives at source line 21.
        tuple_violations = [x for x in r002 if x.line == 21]
        assert len(tuple_violations) >= 1

    def test_module_attribute_exception_is_flagged(self):
        v = scan_source(_source("r002_attribute_type.py"))
        r002 = _by_rule(v, "R002")
        assert len(r002) == 2
        assert any("Exception" in x.message for x in r002)

    def test_module_attribute_specific_not_flagged(self):
        v = scan_source(_source("r002_attribute_type.py"))
        for violation in v:
            if violation.rule_id == "R002":
                assert "ValueError" not in violation.message


# =============================================================================
# R003 — silent except
# =============================================================================


class TestRuleR003:
    def test_pass_is_silent(self):
        v = scan_source(_source("r003_silent_except.py"))
        r003 = _by_rule(v, "R003")
        assert len(r003) >= 1
        assert any(x.line == 7 for x in r003)  # silent_pass (except line)

    def test_return_only_is_silent(self):
        v = scan_source(_source("r003_silent_except.py"))
        r003 = _by_rule(v, "R003")
        assert any(x.line == 14 for x in r003)

    def test_ellipsis_is_silent(self):
        v = scan_source(_source("r003_silent_except.py"))
        r003 = _by_rule(v, "R003")
        assert any(x.line == 21 for x in r003)

    def test_raise_is_not_silent(self):
        v = scan_source(_source("r003_silent_except.py"))
        r003 = _by_rule(v, "R003")
        for violation in r003:
            assert violation.line != 27  # not_silent_raise

    def test_print_is_not_silent(self):
        v = scan_source(_source("r003_silent_except.py"))
        r003 = _by_rule(v, "R003")
        for violation in r003:
            assert violation.line != 34  # not_silent_print

    def test_logger_call_inside_except_is_not_silent(self):
        v = scan_source(_source("r003_silent_except.py"))
        r003 = _by_rule(v, "R003")
        for violation in r003:
            assert violation.line != 41  # not_silent_logger_method

    def test_nested_function_def_is_still_silent(self):
        # The helper function's body is its own scope — the outer
        # ``except`` must still be flagged as silent.
        v = scan_source(_source("r003_silent_except.py"))
        r003 = _by_rule(v, "R003")
        # nested_def_does_not_save contains ``try / except ValueError:``
        # whose handler body is a FunctionDef followed by a function call.
        # No Raise / log / print at the handler's own level → R003 fires.
        # The outer ``try`` line does not show in violation output because
        # R003 reports the line of the ``except`` keyword.
        assert any(x.line == 49 for x in r003)


# =============================================================================
# All rules at once
# =============================================================================


class TestAllRulesTrigger:
    def test_every_rule_fires(self):
        v = scan_source(_source("all_three.py"))
        assert _by_rule(v, "R001")
        assert _by_rule(v, "R002")
        assert _by_rule(v, "R003")

    def test_violations_are_sorted(self):
        v = scan_source(_source("all_three.py"))
        assert [x.line for x in v] == sorted(x.line for x in v)


# =============================================================================
# Ignore directives — bare / scoped / standalone / try
# =============================================================================


class TestIgnoreDirectives:
    def test_bare_directive_silences_all(self):
        v = scan_source(_source("ignore_bare.py"))
        # Every function in the fixture has either a bare or scoped
        # ``# eg: ignore`` directive; the scanner should emit zero
        # violations.
        assert v == []

    def test_short_alias_works(self):
        v = scan_source(_source("ignore_bare.py"))
        assert v == []

    def test_typo_alias_works(self):
        v = scan_source(_source("ignore_bare.py"))
        assert v == []

    def test_scoped_directive_only_silences_listed_rules(self):
        v = scan_source(_source("ignore_scoped.py"))
        # First function is scoped to ``[R001]``; it still has an
        # ``except Exception: pass`` (line 9) that fires R002 and R003.
        assert any(x.line == 9 for x in _by_rule(v, "R002"))
        assert any(x.line == 9 for x in _by_rule(v, "R003"))
        # Only the ungoverned ``scoped_then_bare`` at the bottom of
        # the file should ever produce an R001 violation (and even that
        # one is silenced by ``# eg: ignore`` — not scoped to R001,
        # but bare, so it suppresses R001 too).
        r001 = _by_rule(v, "R001")
        # The two ``logger.error`` calls in ``r001_only_disabled``
        # (lines 5 and 6) must never appear in the result set.
        for violation in r001:
            assert violation.line not in (5, 6)

    def test_empty_scope_is_a_no_op(self):
        v = scan_source(_source("ignore_no_op.py"))
        r001 = _by_rule(v, "R001")
        r002 = _by_rule(v, "R002")
        # The ``logger.error`` call in ``empty_scope_does_not_save``
        # sits on source line 5; with the empty ``[R001]`` scope
        # it stays flagged.
        assert any(x.line == 5 for x in r001)
        # The matching ``except Exception:`` on line 8 is ungoverned
        # by an ignore directive and must remain flagged.
        assert any(x.line == 8 for x in r002)

    def test_standalone_directive_above_try_silences_handler(self):
        v = scan_source(_source("with_ignore_directive_above_try.py"))
        assert _by_rule(v, "R002") == []
        assert _by_rule(v, "R003") == []


# =============================================================================
# scan_file — disk I/O failures
# =============================================================================


class TestScanFile:
    def test_scan_real_file(self):
        path = DATA_DIR / "all_three.py"
        v = scan_file(path)
        assert len(v) >= 3

    def test_scan_accepts_string_path(self):
        path = str(DATA_DIR / "all_three.py")
        v = scan_file(path)
        assert len(v) >= 3

    def test_scan_missing_file_returns_infrastructure_finding(self, capsys):
        missing = DATA_DIR / "does_not_exist_zzz.py"
        v = scan_file(missing)
        assert len(v) == 1
        assert v[0].rule_id == "R000"
        assert v[0].rule_name == "file-read-error"
        # an explanatory line is printed to stderr
        err = capsys.readouterr().err
        assert "errongreat:" in err

    def test_scan_non_utf8_file_reports_decode_error(self, tmp_path):
        bad = tmp_path / "bad_encoding.py"
        bad.write_bytes(b"\xff\xfe\x00not-utf8")
        v = scan_file(bad)
        assert len(v) == 1
        assert v[0].rule_id == "R000"
        assert v[0].rule_name == "file-read-error"
        assert "decode" in v[0].message.lower() or "utf-8" in v[0].message.lower()


# =============================================================================
# scan_path — recursion, exclusion, per-file rules
# =============================================================================


class TestScanPath:
    def test_scan_path_directory_recursive_default(self):
        v = scan_path(DATA_DIR)
        # Every rule must have fired across the fixture directory.
        assert _by_rule(v, "R001")
        assert _by_rule(v, "R002")
        assert _by_rule(v, "R003")

    def test_scan_path_non_recursive_does_not_descend(self):
        v = scan_path(DATA_DIR, recursive=False)
        # The nested file is skipped; this still finds violations but
        # importantly the deep path must not appear.
        files = {x.file for x in v}
        assert not any("nested" in f for f in files)

    def test_scan_path_on_a_single_file(self):
        v = scan_path(DATA_DIR / "clean.py")
        assert v == []

    def test_scan_path_missing_reports_path_not_found(self):
        v = scan_path(DATA_DIR / "definitely_not_here_xxx")
        assert len(v) == 1
        assert v[0].rule_name == "path-not-found"

    def test_scan_path_respects_exclude(self):
        # A pattern that matches every file in the dataset's basename.
        cfg = Config(exclude=("*.py",))
        v = scan_path(DATA_DIR, config=cfg)
        assert v == []

    def test_scan_path_respects_per_file_ignores(self, tmp_path):
        # Create a one-off file that violates R001; then exclude only R001
        # for that file via per_file_ignores.
        target = tmp_path / "target.py"
        target.write_text("def f(logger):\n    logger.error('boom')\n", encoding="utf-8")
        cfg = Config(per_file_ignores={str(target): frozenset({"R001"})})
        v = scan_path(target, config=cfg)
        assert _by_rule(v, "R001") == []
        # Other rules untouched.
        for violation in v:
            assert violation.rule_id != "R001"

    def test_scan_path_results_sorted_by_file_then_line(self):
        v = scan_path(DATA_DIR)
        keys = [(x.file, x.line, x.col, x.rule_id) for x in v]
        assert keys == sorted(keys)


# =============================================================================
# Config dataclass
# =============================================================================


class TestConfigDataclass:
    def test_default_config_enables_all_rules(self):
        cfg = Config()
        assert cfg.enabled_rules == frozenset(RULE_IDS)
        assert cfg.ignore == frozenset()
        assert cfg.exclude == ()
        assert cfg.extend_exclude == ()
        assert cfg.per_file_ignores == {}
        assert cfg.source_path is None

    def test_all_excludes_combines_lists(self):
        cfg = Config(exclude=("a", "b"), extend_exclude=("c",))
        assert cfg.all_excludes == ("a", "b", "c")

    def test_enabled_rules_subtracts_ignore(self):
        cfg = Config(ignore=frozenset({"R001"}))
        assert "R001" not in cfg.enabled_rules
        assert cfg.enabled_rules == frozenset({"R002", "R003"})

    def test_enabled_rules_for_subtracts_per_file(self):
        cfg = Config(per_file_ignores={"tests/legacy.py": frozenset({"R003"})})
        assert cfg.enabled_rules_for("tests/legacy.py") == frozenset({"R001", "R002"})
        assert cfg.enabled_rules_for("tests/modern.py") == cfg.enabled_rules

    def test_is_excluded_matches_basename(self):
        cfg = Config(exclude=("legacy.py",))
        assert cfg.is_excluded("/path/to/legacy.py")
        assert cfg.is_excluded("anywhere/legacy.py")
        assert not cfg.is_excluded("anywhere/clean.py")

    def test_merged_with_replaces_supplied_fields(self):
        original = Config(
            select=frozenset({"R001"}),
            ignore=frozenset(),
            exclude=("a",),
            extend_exclude=("b",),
        )
        merged = original.merged_with(
            select=("R002",),
            ignore=("R001",),
            exclude=("c",),
            extend_exclude=("d",),
        )
        assert merged.select == frozenset({"R002"})
        assert merged.ignore == frozenset({"R001"})
        assert merged.exclude == ("c",)
        assert merged.extend_exclude == ("d",)
        # per_file_ignores & source_path are preserved.
        assert merged.per_file_ignores == original.per_file_ignores
        assert merged.source_path == original.source_path

    def test_merged_with_omitted_fields_are_preserved(self):
        original = Config(select=frozenset({"R001"}), ignore=frozenset({"R003"}))
        merged = original.merged_with(select=("R002",))
        # ``ignore`` was not supplied — keep the original.
        assert merged.ignore == frozenset({"R003"})
        assert merged.select == frozenset({"R002"})


# =============================================================================
# Config discovery & parsers
# =============================================================================


class TestLoadConfigDefaults:
    def test_no_files_in_empty_dir_returns_defaults(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = load_config()
        assert cfg.source_path is None
        assert cfg.enabled_rules == frozenset(RULE_IDS)

    def test_explicit_missing_path_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_config(tmp_path / "missing.ini")


class TestLoadConfigIni:
    def test_loads_ini_with_full_settings(self, monkeypatch):
        monkeypatch.chdir(DATA_DIR / "cfg")
        cfg = load_config("errongreat.ini")
        assert cfg.source_path is not None
        assert cfg.source_path.endswith("errongreat.ini")
        assert cfg.select == frozenset({"R001", "R003"})
        assert cfg.exclude == ("tmp/*", "build/*")
        assert cfg.extend_exclude == ("*.tmp",)
        assert cfg.per_file_ignores == {
            "tests/legacy.py": frozenset({"R003"}),
            "*ignore_me.py": frozenset({"R001", "R002"}),
        }

    def test_loads_cfg_with_simple_select(self, monkeypatch):
        monkeypatch.chdir(DATA_DIR / "cfg")
        cfg = load_config("errongreat.cfg")
        assert cfg.select == frozenset({"R002"})
        assert cfg.extend_exclude == ("*_legacy.py",)

    def test_unknown_extension_falls_back_to_ini_parser(self, tmp_path):
        custom = tmp_path / "errongreat.weird"
        custom.write_text(
            "[errongreat]\nselect = R001\n",
            encoding="utf-8",
        )
        cfg = load_config(custom)
        assert cfg.select == frozenset({"R001"})

    def test_search_dirs_overrides_cwd(self, tmp_path):
        shutil_dir = tmp_path / "conf_area"
        shutil_dir.mkdir()
        ini = shutil_dir / "errongreat.ini"
        ini.write_text("[errongreat]\nselect = R001\n", encoding="utf-8")
        cfg = load_config(search_dirs=[shutil_dir])
        assert cfg.select == frozenset({"R001"})

    def test_search_dirs_returns_default_when_empty(self, tmp_path):
        cfg = load_config(search_dirs=[tmp_path])
        assert cfg.source_path is None

    def test_unknown_extension_with_ini_content_parses_as_ini(self, tmp_path):
        bad = tmp_path / "errongreat.weird"
        bad.write_text("[errongreat]\nselect = R001\n", encoding="utf-8")
        # The dispatcher falls back to the INI parser for unknown
        # extensions rather than rejecting them outright.
        cfg = load_config(bad)
        assert cfg.select == frozenset({"R001"})


class TestLoadConfigToml:
    def test_loads_pyproject_toml_section(self, monkeypatch):
        monkeypatch.chdir(DATA_DIR / "cfg")
        cfg = load_config("pyproject.toml")
        assert cfg.source_path is not None
        assert cfg.source_path.endswith("pyproject.toml")
        assert cfg.select == frozenset({"R001", "R002"})
        assert cfg.ignore == frozenset()
        assert cfg.exclude == ("tmp/*",)
        assert cfg.extend_exclude == ("*.bak",)
        assert cfg.per_file_ignores == {
            "tests/legacy.py": frozenset({"R003"}),
            "skip_me.py": frozenset({"R001", "R002"}),
        }

    def test_pyproject_without_section_returns_default(self, monkeypatch, tmp_path):
        project = tmp_path / "pyproject.toml"
        project.write_text("[tool.other]\nkey = 'x'\n", encoding="utf-8")
        cfg = load_config(project)
        assert cfg.source_path == str(project)
        assert cfg.enabled_rules == frozenset(RULE_IDS)


# =============================================================================
# CLI — main()
# =============================================================================


class TestCliMain:
    def test_clean_target_returns_zero(self, capsys):
        rc = main(["--quiet", str(DATA_DIR / "clean.py")])
        captured = capsys.readouterr()
        assert rc == 0
        assert "no violations" in captured.out

    def test_noisy_target_returns_one(self, capsys):
        rc = main(["--quiet", str(DATA_DIR / "all_three.py")])
        assert rc == 1
        captured = capsys.readouterr()
        assert "R001" in captured.out
        assert "R002" in captured.out
        assert "R003" in captured.out

    def test_summary_printed_on_stderr_when_violations_exist(self, capsys):
        main([str(DATA_DIR / "all_three.py")])
        captured = capsys.readouterr()
        assert "violation(s)" in captured.err

    def test_clean_file_emits_no_summary_line(self, capsys):
        # The summary line is gated on ``if violations:`` and never
        # appears on a clean file.  This is the contract independent of
        # the ``--quiet`` flag.
        main(["--quiet", str(DATA_DIR / "clean.py")])
        captured = capsys.readouterr()
        assert "no violations" in captured.out
        assert "violation(s)" not in captured.err

    def test_json_format_outputs_valid_json(self, capsys):
        main(["--format", "json", "--quiet", str(DATA_DIR / "all_three.py")])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert data
        first = data[0]
        for key in ("file", "line", "col", "rule_id", "rule_name", "message"):
            assert key in first

    def test_json_format_on_clean_outputs_empty_list(self, capsys):
        main(["--format", "json", "--quiet", str(DATA_DIR / "clean.py")])
        captured = capsys.readouterr()
        assert json.loads(captured.out) == []

    def test_rule_filter_keeps_only_selected(self, capsys):
        main(
            [
                "--rule",
                "R001",
                "--quiet",
                "--format",
                "json",
                str(DATA_DIR / "all_three.py"),
            ]
        )
        data = json.loads(capsys.readouterr().out)
        assert data
        for entry in data:
            assert entry["rule_id"] == "R001"

    def test_unknown_rule_id_is_silently_ignored(self, capsys):
        rc = main(
            [
                "--rule",
                "R999",
                "--rule",
                "R001",
                "--quiet",
                "--format",
                "json",
                str(DATA_DIR / "all_three.py"),
            ]
        )
        assert rc == 1
        data = json.loads(capsys.readouterr().out)
        assert all(x["rule_id"] == "R001" for x in data)

    def test_select_cli_overrides_config(self, tmp_path, monkeypatch, capsys):
        cfg = tmp_path / "errongreat.ini"
        cfg.write_text("[errongreat]\nselect = R001,R003\n", encoding="utf-8")
        # CLI ``--select`` replaces the file value entirely.
        rc = main(
            [
                "--config",
                str(cfg),
                "--select",
                "R002",
                "--quiet",
                "--format",
                "json",
                str(DATA_DIR / "all_three.py"),
            ]
        )
        data = json.loads(capsys.readouterr().out)
        assert rc == 1
        assert data
        assert all(x["rule_id"] == "R002" for x in data)
        # Original file untouched.
        assert "R001,R003" in cfg.read_text()

    def test_ignore_cli_subtracts_from_rules(self, tmp_path, capsys):
        cfg = tmp_path / "errongreat.ini"
        cfg.write_text("[errongreat]\nselect =\n", encoding="utf-8")
        # By default ``select`` is "all rules". ``--ignore R002`` removes R002.
        rc = main(
            [
                "--config",
                str(cfg),
                "--ignore",
                "R002",
                "--quiet",
                "--format",
                "json",
                str(DATA_DIR / "all_three.py"),
            ]
        )
        data = json.loads(capsys.readouterr().out)
        assert rc == 1
        for entry in data:
            assert entry["rule_id"] != "R002"

    def test_exclude_cli_skips_files(self, tmp_path, capsys):
        cfg = tmp_path / "errongreat.ini"
        cfg.write_text("[errongreat]\nselect =\n", encoding="utf-8")
        rc = main(
            [
                "--config",
                str(cfg),
                "--exclude",
                "*all_three.py",
                "--quiet",
                "--format",
                "json",
                str(DATA_DIR),
            ]
        )
        data = json.loads(capsys.readouterr().out)
        # all_three.py is excluded → no violations for it (but other rules
        # are still on for the rest of the directory).
        for entry in data:
            assert "all_three" not in entry["file"]

    def test_extend_exclude_appends(self, tmp_path, capsys):
        cfg = tmp_path / "errongreat.ini"
        cfg.write_text(
            "[errongreat]\nselect =\nexclude = *r003*\n",
            encoding="utf-8",
        )
        rc = main(
            [
                "--config",
                str(cfg),
                "--extend-exclude",
                "*r002*",
                "--quiet",
                "--format",
                "json",
                str(DATA_DIR),
            ]
        )
        data = json.loads(capsys.readouterr().out)
        for entry in data:
            assert "r002" not in entry["file"]
            assert "r003" not in entry["file"]

    def test_show_config_prints_resolved_config(self, capsys):
        cfg = DATA_DIR / "cfg" / "errongreat.ini"
        rc = main(["--config", str(cfg), "--show-config"])
        captured = capsys.readouterr()
        assert rc == 0
        assert "select" in captured.out
        assert "enabled_rules" in captured.out

    def test_show_config_with_cli_overrides(self, tmp_path, capsys):
        cfg = tmp_path / "errongreat.ini"
        cfg.write_text("[errongreat]\nselect = R001\n", encoding="utf-8")
        rc = main(
            [
                "--config",
                str(cfg),
                "--ignore",
                "R002",
                "--show-config",
            ]
        )
        captured = capsys.readouterr()
        assert rc == 0
        assert "enabled_rules" in captured.out

    def test_no_recursive_skips_nested(self, capsys):
        rc = main(
            [
                "--no-recursive",
                "--quiet",
                "--format",
                "json",
                str(DATA_DIR),
            ]
        )
        data = json.loads(capsys.readouterr().out)
        # non-recursive scan must not descend into ``nested/``.
        for entry in data:
            assert "nested" not in entry["file"]

    def test_recursive_default_includes_nested(self, capsys):
        rc = main(
            [
                "--quiet",
                "--format",
                "json",
                str(DATA_DIR),
            ]
        )
        data = json.loads(capsys.readouterr().out)
        # The default is ``--recursive`` → we DO descend.
        assert any("nested" in entry["file"] for entry in data)

    def test_missing_path_returns_exit_code_one(self, capsys):
        # ``scan_path`` returns a ``path-not-found`` ``Violation``
        # instead of raising FileNotFoundError, so ``main`` exits
        # with 1 (violations present), not 2.
        rc = main([str(DATA_DIR / "totally_missing_xx")])
        assert rc == 1
        captured = capsys.readouterr()
        assert "Path not found" in captured.out or "no violations" in captured.out

    def test_missing_config_returns_exit_code_two(self, tmp_path, capsys):
        # Pointing ``--config`` at a non-existent file is the one path
        # that escalates to ``FileNotFoundError`` and exit code 2.
        rc = main(["--config", str(tmp_path / "absent.ini"), str(DATA_DIR / "clean.py")])
        assert rc == 2
        captured = capsys.readouterr()
        assert "errongreat:" in captured.err

    def test_config_discovery_in_cwd(self, tmp_path, monkeypatch, capsys):
        # Place an errongreat.ini in a temp cwd and ensure the CLI finds it.
        cfg = tmp_path / "errongreat.ini"
        cfg.write_text("[errongreat]\nselect = R001\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        rc = main(
            [
                "--quiet",
                "--format",
                "json",
                str(DATA_DIR / "r001_logger_error.py"),
            ]
        )
        data = json.loads(capsys.readouterr().out)
        assert rc == 1
        # Only R001 is configured → only R001 fires even though other
        # rules could have fired in a separately-defined fixture.
        assert data
        assert all(x["rule_id"] == "R001" for x in data)


# =============================================================================
# CLI — argument parser
# =============================================================================


class TestArgparseBuild:
    def test_help_exits_cleanly(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0

    def test_parse_args_default(self):
        parser = errongreat._build_parser()
        args = parser.parse_args(["somepath"])
        assert args.path == "somepath"
        assert args.recursive is True
        assert args.format == "text"
        assert args.rule is None
        assert args.config is None
        assert args.select is None
        assert args.ignore is None
        assert args.exclude is None
        assert args.extend_exclude is None
        assert args.quiet is False
        assert args.show_config is False

    def test_parse_args_all_flags(self):
        parser = errongreat._build_parser()
        args = parser.parse_args(
            [
                "somepath",
                "--no-recursive",
                "--format",
                "json",
                "--rule",
                "R001",
                "--rule",
                "R002",
                "--config",
                "cfg.ini",
                "--select",
                "R003",
                "--ignore",
                "R001",
                "--exclude",
                "tmp/*",
                "--extend-exclude",
                "*.bak",
                "--quiet",
                "--show-config",
            ]
        )
        assert args.recursive is False
        assert args.format == "json"
        assert args.rule == ["R001", "R002"]
        assert args.config == "cfg.ini"
        assert args.select == ["R003"]
        assert args.ignore == ["R001"]
        assert args.exclude == ["tmp/*"]
        assert args.extend_exclude == ["*.bak"]
        assert args.quiet is True
        assert args.show_config is True


# =============================================================================
# Format helpers
# =============================================================================


class TestFormatHelpers:
    def test_format_text_empty_returns_label(self):
        text = errongreat._format_text([], "src.py")
        assert "src.py" in text
        assert "no violations" in text

    def test_format_text_concatenates_violations(self):
        v = Violation(
            file="src.py",
            line=1,
            col=2,
            rule_id="R001",
            rule_name="r",
            message="m",
        )
        text = errongreat._format_text([v], "src.py")
        assert "R001" in text
        assert "m" in text

    def test_format_json_round_trips(self):
        v = Violation(
            file="src.py",
            line=1,
            col=2,
            rule_id="R001",
            rule_name="r",
            message="m",
        )
        rendered = errongreat._format_json([v])
        data = json.loads(rendered)
        assert data == [
            {
                "file": "src.py",
                "line": 1,
                "col": 2,
                "rule_id": "R001",
                "rule_name": "r",
                "message": "m",
            }
        ]

    def test_format_json_empty_array(self):
        rendered = errongreat._format_json([])
        assert json.loads(rendered) == []

    def test_filter_by_rules_keeps_only_requested(self):
        v1 = Violation(file="x.py", line=1, col=0, rule_id="R001", rule_name="r", message="m")
        v2 = Violation(file="x.py", line=2, col=0, rule_id="R002", rule_name="r", message="m")
        out = errongreat._filter_by_rules([v1, v2], ["R001"])
        assert out == [v1]

    def test_filter_by_rules_returns_all_when_request_is_none(self):
        v1 = Violation(file="x.py", line=1, col=0, rule_id="R001", rule_name="r", message="m")
        v2 = Violation(file="x.py", line=2, col=0, rule_id="R002", rule_name="r", message="m")
        out = errongreat._filter_by_rules([v1, v2], None)
        assert out == [v1, v2]

    def test_filter_by_rules_ignores_unknown_rule_ids(self):
        v = Violation(file="x.py", line=1, col=0, rule_id="R001", rule_name="r", message="m")
        out = errongreat._filter_by_rules([v], ["R999"])
        assert out == []

    def test_format_config_renders_each_field(self, tmp_path):
        cfg = Config(
            select=frozenset({"R001", "R002"}),
            ignore=frozenset({"R003"}),
            exclude=("a.py",),
            extend_exclude=("b.py",),
            per_file_ignores={"x.py": frozenset({"R002"})},
            source_path=str(tmp_path / "c.toml"),
        )
        rendered = errongreat._format_config(cfg)
        assert "select" in rendered
        assert "ignore" in rendered
        assert "enabled_rules" in rendered
        assert "per-file-ignores:" in rendered
        assert "x.py" in rendered

    def test_format_config_with_no_per_file_ignores(self):
        cfg = Config()
        rendered = errongreat._format_config(cfg)
        assert "per-file-ignores = <none>" in rendered


# =============================================================================
# Helper modules — purely internal but tested for robustness
# =============================================================================


class TestParseCsvList:
    def test_empty_input(self):
        assert errongreat._parse_csv_list("") == ()

    def test_strips_whitespace(self):
        assert errongreat._parse_csv_list(" a , b ,c ") == ("a", "b", "c")

    def test_drops_empty_tokens(self):
        out = errongreat._parse_csv_list("a,,b,")
        assert out == ("a", "b")


class TestGlobMatch:
    @pytest.mark.parametrize(
        "pattern,path,expected",
        [
            # ``*.py`` matches a file with the .py extension.
            ("*.py", "foo.py", True),
            # ``*.py`` rejects a non-.py file.
            ("*.py", "foo.txt", False),
            # A bare basename matches a file with the same basename
            # anywhere in its path; the helper also tries the basename
            # form explicitly.
            ("legacy.py", "/anywhere/legacy.py", True),
            ("legacy.py", "/anywhere/clean.py", False),
            # The ``*`` wildcard matches any sequence except ``/``.
            ("foo*bar", "foozbar", True),
            ("foo*bar", "foo/bar", False),
        ],
    )
    def test_glob_match(self, pattern, path, expected):
        assert errongreat._glob_match(pattern, path) is expected


# =============================================================================
# Internal helpers — ignore directive coverage logic
# =============================================================================


class TestCoveredLinesForDirective:
    def test_directive_always_covers_its_own_line(self):
        covered = errongreat._covered_lines_for_directive(10, 11, None)
        assert 10 in covered

    def test_next_code_line_is_covered(self):
        covered = errongreat._covered_lines_for_directive(10, 11, None)
        assert 11 in covered

    def test_handlers_of_try_are_covered(self):
        import ast as _ast

        src = "try:\n    pass\nexcept:\n    pass\nfinally:\n    pass\n"
        tree = _ast.parse(src)
        # The directive sits above the ``try`` line → covers the entire try.
        try_node = tree.body[0]
        assert isinstance(try_node, _ast.Try)
        covered = errongreat._covered_lines_for_directive(1, 2, try_node)
        assert 2 in covered
        for handler in try_node.handlers:
            assert handler.lineno in covered

    def test_unrelated_node_does_not_extend_coverage(self):
        covered = errongreat._covered_lines_for_directive(10, 11, None)
        # Without an ast.Try node, only own + next code line are covered.
        assert covered == frozenset({10, 11})


class TestApplyDirectives:
    def test_no_directives_means_all_violations_passthrough(self):
        v = Violation(file="x.py", line=1, col=0, rule_id="R001", rule_name="r", message="m")
        assert errongreat._apply_directives([v], {}) == [v]

    def test_directive_matching_clears_violation(self):
        v = Violation(file="x.py", line=5, col=0, rule_id="R001", rule_name="r", message="m")
        directives = {4: (frozenset({"*"}), frozenset({4, 5}))}
        assert errongreat._apply_directives([v], directives) == []

    def test_directive_for_different_rule_does_not_clear(self):
        v = Violation(file="x.py", line=5, col=0, rule_id="R001", rule_name="r", message="m")
        directives = {4: (frozenset({"R002"}), frozenset({4, 5}))}
        assert errongreat._apply_directives([v], directives) == [v]

    def test_orphan_directive_keeps_other_violations(self):
        v = Violation(file="x.py", line=99, col=0, rule_id="R001", rule_name="r", message="m")
        directives = {4: (frozenset({"*"}), frozenset({4, 5}))}
        assert errongreat._apply_directives([v], directives) == [v]


# =============================================================================
# Visitor internals — black-box via scan_source
# =============================================================================


class TestVisitorIntegration:
    def test_visitor_types_are_distinct(self):
        # Each visitor must surface its declared rule id.  We confirm
        # this by scanning per-rule fixtures and checking that exactly
        # the expected rule_id appears (and only that one).
        r001 = _violations(["r001_logger_error.py"])
        r002 = _violations(["r002_bare_except.py"])
        r003 = _violations(["r003_silent_except.py"])
        for label, vs, expected in (
            ("r001_logger_error.py", r001, "R001"),
            ("r002_bare_except.py", r002, "R002"),
            ("r003_silent_except.py", r003, "R003"),
        ):
            assert vs, f"{label} produced no violations"
            assert {v.rule_id for v in vs} == {expected}, label

    def test_visitors_are_fresh_per_scan(self):
        # Two consecutive scans must not share visitor state.
        first = scan_source(_source("r001_logger_error.py"))
        second = scan_source(_source("r001_logger_error.py"))
        assert len(first) == len(second)
        for a, b in zip(first, second):
            assert a.file == b.file
            assert a.line == b.line


# =============================================================================
# CLI smoke — basic ``python -m _errortools.errongreat`` scenarios
# =============================================================================


class TestCliSmoke:
    def test_directory_scan_exits_with_code_one(self, capsys):
        rc = main(["--quiet", "--format", "json", str(DATA_DIR)])
        assert rc == 1
        json.loads(capsys.readouterr().out)

    def test_text_format_emits_one_line_per_violation(self, capsys):
        main(["--quiet", str(DATA_DIR / "all_three.py")])
        out_lines = capsys.readouterr().out.strip().splitlines()
        # one line per violation; non-empty because all_three.py is dirty.
        assert out_lines
        for line in out_lines:
            assert ":" in line
            assert "[" in line and "]" in line

    def test_argv_default_uses_sys_argv(self, monkeypatch, capsys):
        # When argv is ``None`` main() consults :data:`sys.argv` directly.
        monkeypatch.setattr("sys.argv", ["errongreat", "--quiet", str(DATA_DIR / "clean.py")])
        rc = main()
        assert rc == 0
