"""Ultra-lightweight plugin system for errortools."""

from typing import Callable, Any

_REGISTRY: dict[str, Callable[..., Any]] = {}
_UNSET = object()

__all__ = [
    "register",
    "get",
    "has",
    "list_all",
    "run",
    "remove",
    "clear",
    "Registry",
]


def register(name: str) -> Callable:
    """Register plugin (decorator).

    .. versionadded:: 3.2
    """

    def decorator(func: Callable) -> Callable:
        _REGISTRY[name] = func
        return func

    return decorator


def get(name: str, default: Any = _UNSET) -> Any:
    """Get registered plugin.

    Args:
        name: Plugin identifier.
        default: Value returned when the plugin is missing.
            If not provided, a `ValueError` is raised instead.

    Raises:
        ValueError: If the plugin does not exist and no *default* was supplied.

    .. versionadded:: 3.2
    """
    try:
        return _REGISTRY[name]
    except KeyError:
        if default is not _UNSET:
            return default
        raise ValueError(f"Plugin {name!r} is not registered")


def has(name: str) -> bool:
    """Check whether a plugin is registered.

    Args:
        name: Plugin identifier.

    Returns:
        ``True`` if a plugin with the given *name* is registered,
        otherwise ``False``.

    .. versionadded:: 3.3
    """
    return name in _REGISTRY


def remove(name: str) -> None:
    """Remove a plugin.

    This is a no-op if the plugin does not exist.

    .. versionadded:: 3.2
    """
    _REGISTRY.pop(name, None)


def clear() -> None:
    """Remove all plugins from the registry.

    .. versionadded:: 3.3
    """
    _REGISTRY.clear()


def list_all() -> list[str]:
    """List all plugin names.

    .. versionadded:: 3.2
    """
    return list(_REGISTRY.keys())


def run(name: str, *args, **kwargs) -> Any:
    """Run plugin.

    Raises:
        ValueError: If the plugin does not exist.

    .. versionadded:: 3.2
    """
    return get(name)(*args, **kwargs)


class Registry:
    """Static class providing an alternative API for the plugin registry.

    .. versionadded:: 3.2
    """

    @staticmethod
    def register(name: str, func: Callable) -> None:
        _REGISTRY[name] = func

    @staticmethod
    def list_all() -> list[str]:
        return list_all()

    @staticmethod
    def get(name: str) -> Any:
        return get(name)

    @staticmethod
    def has(name: str) -> bool:
        return has(name)

    @staticmethod
    def remove(name: str) -> None:
        remove(name)

    @staticmethod
    def clear() -> None:
        clear()


if __name__ == "__main__":
    print(f"All plugins: {list_all()}")
