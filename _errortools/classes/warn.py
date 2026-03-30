"""Base warning classes."""

from __future__ import annotations

import warnings

from .base.base import ErrorToolsBaseWarning

__all__ = [
    "BaseWarning",
    "DeprecatedWarning",
    "PerformanceWarning",
    "ResourceUsageWarning",
    "RuntimeBehaviourWarning",
    "ConfigurationWarning",
]


class BaseWarning(ErrorToolsBaseWarning):
    """A base warning with a default detail message.

    Subclass and override `default_detail` to define domain-specific
    warnings.  Call `emit` to issue via `warnings.warn`.

    Attributes:
        default_detail: Fallback message used when no *detail* is supplied.

    Example:
        >>> class ExperimentalWarning(BaseWarning):
        ...     default_detail = "This feature is experimental."
        >>> ExperimentalWarning.emit()
    """

    default_detail: str = "A warning occurred."

    def __init__(self, detail: str | None = None) -> None:
        """Initialise the warning with an optional detail message.

        Args:
            detail: Human-readable description of the warning.  Falls back to
                `default_detail` when ``None``.
        """
        self.detail = detail if detail is not None else self.default_detail
        super().__init__(self.detail)

    def __str__(self) -> str:
        return self.detail

    def __repr__(self) -> str:
        return f"{type(self).__name__}(detail={self.detail!r})"

    @classmethod
    def emit(cls, detail: str | None = None, stacklevel: int = 2) -> None:
        """Issue this warning via `warnings.warn`.

        Args:
            detail: Optional override for the default detail message.
            stacklevel: Controls which call site appears in the warning.
                Defaults to ``2`` so the warning points at the caller of
                `emit`, not at `emit` itself.
        """
        warnings.warn(cls(detail), stacklevel=stacklevel)

    # ------------------------------------------------------------------
    # Factory classmethods
    # ------------------------------------------------------------------

    @classmethod
    def deprecated(cls, detail: str | None = None) -> DeprecatedWarning:
        """Return a `DeprecatedWarning` instance."""
        return DeprecatedWarning(detail)

    @classmethod
    def performance(cls, detail: str | None = None) -> PerformanceWarning:
        """Return a `PerformanceWarning` instance."""
        return PerformanceWarning(detail)

    @classmethod
    def resource(cls, detail: str | None = None) -> ResourceUsageWarning:
        """Return a `ResourceUsageWarning` instance."""
        return ResourceUsageWarning(detail)

    @classmethod
    def runtime(cls, detail: str | None = None) -> RuntimeBehaviourWarning:
        """Return a `RuntimeBehaviourWarning` instance."""
        return RuntimeBehaviourWarning(detail)

    @classmethod
    def configuration(cls, detail: str | None = None) -> ConfigurationWarning:
        """Return a `ConfigurationWarning` instance."""
        return ConfigurationWarning(detail)


# ----------------------------------------------------------------------
# Predefined subclasses
# ----------------------------------------------------------------------


class DeprecatedWarning(BaseWarning):
    """A feature or API is deprecated and may be removed in future."""

    default_detail = "This feature is deprecated."


class PerformanceWarning(BaseWarning):
    """An operation may cause significant performance degradation."""

    default_detail = "This operation may be slow."


class ResourceUsageWarning(BaseWarning):
    """A resource is being used inefficiently."""

    default_detail = "Inefficient resource usage detected."


class RuntimeBehaviourWarning(BaseWarning):
    """Unusual behaviour detected at runtime that may indicate a bug."""

    default_detail = "Unexpected runtime behaviour."


class ConfigurationWarning(BaseWarning):
    """A configuration value is missing, unusual, or suboptimal."""

    default_detail = "Suboptimal configuration detected."
