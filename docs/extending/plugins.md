# Plugin System

> **API stability:** `provisional`
>
> The plugin API is functional but may evolve based on community feedback.
>
> ```{versionadded} 3.2
> ```

errortools includes an ultra-lightweight plugin registry. It is useful when you want to:

- Dynamically extend library behaviour at runtime.
- Keep optional features as pluggable modules.
- Swap implementations for different environments (dev vs. prod).

## Registering a plugin

### Decorator (recommended)

Use `register()` as a decorator on the function you wish to expose:

```python
from errortools import register

@register("json_serialize")
def _to_json(obj):
    import json
    return json.dumps(obj.__dict__, default=str)
```

If the name has already been registered the previous function is **silently overwritten**.

### Programmatic registration

For cases where a decorator is inconvenient (e.g. third-party adapters), use `Registry.register`:

```python
from errortools import Registry

def yaml_serialize(obj):
    ...  # implementation

Registry.register("yaml_serialize", yaml_serialize)
```

## Calling a plugin

### Direct lookup

`get()` returns the raw callable. This is the preferred pattern when you will invoke the plugin many times and want to avoid repeated dictionary look-ups:

```python
from errortools import get

serialize = get("json_serialize")

for user in users:
    payload = serialize(user)
    queue.put(payload)
```

### One-shot execution

`run()` combines lookup and invocation. It is convenient for ad-hoc calls:

```python
from errortools import run

output = run("json_serialize", some_user)
```

### Default value for missing plugins

`get()` accepts an optional `default`. When provided, missing plugins return the default instead of raising `ValueError`:

```python
from errortools import get

formatter = get("rich_formatter", default=plain_formatter)
```

## Inspecting and removing plugins

```python
from errortools import list_all, remove

print(list_all())
# ['json_serialize']

remove("json_serialize")
print(list_all())
# []
```

`remove()` is idempotent—calling it with a name that does not exist does nothing.

You can check whether a plugin exists without risk of raising:

```python
from errortools import has

if has("json_serialize"):
    ...
```

To remove **all** plugins at once (useful in test teardown):

```python
from errortools import clear

clear()
```

## Error handling

| Situation | Behaviour |
|-----------|-----------|
| `get("unknown")` | Raises `ValueError: Plugin 'unknown' is not registered` |
| `get("unknown", default=f)` | Returns `f` |
| `get("unknown", default=None)` | Returns `None` (since 3.3.5) |
| `run("unknown")` | Raises `ValueError` (no default path) |
| `has("unknown")` | Returns `False` |

## Practical example: environment-based alert backend

```python
# errortools_alerts/__init__.py
from errortools import register

@register("alert.send")
def _default_alert(message: str):
    print(f"[ALERT] {message}", file=sys.stderr)
```

A production package can override it:

```python
# errortools_alerts_pagerduty/__init__.py
from errortools import Registry
from .client import PagerDutyClient

_registry = PagerDutyClient(api_key=...)
Registry.register("alert.send", _registry.send)
```

Application code stays the same regardless of which package is installed:

```python
from errortools import run

run("alert.send", "Disk usage exceeded 90 %")
```

## Thread safety

The internal registry is a plain `dict`. Concurrent registration / removal from multiple threads is **not** guaranteed to be safe; serialise such operations with a `threading.Lock` if necessary.  Look-ups (`get`, `run`, `list_all`) are safe because CPython dict read operations are atomic.

## API reference

### `register(name: str) -> Callable[[Callable], Callable]`

Decorator that adds a function to the global registry under `name`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique identifier for the plugin. |

**Returns:** A decorator that takes the target function and returns it unchanged.

### `get(name: str, default: Any = None) -> Any`

Retrieve a registered plugin.

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Plugin identifier. |
| `default` | `Any` | Value returned when the plugin is missing. If not provided, a `ValueError` is raised instead. |

**Returns:** The registered callable, or `default`.

**Raises:** `ValueError` — if the plugin does not exist and no *default* was supplied.

**Note:** Starting from **3.3.5**, passing `default=None` is correctly honored and returns `None` instead of raising.

### `run(name: str, *args, **kwargs) -> Any`

Look up and immediately call a plugin.

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Plugin identifier. |
| `*args` | | Positional arguments forwarded to the plugin. |
| `**kwargs` | | Keyword arguments forwarded to the plugin. |

**Returns:** Whatever the plugin callable returns.

**Raises:** `ValueError` — if the plugin does not exist.

### `list_all() -> list[str]`

Return a snapshot of currently registered plugin names.

**Returns:** `list[str]`

### `remove(name: str) -> None`

Delete a plugin from the registry. No-op if the name is absent.

### `has(name: str) -> bool`

Check whether a plugin is registered.

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Plugin identifier. |

**Returns:** `True` if the plugin exists, otherwise `False`.

### `clear() -> None`

Remove **all** plugins from the registry. This is useful for test isolation or resetting state.

### `class Registry`

Programmatic equivalent of the top-level functions, exposed as a class for IDE discoverability.

| Method | Equivalent to |
|--------|---------------|
| `Registry.register(name, func)` | `register(name)(func)` |
| `Registry.get(name)` | `get(name)` |
| `Registry.has(name)` | `has(name)` |
| `Registry.list_all()` | `list_all()` |
| `Registry.remove(name)` | `remove(name)` |
| `Registry.clear()` | `clear()` |

## See also

- [`BaseLogger.bind()`](../user_guide/logging.md#context-binding) — a different kind of extensibility where extra context fields are attached to every log record.
