def _get_version_tuple(version: str) -> tuple[int, int, int]:
    parts = [int(p) for p in version.split(".")]

    major = parts[0] if len(parts) >= 1 else 0
    minor = parts[1] if len(parts) >= 2 else 0
    patch = parts[2] if len(parts) >= 3 else 0

    return (major, minor, patch)


__version__: str = "3.3.1"
__version_tuple__: tuple[int, int, int] = _get_version_tuple(__version__)
__commit_id__: str | None = None

version = __version__
version_tuple = __version_tuple__
commit_id = __commit_id__
