"""Tests for ``errortools/__init__.py`` — public re-export package.

These tests cover the optimization of
:class:`errortools.ErrortoolsDeprecationWarning` and the lazy
``__getattr__`` deprecation dispatcher.
"""

import warnings

import pytest

import _errortools.warning_types
import errortools
from _errortools.version import VersionInfo

# =============================================================================
# ErrortoolsDeprecationWarning — structured constructor
# =============================================================================


class TestErrortoolsDeprecationWarning:
    def test_is_subclass_of_deprecation_warning(self):
        assert issubclass(_errortools.warning_types.ErrortoolsDeprecationWarning, DeprecationWarning)

    def test_is_in_dunder_all(self):
        assert "ErrortoolsDeprecationWarning" in errortools.__all__

    def test_no_args_uses_unspecified_defaults(self):
        w = _errortools.warning_types.ErrortoolsDeprecationWarning()
        assert w.raw_message == ""
        assert w.use_instead_message == ""
        assert w.deprecated_version == "<unspecified>"
        assert w.removed_version == "<unspecified>"
        assert w.formatted_message == (
            " (Deprecated in errortools v<unspecified>, will be removed in errortools v<unspecified>)"
        )

    def test_single_message_arg_is_supported(self):
        w = _errortools.warning_types.ErrortoolsDeprecationWarning("errortools.foo is deprecated")
        assert w.raw_message == "errortools.foo is deprecated"
        assert w.use_instead_message == ""
        assert w.deprecated_version == "<unspecified>"
        assert w.removed_version == "<unspecified>"
        assert "Deprecated in errortools" in w.formatted_message

    def test_warning_subclass_zero_or_one_argument(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            warnings.warn("hello world", _errortools.warning_types.ErrortoolsDeprecationWarning)
        assert len(caught) == 1
        rec = caught[0]
        assert issubclass(rec.category, _errortools.warning_types.ErrortoolsDeprecationWarning)
        assert "hello world" in str(rec.message)
        assert "Deprecated in errortools" in str(rec.message)

    def test_uses_string_versions(self):
        w = _errortools.warning_types.ErrortoolsDeprecationWarning(
            "msg",
            use_instead="use X instead",
            removed_version="5.0",
            deprecated_version="3.0",
        )
        assert w.removed_version == "5.0"
        assert w.deprecated_version == "3.0"
        assert "use X instead" in w.formatted_message
        assert "v5.0" in w.formatted_message
        assert "v3.0" in w.formatted_message

    def test_accepts_version_info(self):
        w = _errortools.warning_types.ErrortoolsDeprecationWarning(
            "msg",
            removed_version=VersionInfo(5, 0, 0),
            deprecated_version=VersionInfo(3, 1, 2),
        )
        assert w.removed_version == "5.0.0"
        assert w.deprecated_version == "3.1.2"

    def test_version_strings_are_stripped(self):
        w = _errortools.warning_types.ErrortoolsDeprecationWarning(
            "msg",
            removed_version="  5.0  ",
            deprecated_version=" 3.0 ",
        )
        assert w.removed_version == "5.0"
        assert w.deprecated_version == "3.0"

    def test_repr_contains_all_fields(self):
        w = _errortools.warning_types.ErrortoolsDeprecationWarning("msg", use_instead="use X")
        r = repr(w)
        assert "ErrortoolsDeprecationWarning(" in r
        assert "message=" in r
        assert "use_instead=" in r
        assert "deprecated_version=" in r
        assert "removed_version=" in r

    def test_has_slots_declared(self):
        slots = _errortools.warning_types.ErrortoolsDeprecationWarning.__slots__
        # Every documented attribute must be a declared slot.
        assert "raw_message" in slots
        assert "use_instead_message" in slots
        assert "removed_version" in slots
        assert "deprecated_version" in slots
        assert "formatted_message" in slots

    def test_slot_attributes_round_trip(self):
        w = _errortools.warning_types.ErrortoolsDeprecationWarning("msg")
        # Reading a known slot attribute works.
        assert w.raw_message == "msg"
        assert w.formatted_message.startswith("msg")
        # All five slots are accessible.
        for attr in (
            "raw_message",
            "use_instead_message",
            "removed_version",
            "deprecated_version",
            "formatted_message",
        ):
            assert hasattr(w, attr)

    def test_formatted_message_is_str(self):
        w = _errortools.warning_types.ErrortoolsDeprecationWarning("hello")
        assert isinstance(w.formatted_message, str)

    def test_emit_classmethod_emits_warning(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _errortools.warning_types.ErrortoolsDeprecationWarning.emit(
                "via emit()",
                use_instead="use Z",
                removed_version="5.0",
            )
        assert len(caught) == 1
        rec = caught[0]
        assert issubclass(rec.category, _errortools.warning_types.ErrortoolsDeprecationWarning)
        assert "via emit()" in str(rec.message)
        assert "use Z" in str(rec.message)

    def test_emit_default_stacklevel_points_past_impl(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _errortools.warning_types.ErrortoolsDeprecationWarning.emit("hello")
        assert len(caught) == 1
        filename = caught[0].filename
        # The default stacklevel must climb out of the implementation
        # file.  Some test runners (e.g. ``pytest``'s ``recwarn``)
        # interpose one extra frame, so we accept either the test file
        # or pytest's own helper.
        assert not filename.endswith("errortools/__init__.py")
        assert not filename.endswith("_errortools\\__init__.py")
        assert "test_init.py" in filename or "_pytest" in filename

    def test_filter_by_subclass_via_warnings_filterwarnings(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error", _errortools.warning_types.ErrortoolsDeprecationWarning)
            with pytest.raises(_errortools.warning_types.ErrortoolsDeprecationWarning):
                _errortools.warning_types.ErrortoolsDeprecationWarning.emit("filterable")


# =============================================================================
# __getattr__ lazy deprecation dispatcher
# =============================================================================


class TestDeprecatedNamesDispatcher:
    def test_input_error_emits_warning_with_structured_version(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", _errortools.warning_types.ErrortoolsDeprecationWarning)
            errortools.InputError  # noqa: B018
        rec = next(c for c in caught if issubclass(c.category, _errortools.warning_types.ErrortoolsDeprecationWarning))
        # ``rec.message`` *is* the ``ErrortoolsDeprecationWarning`` instance —
        # that's how the structured fields are carried in transit.
        inst = rec.message
        assert isinstance(inst, _errortools.warning_types.ErrortoolsDeprecationWarning)
        assert inst.deprecated_version == "3.0"
        assert inst.removed_version == "5.0"
        assert inst.use_instead_message == "Use InvalidInputError directly."
        assert "InputError" in inst.raw_message

    def test_input_error_returns_canonical_replacement(self):
        from _errortools.classes.errorcodes import InvalidInputError

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", _errortools.warning_types.ErrortoolsDeprecationWarning)
            value = errortools.InputError  # noqa: B018
        assert value is InvalidInputError

    def test_access_error_returns_canonical_replacement(self):
        from _errortools.classes.errorcodes import AccessDeniedError

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            value = errortools.AccessError  # noqa: B018
        assert value is AccessDeniedError

    def test_lookup_error_returns_canonical_replacement(self):
        from _errortools.classes.errorcodes import NotFoundError

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            value = errortools.LookupError_  # noqa: B018
        assert value is NotFoundError

    def test_runtime_error_returns_first_replacement(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            value = errortools.RuntimeError_  # noqa: B018
        assert value is errortools.RuntimeFailure

    def test_fast_ignore_returns_canonical_replacement(self):
        from _errortools.ignore import fast_ignore

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            value = errortools.fast_ignore  # noqa: B018
        assert value is fast_ignore

    def test_partial_submodule_loads_lazily(self):
        """``errortools.partial`` is loaded on demand and emits its own warning."""
        with warnings.catch_warnings():
            # The submodule's own DeprecationWarning triggers here; silence it
            # to assert only the dispatcher behaviour.
            warnings.simplefilter("ignore")
            value = errortools.partial
        assert value.__name__ == "errortools.partial"

    def test_emits_deprecation_warning_each_access(self):
        """The dispatcher must warn on every access (no caching of warning state)."""
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", _errortools.warning_types.ErrortoolsDeprecationWarning)
            errortools.InputError  # noqa: B018
            errortools.AccessError  # noqa: B018
        deprecations = [
            c for c in caught if issubclass(c.category, _errortools.warning_types.ErrortoolsDeprecationWarning)
        ]
        assert len(deprecations) == 2

    def test_unknown_attribute_still_raises_attribute_error(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with pytest.raises(AttributeError):
                errortools.totally_made_up_name  # type: ignore[attr-defined]

    def test_submodule_lazy_loading_still_works(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mod = errortools.future
        assert mod.__name__ == "_errortools.future"

    def test_typed_alias_round_trip_isinstance(self):
        """``isinstance`` works through the deprecated alias (it IS the canonical class)."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", _errortools.warning_types.ErrortoolsDeprecationWarning)
            cls = errortools.InputError  # noqa: B018
        err: object = cls("bad input")  # raises if constructor is strict
        assert isinstance(err, cls)
        assert isinstance(err, errortools.InvalidInputError)
        assert isinstance(err, errortools.BaseErrorCodes)


class TestDeprecationCatalogue:
    """The three-table ``_DEPRECATED_*`` catalogue is structurally consistent."""

    def test_names_keys_match_resolvers_and_versions(self):
        n = set(_errortools.warning_types._DEPRECATED_NAMES)
        v = set(_errortools.warning_types._DEPRECATED_VERSIONS)
        r = set(_errortools.warning_types._DEPRECATED_RESOLVERS)
        assert n == v == r, (
            f"Mismatch:\n  _DEPRECATED_NAMES only: {n - r}\n  "
            f"_DEPRECATED_RESOLVERS only: {r - n}\n  "
            f"_DEPRECATED_VERSIONS only: {v - n}"
        )

    def test_each_resolver_is_callable_zero_args(self):
        for name, resolver in _errortools.warning_types._DEPRECATED_RESOLVERS.items():
            assert callable(resolver), f"{name!r} resolver must be callable"

    def test_each_version_pair_is_two_strings(self):
        for name, (deprecated, removed) in _errortools.warning_types._DEPRECATED_VERSIONS.items():
            assert isinstance(deprecated, str) and deprecated, f"{name!r} deprecated version invalid"
            assert isinstance(removed, str) and removed, f"{name!r} removed version invalid"


# =============================================================================
# Module surface
# =============================================================================


class TestPublicAPISurface:
    def test_all_includes_deprecated_names(self):
        """``__all__`` drives ``dir(errortools)`` and ``from errortools import *``."""
        all_names = set()
        for entry in errortools.__all__:
            # ``__all__`` may flatten nested lists on Python 3.11+
            # for older interpreter versions we materialise entries as-is.
            if isinstance(entry, list):
                all_names.update(entry)
            else:
                all_names.add(entry)
        for deprecated in ("InputError", "AccessError", "LookupError_", "RuntimeError_"):
            assert deprecated in all_names

    def test_version_metadata_is_present(self):
        assert isinstance(errortools.__version__, str)
        assert isinstance(errortools.__version_info__, VersionInfo)

    def test_repr_warning_is_dev_friendly(self):
        w = _errortools.warning_types.ErrortoolsDeprecationWarning("alpha", removed_version="5.0")
        # repr should round-trip the meaningful fields
        text = repr(w)
        assert "'alpha'" in text
        assert "'5.0'" in text
