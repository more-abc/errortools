# Logging

`errortools.logging` is a loguru-inspired structured logger with no external dependencies.

## Quick start

```python
from errortools.logging import logger

logger.info("Server started on port {}", 8080)
logger.warning("Disk at {pct:.1f}%", pct=92.5)
logger.success("All systems operational")
```

Output (colorized in terminal):

```
2026-04-30 08:34:21.850 | ℹ INFO     | <string>:<module>:3 - Server started on port 8080
2026-04-30 08:34:21.851 | ⚠ WARNING  | <string>:<module>:4 - Disk at 92.5%
2026-04-30 08:34:21.851 | ✔ SUCCESS  | <string>:<module>:5 - All systems operational
```

## Log levels

| Method | Level | Number |
|--------|-------|--------|
| `logger.trace()` | TRACE | 5 |
| `logger.debug()` | DEBUG | 10 |
| `logger.info()` | INFO | 20 |
| `logger.success()` | SUCCESS | 25 |
| `logger.warning()` | WARNING | 30 |
| `logger.error()` | ERROR | 40 |
| `logger.critical()` | CRITICAL | 50 |

## Sinks

Add and remove log destinations at runtime.

### Stream sink

```python
import sys
from errortools.logging import logger

# Add stdout sink
logger.add(sys.stdout, level="WARNING")
```

### File sink

```python
# File with rotation and retention
sid = logger.add(
    "logs/app.log",
    rotation=10_485_760,  # 10 MB
    retention=5           # Keep 5 old files
)
```

### Callable sink

```python
# Any callable
logger.add(print)
logger.add(lambda msg: send_to_service(msg))
```

### Remove sinks

```python
# Remove by ID
logger.remove(sid)

# Remove all sinks
logger.remove()
```

## Level filtering

```python
from errortools.logging import logger, Level

# Set global level
logger.set_level("WARNING")  # or Level.WARNING or 30

logger.debug("dropped")   # Below threshold — not emitted
logger.warning("kept")    # At threshold — emitted
```

## Context binding

`bind()` returns a new logger with extra fields in every record.

```python
# Bind request context
req_log = logger.bind(request_id="abc-123", user="alice")
req_log.info("Request received")

# Stack bindings
db_log = req_log.bind(db="postgres")
db_log.debug("Query OK")  # Contains: request_id, user, db
```

## Exception capture

### exception()

Log with automatic traceback capture:

```python
try:
    connect()
except ConnectionError:
    logger.exception("DB connection failed")  # Logs at ERROR + traceback
```

### opt(exception=True)

Equivalent long-hand:

```python
logger.opt(exception=True).error("DB connection failed")
```

## catch()

Auto-log and suppress exceptions.

### As context manager

```python
# Suppress and log
with logger.catch():
    int("not a number")  # Logged at ERROR, then suppressed

# Re-raise after logging
with logger.catch(ConnectionError, reraise=True):
    connect()
```

### As decorator

```python
@logger.catch(ValueError)
def parse(s: str) -> int:
    return int(s)

parse("bad")  # Logged and suppressed
```

## Custom format

```python
logger.add(
    "debug.log",
    fmt="{time} | {level} | {name}:{function}:{line} - {message}",
)
```

### Available placeholders

- `{time}` - Timestamp
- `{level}` - Log level
- `{name}` - Module name
- `{file}` - File name
- `{line}` - Line number
- `{function}` - Function name
- `{message}` - Log message

## Advanced usage

### Multiple sinks with different levels

```python
# Console: WARNING and above
logger.add(sys.stderr, level="WARNING")

# File: DEBUG and above
logger.add("debug.log", level="DEBUG")

# Critical alerts: CRITICAL only
logger.add(send_alert, level="CRITICAL")
```

### Structured logging

```python
req_log = logger.bind(
    request_id="abc-123",
    user_id=42,
    endpoint="/api/users"
)

req_log.info("Request started")
req_log.success("Request completed in {ms}ms", ms=123)
```
