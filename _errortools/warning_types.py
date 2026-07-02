from typing import Union

from _errortools.version import VersionInfo
from errortools import _normalize_version


import warnings


class ErrortoolsDeprecationWarning(DeprecationWarning):
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

    def __init__(
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
