"""Ultra-lightweight plugin system for errortools."""

from typing import Callable, Any

_REGISTRY: dict[str, Callable[..., Any]] = {}

__all__ = [
    "register",
    "get",
    "list_all",
    "run",
    "remove",
    "Registry",
]


def register(name: str) -> Callable:
    """
    Register plugin (decorator)

    .. versionadded:: 3.2
    """

    def decorator(func: Callable) -> Callable:
        _REGISTRY[name] = func
        return func

    return decorator


def get(name: str, default: Any = None) -> Any:
    """
    Get registered plugin

    .. versionadded:: 3.2
    """
    plugin = _REGISTRY.get(name)
    if plugin is None:
        if default is not None:
            return default
        raise ValueError(f"Plugin {name!r} is not registered")
    return plugin


def remove(name: str) -> None:
    """
    Remove a plugin

    .. versionadded:: 3.2
    """
    _REGISTRY.pop(name, None)


def list_all() -> list[str]:
    """
    List all plugin names

    .. versionadded:: 3.2
    """
    return list(_REGISTRY.keys())


def run(name: str, *args, **kwargs) -> Any:
    """Run plugin

    .. versionadded:: 3.2"""
    return get(name)(*args, **kwargs)


class Registry:
    """.. versionadded:: 3.2"""

    @staticmethod
    def register(name: str, func: Callable) -> None:
        _REGISTRY[name] = func

    @staticmethod
    def list_all() -> list[str]:
        return list_all()

    @staticmethod
    def get(name: str) -> Any:
        return get(name)
