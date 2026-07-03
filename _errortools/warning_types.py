"""Warning types and function toolset for :mod:`errortools` module."""

import importlib
from typing import Any, Callable, Union

from _errortools.classes.errorcodes import RuntimeFailure
from _errortools.version import VersionInfo


import warnings


def _normalize_version(value: Union[str, VersionInfo, None]) -> str:
    """Coerce a version spec into its canonical string form.

    Args:
        value: Either a :class:`_errortools.version.VersionInfo`, a
            dotted-decimal string, or ``None``.

    Returns:
        The canonical string form.  ``None`` maps to the
        :data:`ErrortoolsDeprecationWarning._UNSPECIFIED` sentinel so
        warnings remain searchable even when version metadata is
        unknown.
    """
    if value is None:
        return ErrortoolsDeprecationWarning._UNSPECIFIED
    if isinstance(value, VersionInfo):
        return str(value)
    return value.strip()


class ErrortoolsWarning(Warning):
    """Base class for all warnings emitted by pytest."""

    __module__ = "errortools"


class ErrortoolsDeprecationWarning(ErrortoolsWarning, DeprecationWarning):
    """Base class for warnings about deprecated features in ``errortools``.

    Subclassing :class:`DeprecationWarning` (rather than emitting a bare
    ``DeprecationWarning``) lets library users filter with::

        warnings.filterwarnings(
            "error", category=errortools.ErrortoolsDeprecationWarning
        )

    The class is also safe to use directly as a *category* argument to
    :func:`warnings.warn`: when the standard library instantiates the
    category with a single message string, the constructor degrades
    gracefully — every other field falls back to a documented default.

    Attributes:
        raw_message: Original (un-formatted) message text.
        use_instead_message: Suggested replacement hint (possibly empty).
        removed_version: String form of the version in which the
            deprecated feature will be removed, or ``"<unspecified>"``.
        deprecated_version: String form of the version in which the
            feature was first deprecated, or ``"<unspecified>"``.
        formatted_message: Pre-rendered, end-user friendly message that
            is forwarded to ``DeprecationWarning.__init__``.

    Example:
        >>> import errortools
        >>> w = errortools.ErrortoolsDeprecationWarning(
        ...     "errortools.foo is deprecated",
        ...     use_instead="Use errortools.bar instead.",
        ...     removed_version="5.0",
        ... )
        >>> w.deprecated_version
        '<unspecified>'
        >>> 'Deprecated in errortools' in w.formatted_message
        True
    """

    __slots__ = (
        "raw_message",
        "use_instead_message",
        "removed_version",
        "deprecated_version",
        "formatted_message",
    )
    # Like pytest do to the warning classes
    __module__ = "errortools"
    _UNSPECIFIED: str = "<unspecified>"

    def __init__(  # noqa: B042
        self,
        message: str = "",
        use_instead: str = "",
        removed_version: Union[str, VersionInfo, None] = None,
        deprecated_version: Union[str, VersionInfo, None] = None,
    ) -> None:
        """Initialise the warning with structured deprecation metadata.

        Args:
            message: Human-readable description of the deprecation.
                When the class is used as a *category* in
                :func:`warnings.warn`, CPython invokes this constructor
                with only this argument, so a sensible default
                (empty string) keeps that path working.
            use_instead: Optional suggestion describing the replacement
                (e.g. ``"Use errortools.bar instead."``).  May be empty.
            removed_version: Version in which the feature will be
                removed.  Accepts a string (``"5.0"``), a
                :class:`_errortools.version.VersionInfo`, or ``None``
                (which renders as ``"<unspecified>"``).
            deprecated_version: Version in which the feature was first
                deprecated.  Same accepted types as ``removed_version``.
        """
        self.raw_message = message if isinstance(message, str) else str(message)
        self.use_instead_message = use_instead
        self.removed_version = _normalize_version(removed_version)
        self.deprecated_version = _normalize_version(deprecated_version)

        tail = f", {use_instead}" if use_instead else ""
        self.formatted_message = (
            f"{self.raw_message} (Deprecated in errortools v{self.deprecated_version}, "
            f"will be removed in errortools v{self.removed_version}){tail}"
        )
        super().__init__(self.formatted_message)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"message={self.raw_message!r}, "
            f"use_instead={self.use_instead_message!r}, "
            f"deprecated_version={self.deprecated_version!r}, "
            f"removed_version={self.removed_version!r})"
        )

    @classmethod
    def emit(
        cls,
        message: str,
        use_instead: str = "",
        removed_version: Union[str, VersionInfo, None] = None,
        deprecated_version: Union[str, VersionInfo, None] = None,
        stacklevel: int = 2,
    ) -> None:
        """Emit this warning via :func:`warnings.warn`.

        Convenience wrapper mirroring :meth:`BaseWarning.emit` so callers
        do not have to import :mod:`warnings` themselves.

        Args:
            message: Human-readable description of the deprecation.
            use_instead: Optional suggestion for the replacement.
            removed_version: Version in which the feature will be removed.
            deprecated_version: Version in which the feature was first
                deprecated.
            stacklevel: Same meaning as in :func:`warnings.warn`.  The
                default of ``2`` points at the caller of ``emit``.
        """
        warnings.warn(
            cls(
                message=message,
                use_instead=use_instead,
                removed_version=removed_version,
                deprecated_version=deprecated_version,
            ),
            stacklevel=stacklevel + 1,
        )


def _resolve_partial() -> Any:
    # ``partial`` is re-exported from ``_errortools.partial`` via the public
    # ``errortools.partial`` submodule shim.  Loading it here re-emits that
    # module's own ``DeprecationWarning`` while still returning the module.
    return importlib.import_module("errortools.partial")


def _resolve_fast_ignore() -> Any:
    from _errortools.ignore import fast_ignore as _cls

    return _cls


def _resolve_runtime_error() -> Any:
    # ``RuntimeError_`` was a type alias of ``Union[RuntimeFailure, TimeoutFailure]``;
    # ``isinstance`` callers benefit from the concrete first member while
    # ``type``-context usage keeps working through the existing aliases.
    return RuntimeFailure


def _resolve_lookup_error() -> Any:
    from _errortools.classes.errorcodes import NotFoundError as _cls

    return _cls


def _resolve_access_error() -> Any:
    from _errortools.classes.errorcodes import AccessDeniedError as _cls

    return _cls


def _resolve_input_error() -> Any:
    from _errortools.classes.errorcodes import InvalidInputError as _cls

    return _cls


_DEPRECATED_RESOLVERS: dict[str, Callable[[], Any]] = {
    "InputError": _resolve_input_error,
    "AccessError": _resolve_access_error,
    "LookupError_": _resolve_lookup_error,
    "RuntimeError_": _resolve_runtime_error,
    "fast_ignore": _resolve_fast_ignore,
    "partial": _resolve_partial,
}
_DEPRECATED_VERSIONS: dict[str, tuple[str, str]] = {
    "InputError": ("3.0", "5.0"),
    "AccessError": ("3.0", "5.0"),
    "LookupError_": ("3.0", "5.0"),
    "RuntimeError_": ("3.0", "5.0"),
    "fast_ignore": ("3.5.0", "5.2"),
    "partial": ("3.5", "5.0"),
}
# ---------------------------------------------------------------------------
# Deprecation catalogue
# ---------------------------------------------------------------------------
#
# Three small tables drive the lazy ``__getattr__`` dispatcher:
#
# * ``_DEPRECATED_NAMES``  — the public-facing ``(display_name, reason)``
#   pair, kept in the same 2-tuple shape documented in
#   ``.agents/skills/deprecate-public-name.md`` so existing skill tooling
#   stays compatible.
# * ``_DEPRECATED_VERSIONS`` — structured ``(deprecated_in, removed_in)``
#   metadata surfaced via ``ErrortoolsDeprecationWarning`` on access.
#   Missing entries degrade to ``"<unspecified>"``.
# * ``_DEPRECATED_RESOLVERS`` — zero-argument callables that lazily fetch
#   the canonical replacement object.  Callables (rather than direct
#   references) keep import-time cost identical while restoring the
#   transparent alias-return behaviour that the original dispatcher
#   silently lost (it used to fall through to ``globals().get(name)``
#   which returned ``None`` for every entry without a private alias).
_DEPRECATED_NAMES: dict[str, tuple[str, str]] = {
    "InputError": ("InputError", "Use InvalidInputError directly."),
    "AccessError": ("AccessError", "Use AccessDeniedError directly."),
    "LookupError_": ("LookupError_", "Use NotFoundError directly."),
    "RuntimeError_": ("RuntimeError_", "Use RuntimeFailure or TimeoutFailure directly."),
    "fast_ignore": ("fast_ignore", "Use errortools.future.super_fast_ignore instead."),
    "partial": (
        "partial",
        "Just use the original functions directly.",
    ),
}


def _deprecated_getattr(name: str) -> Any:
    """Internal dispatcher used by the module-level :func:`__getattr__`.

    Returns the resolved replacement *and* emits the structured
    :class:`ErrortoolsDeprecationWarning` for the given deprecated name.
    Falls back to ``None`` only if no resolver is registered (the slot
    in ``_DEPRECATED_RESOLVERS`` is missing).
    """
    attr_name, reason = _DEPRECATED_NAMES[name]
    deprecated_in, removed_in = _DEPRECATED_VERSIONS.get(
        name,
        (ErrortoolsDeprecationWarning._UNSPECIFIED, ErrortoolsDeprecationWarning._UNSPECIFIED),
    )
    ErrortoolsDeprecationWarning.emit(
        message=f"errortools.{attr_name} is deprecated. {reason}",
        use_instead=reason,
        deprecated_version=deprecated_in,
        removed_version=removed_in,
        stacklevel=2,
    )
    resolver = _DEPRECATED_RESOLVERS.get(name)
    if resolver is None:
        return None
    try:
        return resolver()
    except Exception:  # noqa: BLE001 — resolvers must never raise to the user.
        return None
