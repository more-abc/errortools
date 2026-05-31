## Plugin System

### register()
```python
register(name: str) -> Callable
```
Decorator to register a function as plugin.

**Parameters:**
- `name`: Unique name for plugin

#### Example:
```python
from errortools import register

@register("my_plugin")
def my_plugin():
    return "Hello from plugin"
```

### get()
```python
get(name: str, default: Any = None) -> Callable[..., Any]
```
Get registered plugin function.

**Raises:**
- `ValueError`: Plugin not registered

#### Example:
```python
from errortools import get
plugin = get("my_plugin")
```

### list_all()
```python
list_all() -> list[str]
```
List all registered plugin names.

### run()
```python
run(name: str, *args, **kwargs) -> Any
```
Execute registered plugin.

**Parameters:**
- `name`: Plugin name
- `*args, **kwargs`: Arguments passed to plugin

**Raises:**
- `ValueError`: Plugin not registered

### remove()
```python
remove(name: str) -> None
```
Remove plugin from registry.
