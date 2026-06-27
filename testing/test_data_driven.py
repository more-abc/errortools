"""Data-driven tests powered by JSON fixtures in ``testing/data/``.

These tests load scenarios from the ``testing/data/*.json`` files and exercise
the public errortools API across many input combinations.  Each test class
focuses on a single module so failures clearly point at the affected surface.

Adding new scenarios is as simple as appending entries to the relevant JSON
file — no test code changes are required.
"""

import asyncio
import builtins
import sys
import warnings

import pytest

from testing.data.json import loader

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_warning_category(name):
    """Look up a :class:`Warning` subclass by name.

    Warning categories live in :mod:`builtins` (``UserWarning``, etc.), not in
    :mod:`warnings`.  Fall back to the ``warnings`` module for completeness.
    """
    category = getattr(builtins, name, None)
    if isinstance(category, type) and issubclass(category, Warning):
        return category
    category = getattr(warnings, name, None)
    if isinstance(category, type) and issubclass(category, Warning):
        return category
    raise LookupError(f"Unknown warning category: {name!r}")


# ============================================================================
# errno
# ============================================================================


class TestErrnoDataDriven:
    """Verify ``get_errno_name`` / ``is_valid_errno`` against a table of codes."""

    @pytest.mark.parametrize("case", loader.errno_cases(), ids=lambda c: c["name"])
    def test_valid_code_resolves_to_name(self, case):
        code = case["code"]
        expected_name = case["name"]
        if sys.platform == "linux" and expected_name == "EILSEQ" and code == 42:
            pytest.skip("EILSEQ code mismatch on Linux platform")
        from _errortools.errno import get_errno_name, is_valid_errno

        assert get_errno_name(code) == expected_name
        assert is_valid_errno(code) is True

    @pytest.mark.parametrize("case", loader.errno_cases(), ids=lambda c: c["name"])
    def test_valid_code_message_is_non_empty(self, case):
        from _errortools.errno import get_errno_message

        message = get_errno_message(case["code"])
        assert isinstance(message, str)
        assert len(message) > 0

    @pytest.mark.parametrize("code", loader.errno_invalid_codes())
    def test_invalid_code_has_no_name(self, code):
        from _errortools.errno import get_errno_name, is_valid_errno

        assert get_errno_name(code) is None
        assert is_valid_errno(code) is False

    @pytest.mark.parametrize("code", loader.errno_invalid_codes())
    def test_invalid_code_message_raises_value_error(self, code):
        from _errortools.errno import get_errno_message

        with pytest.raises(ValueError):
            get_errno_message(code)


# ============================================================================
# raises / raises_all / assert_raises
# ============================================================================


class TestRaisesDataDriven:
    """Verify ``raises`` against a table of (type, message) specs."""

    @pytest.mark.parametrize(
        "spec",
        loader.single_error_specs(),
        ids=lambda s: f"{s['type']}:{s['message']}",
    )
    def test_raises_expected_type_and_message(self, spec):
        from _errortools.raises import raises

        exc_type = loader._resolve_type(spec["type"])
        with pytest.raises(exc_type, match=spec["message"]):
            raises([exc_type], [spec["message"]])

    @pytest.mark.parametrize(
        "spec",
        loader.multi_error_specs(),
        ids=lambda s: f"{len(s['errors'])}x{len(s['messages'])}",
    )
    @pytest.mark.skipif(sys.version_info < (3, 11), reason="requires ExceptionGroup")
    def test_raises_all_cartesian_product(self, spec):
        from _errortools.raises import raises_all

        errors = [loader._resolve_type(n) for n in spec["errors"]]
        with pytest.raises(ExceptionGroup) as exc_info:
            raises_all(errors, spec["messages"])
        assert len(exc_info.value.exceptions) == spec["expected_count"]

    @pytest.mark.parametrize(
        "spec",
        loader.custom_baseerror_specs(),
        ids=lambda s: f"{s['type']}<:{s['baseerror']}",
    )
    def test_raises_baseerror_validation(self, spec):
        from _errortools.raises import raises

        exc_type = loader._resolve_type(spec["type"])
        base_type = loader._resolve_type(spec["baseerror"])

        if spec["should_raise"]:
            with pytest.raises(exc_type, match=spec["message"]):
                raises([exc_type], [spec["message"]], baseerror=base_type)
        else:
            with pytest.raises(TypeError):
                raises([exc_type], [spec["message"]], baseerror=base_type)

    @pytest.mark.parametrize(
        "spec",
        loader.empty_input_specs(),
        ids=lambda s: f"errs={len(s['errors'])}msgs={len(s['messages'])}",
    )
    def test_empty_inputs_do_not_raise(self, spec):
        from _errortools.raises import raises, raises_all

        errors = [loader._resolve_type(n) for n in spec["errors"]] if spec["errors"] else []
        # raises() should silently return
        raises(errors, spec["messages"])

        if sys.version_info >= (3, 11):
            # raises_all() should also silently return
            raises_all(errors, spec["messages"])


# ============================================================================
# @suppress decorator
# ============================================================================


def _build_operation(operation, args):
    """Run the configured operation for a @suppress case."""
    if operation == "divide":
        return args[0] / args[1]
    if operation == "dict_lookup":
        return args[0][args[1]]
    if operation == "int_parse":
        return int(args[0])
    if operation == "list_index":
        return args[0][args[1]]
    if operation == "open_file":
        return open(args[0]).read()  # noqa: SIM115
    if operation == "raise_value":
        raise ValueError(args[0] if args else "raised")
    raise AssertionError(f"Unknown operation: {operation}")


class TestSuppressDataDriven:
    """Verify the @suppress decorator against a table of scenarios."""

    @pytest.mark.parametrize("case", loader.suppress_cases(), ids=lambda c: c["name"])
    def test_suppress_returns_default(self, case):
        from _errortools.decorator.handlers import suppress

        exc_type = loader._resolve_type(case["exception_type"])
        default = case["default"]

        @suppress(exc_type, default=default)
        def op(*args):
            return _build_operation(case["operation"], list(args))

        result = op(*case["args"])
        assert result == case["expected"]


# ============================================================================
# ignore / fast_ignore / ignore_subclass
# ============================================================================


class TestIgnoreDataDriven:
    """Verify ignore/fast_ignore against a table of scenarios."""

    @pytest.mark.parametrize(
        "case",
        loader.ignore_suppress_cases(),
        ids=lambda c: f"+{','.join(c['types'])}|{c['raise']}",
    )
    def test_ignore_suppresses(self, case):
        from _errortools.ignore import ignore, fast_ignore

        types = tuple(loader._resolve_type(t) for t in case["types"])
        exc = loader.make_exception(case["raise"])

        with ignore(*types):
            raise exc
        with fast_ignore(*types):  # type: ignore[arg-type]
            raise exc

    @pytest.mark.parametrize(
        "case",
        loader.ignore_propagate_cases(),
        ids=lambda c: f"+{','.join(c['types'])}|{c['raise']}",
    )
    def test_ignore_propagates_unrelated(self, case):
        from _errortools.ignore import ignore, fast_ignore

        types = tuple(loader._resolve_type(t) for t in case["types"])
        expected = loader._resolve_type(case["expected"])
        exc = loader.make_exception(case["raise"])

        with pytest.raises(expected):
            with ignore(*types):
                raise exc
        with pytest.raises(expected):
            with fast_ignore(*types):  # type: ignore[arg-type]
                raise exc

    @pytest.mark.parametrize(
        "case",
        loader.ignore_subclass_cases(),
        ids=lambda c: f"<:{c['base']}|{c['raise']}",
    )
    def test_ignore_subclass_suppresses(self, case):
        from _errortools.ignore import ignore_subclass

        base = loader._resolve_type(case["base"])
        exc = loader.make_exception(case["raise"])

        with ignore_subclass(base):
            raise exc

    @pytest.mark.parametrize(
        "case",
        loader.ignore_subclass_propagates(),
        ids=lambda c: f"<:{c['base']}|{c['raise']}",
    )
    def test_ignore_subclass_propagates(self, case):
        from _errortools.ignore import ignore_subclass

        base = loader._resolve_type(case["base"])
        expected = loader._resolve_type(case["expected"])
        exc = loader.make_exception(case["raise"])

        with pytest.raises(expected):
            with ignore_subclass(base):
                raise exc


# ============================================================================
# ignore_warns
# ============================================================================


class TestIgnoreWarnsDataDriven:
    """Verify ignore_warns against a table of warning scenarios."""

    @pytest.mark.parametrize(
        "case",
        loader.warning_single_cases(),
        ids=lambda c: c["category"],
    )
    def test_ignore_warns_single(self, case):
        from _errortools.ignore import ignore_warns

        category = _resolve_warning_category(case["category"])
        with ignore_warns(category):
            warnings.warn(case["warning_message"], category, stacklevel=1)

    @pytest.mark.parametrize(
        "case",
        loader.warning_multi_cases(),
        ids=lambda c: "+".join(c["categories"]),
    )
    def test_ignore_warns_multiple(self, case):
        from _errortools.ignore import ignore_warns

        categories = [_resolve_warning_category(n) for n in case["categories"]]
        with ignore_warns(*categories):
            for cat, msg in zip(categories, case["messages"], strict=True):
                warnings.warn(msg, cat, stacklevel=1)

    @pytest.mark.parametrize(
        "case",
        loader.warning_unrelated_cases(),
        ids=lambda c: f"!{','.join(c['suppressed'])}|{c['raised']}",
    )
    def test_unrelated_warning_still_emitted(self, case):
        from _errortools.ignore import ignore_warns

        suppressed = [_resolve_warning_category(n) for n in case["suppressed"]]
        raised = _resolve_warning_category(case["raised"])

        with pytest.warns(raised):
            with ignore_warns(*suppressed):
                warnings.warn("still emitted", raised, stacklevel=1)

    @pytest.mark.parametrize("case", loader.warning_no_args_cases(), ids=lambda c: c["raised"])
    def test_no_args_suppresses_everything(self, case):
        from _errortools.ignore import ignore_warns

        raised = _resolve_warning_category(case["raised"])
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with ignore_warns():
                warnings.warn("anything", raised, stacklevel=1)
        assert len(caught) == 0


# ============================================================================
# @convert decorator
# ============================================================================


class TestConvertDataDriven:
    """Verify @convert against a table of source/target scenarios."""

    @pytest.mark.parametrize("case", loader.convert_cases(), ids=lambda c: c["name"])
    def test_convert_changes_type(self, case):
        from _errortools.decorator.handlers import convert

        source = loader._resolve_type(case["source"])
        target = loader._resolve_type(case["target"])

        @convert(source, target)
        def fn():
            raise loader.make_exception(case["raise"])

        with pytest.raises(target) as exc_info:
            fn()
        assert case["expected_message_substring"] in str(exc_info.value)

    @pytest.mark.parametrize("case", loader.convert_chained_cases(), ids=lambda c: f"{c['source']}->{c['target']}")
    def test_convert_chains_original(self, case):
        from _errortools.decorator.handlers import convert

        source = loader._resolve_type(case["source"])
        target = loader._resolve_type(case["target"])

        @convert(source, target)
        def fn():
            raise loader.make_exception(case["raise"])

        with pytest.raises(target) as exc_info:
            fn()
        assert isinstance(exc_info.value.__cause__, source)

    @pytest.mark.parametrize("case", loader.convert_tuple_cases(), ids=lambda c: c["name"])
    def test_convert_with_tuple_source(self, case):
        from _errortools.decorator.handlers import convert

        sources = tuple(loader._resolve_type(s) for s in case["sources"])
        target = loader._resolve_type(case["target"])

        @convert(sources, target)
        def fn():
            raise loader.make_exception(case["raise"])

        with pytest.raises(target):
            fn()

    @pytest.mark.parametrize("case", loader.convert_custom_message_cases(), ids=lambda c: c["message"])
    def test_convert_uses_custom_message(self, case):
        from _errortools.decorator.handlers import convert

        source = loader._resolve_type(case["source"])
        target = loader._resolve_type(case["target"])

        @convert(source, target, message=case["message"])
        def fn():
            raise loader.make_exception(case["raise"])

        with pytest.raises(target, match=case["message"]):
            fn()


# ============================================================================
# @retry decorator
# ============================================================================


class TestRetryDataDriven:
    """Verify @retry against a table of retry scenarios."""

    @pytest.mark.parametrize(
        "case",
        loader.retry_success_cases(),
        ids=lambda c: f"t={c['times']},f={c['fails_before_success']}",
    )
    def test_retry_until_success(self, case):
        from _errortools.decorator.retry import retry

        state = {"n": 0}

        @retry(times=case["times"], on=ValueError)
        def fn():
            state["n"] += 1
            if state["n"] <= case["fails_before_success"]:
                raise ValueError(f"fail {state['n']}")
            return state["n"]

        assert fn() == case["fails_before_success"] + 1
        assert state["n"] == case["expected_call_count"]

    @pytest.mark.parametrize(
        "case",
        loader.retry_exhaustion_cases(),
        ids=lambda c: f"t={c['times']}",
    )
    def test_retry_exhausts_and_reraises(self, case):
        from _errortools.decorator.retry import retry

        state = {"n": 0}

        @retry(times=case["times"], on=ValueError)
        def fn():
            state["n"] += 1
            raise ValueError("always")

        with pytest.raises(ValueError, match="always"):
            fn()
        # total attempts = times + 1
        assert state["n"] == case["times"] + 1

    @pytest.mark.parametrize(
        "case",
        loader.retry_unrelated_cases(),
        ids=lambda c: f"!on=ValueError|{c['raise']}",
    )
    def test_retry_propagates_unrelated(self, case):
        from _errortools.decorator.retry import retry

        state = {"n": 0}
        # ``case["raise"]`` is a textual spec like ``"RuntimeError('always')"``;
        # use ``case["expected"]`` (a bare type name) when looking up the type.
        exc = loader._resolve_type(case["expected"])

        @retry(times=case["times"], on=ValueError)
        def fn():
            state["n"] += 1
            raise loader.make_exception(case["raise"])

        with pytest.raises(exc):
            fn()
        assert state["n"] == case["expected_call_count"]

    @pytest.mark.parametrize(
        "case",
        loader.retry_exception_types(),
        ids=lambda c: c["exception"],
    )
    def test_retry_catches_subclass_of_exception(self, case):
        from _errortools.decorator.retry import retry

        exc_type = loader._resolve_type(case["exception"])
        # When ``on`` is left at its default (Exception), every Exception subclass
        # is caught and retried.
        state = {"n": 0}

        @retry(times=2)
        def fn():
            state["n"] += 1
            raise exc_type("fail")

        with pytest.raises(exc_type):
            fn()
        assert state["n"] == 3  # times + 1


# ============================================================================
# NonBlankErrorMsg
# ============================================================================


class TestNonBlankErrorMsgDataDriven:
    """Verify the NonBlankErrorMsg descriptor against whitespace/type edge cases."""

    @pytest.mark.parametrize(
        "case",
        loader.normalization_valid_cases(),
        ids=lambda c: repr(c["input"]),
    )
    def test_valid_input_strips_whitespace(self, case):
        from _errortools.descriptor.nonblankmsg import NonBlankErrorMsg

        class Holder:
            msg = NonBlankErrorMsg("Error message")

        h = Holder()
        h.msg = case["input"]
        assert h.msg == case["expected"]

    @pytest.mark.parametrize(
        "case",
        loader.normalization_blank_cases(),
        ids=lambda c: repr(c["input"]),
    )
    def test_blank_input_raises_value_error(self, case):
        from _errortools.descriptor.nonblankmsg import NonBlankErrorMsg

        class Holder:
            msg = NonBlankErrorMsg("Error message")

        h = Holder()
        with pytest.raises(ValueError, match="can't be blank"):
            h.msg = case["input"]

    @pytest.mark.parametrize(
        "case",
        loader.normalization_non_string_cases(),
        ids=lambda c: type(c["input"]).__name__,
    )
    def test_non_string_input_raises_value_error(self, case):
        from _errortools.descriptor.nonblankmsg import NonBlankErrorMsg

        class Holder:
            msg = NonBlankErrorMsg("Error message")

        h = Holder()
        with pytest.raises(ValueError, match="must be a string type"):
            h.msg = case["input"]


# ============================================================================
# Async retry smoke test (uses data to ensure parity with sync)
# ============================================================================


class TestRetryAsyncDataDriven:
    """Async version of the retry decorator verified against the same scenarios."""

    @pytest.mark.parametrize(
        "case",
        loader.retry_success_cases(),
        ids=lambda c: f"async-t={c['times']},f={c['fails_before_success']}",
    )
    def test_async_retry_until_success(self, case):
        from _errortools.decorator.retry import retry

        state = {"n": 0}

        @retry(times=case["times"], on=ValueError)
        async def fn():
            state["n"] += 1
            if state["n"] <= case["fails_before_success"]:
                raise ValueError(f"fail {state['n']}")
            return state["n"]

        assert asyncio.run(fn()) == case["fails_before_success"] + 1
        assert state["n"] == case["expected_call_count"]

    @pytest.mark.parametrize(
        "case",
        loader.retry_exhaustion_cases(),
        ids=lambda c: f"async-t={c['times']}",
    )
    def test_async_retry_exhausts_and_reraises(self, case):
        from _errortools.decorator.retry import retry

        state = {"n": 0}

        @retry(times=case["times"], on=ValueError)
        async def fn():
            state["n"] += 1
            raise ValueError("always")

        with pytest.raises(ValueError, match="always"):
            asyncio.run(fn())
        assert state["n"] == case["times"] + 1
