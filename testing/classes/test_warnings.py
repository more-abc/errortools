"""Tests for _errortools/classes/warn.py — BaseWarning and predefined warning classes."""

import pytest

from _errortools.classes.warn import (
    BaseWarning,
    DeprecatedWarning,
    PerformanceWarning,
    ResourceUsageWarning,
    RuntimeBehaviourWarning,
    ConfigurationWarning,
)

# =============================================================================
# BaseWarning — basic behaviour
# =============================================================================


class TestBaseWarning:
    def test_is_warning_subclass(self):
        assert issubclass(BaseWarning, Warning)

    def test_default_detail_used_when_none(self):
        w = BaseWarning()
        assert w.detail == BaseWarning.default_detail

    def test_custom_detail_overrides_default(self):
        w = BaseWarning("custom warning")
        assert w.detail == "custom warning"

    def test_str_returns_detail(self):
        w = BaseWarning("hello")
        assert str(w) == "hello"

    def test_repr(self):
        w = BaseWarning("hello")
        r = repr(w)
        assert "BaseWarning" in r
        assert "hello" in r

    def test_emit_issues_warning(self):
        with pytest.warns(BaseWarning):
            BaseWarning.emit(stacklevel=1)

    def test_emit_custom_detail(self):
        with pytest.warns(BaseWarning, match="custom detail"):
            BaseWarning.emit("custom detail", stacklevel=1)

    def test_custom_subclass(self):
        class ExperimentalWarning(BaseWarning):
            default_detail = "Experimental feature."

        w = ExperimentalWarning()
        assert w.detail == "Experimental feature."
        assert str(w) == "Experimental feature."


# =============================================================================
# Predefined warning subclasses — default details
# =============================================================================


class TestPredefinedWarnings:
    @pytest.mark.parametrize(
        "cls, expected_default",
        [
            (DeprecatedWarning, "This feature is deprecated."),
            (PerformanceWarning, "This operation may be slow."),
            (ResourceUsageWarning, "Inefficient resource usage detected."),
            (RuntimeBehaviourWarning, "Unexpected runtime behaviour."),
            (ConfigurationWarning, "Suboptimal configuration detected."),
        ],
    )
    def test_default_detail(self, cls, expected_default):
        w = cls()
        assert w.detail == expected_default

    @pytest.mark.parametrize(
        "cls",
        [
            DeprecatedWarning,
            PerformanceWarning,
            ResourceUsageWarning,
            RuntimeBehaviourWarning,
            ConfigurationWarning,
        ],
    )
    def test_custom_detail(self, cls):
        w = cls("override")
        assert w.detail == "override"

    @pytest.mark.parametrize(
        "cls",
        [
            DeprecatedWarning,
            PerformanceWarning,
            ResourceUsageWarning,
            RuntimeBehaviourWarning,
            ConfigurationWarning,
        ],
    )
    def test_is_base_warning_subclass(self, cls):
        assert issubclass(cls, BaseWarning)
        assert issubclass(cls, Warning)

    @pytest.mark.parametrize(
        "cls",
        [
            DeprecatedWarning,
            PerformanceWarning,
            ResourceUsageWarning,
            RuntimeBehaviourWarning,
            ConfigurationWarning,
        ],
    )
    def test_emit(self, cls):
        with pytest.warns(cls):
            cls.emit(stacklevel=1)


# =============================================================================
# Factory classmethods on BaseWarning
# =============================================================================


class TestWarningFactoryMethods:
    def test_deprecated_factory(self):
        w = BaseWarning.deprecated()
        assert isinstance(w, DeprecatedWarning)

    def test_performance_factory(self):
        w = BaseWarning.performance("slow path")
        assert isinstance(w, PerformanceWarning)
        assert w.detail == "slow path"

    def test_resource_factory(self):
        w = BaseWarning.resource()
        assert isinstance(w, ResourceUsageWarning)

    def test_runtime_factory(self):
        w = BaseWarning.runtime("weird behaviour")
        assert isinstance(w, RuntimeBehaviourWarning)
        assert w.detail == "weird behaviour"

    def test_configuration_factory(self):
        w = BaseWarning.configuration()
        assert isinstance(w, ConfigurationWarning)

    def test_factory_none_uses_default(self):
        w = BaseWarning.deprecated(None)
        assert w.detail == DeprecatedWarning.default_detail
