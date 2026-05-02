# Examples

Real-world examples demonstrating errortools usage.

## Web API Error Handling

```python
from errortools import ContextException, ignore, logger

class APIError(ContextException):
    code = 5000
    default_detail = "API request failed"

def fetch_user(user_id: int) -> dict:
    try:
        response = requests.get(f"/api/users/{user_id}")
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        raise (
            APIError(f"Failed to fetch user {user_id}")
            .with_context(
                user_id=user_id,
                status_code=e.response.status_code,
                endpoint=e.response.url
            )
            .with_cause(e)
        )

# Usage with logging
req_log = logger.bind(request_id="abc-123")
with logger.catch(APIError):
    user = fetch_user(42)
    req_log.info("User fetched successfully")
```

## Database Connection with Retry

```python
from errortools import retry, timeout, logger
import asyncio

@retry(times=3, on=(ConnectionError, TimeoutError), delay=2.0)
@timeout(10.0)
async def connect_db(host: str, port: int) -> Connection:
    logger.info("Connecting to {}:{}", host, port)
    conn = await asyncio.open_connection(host, port)
    logger.success("Connected to database")
    return conn

# Automatically retries up to 3 times with 2s delay
# Times out after 10 seconds per attempt
conn = await connect_db("localhost", 5432)
```

## Batch Processing with Error Collection

```python
from errortools.future import ExceptionCollector
from errortools import logger

def process_batch(items: list[dict]) -> None:
    collector = ExceptionCollector()
    
    for item in items:
        collector.catch(process_item, item)
    
    if collector.has_errors:
        logger.error(
            "Failed to process {} out of {} items",
            collector.count,
            len(items)
        )
        # Continue or raise based on requirements
        if collector.count > len(items) * 0.1:  # >10% failure
            collector.raise_all("Batch processing failed")
    else:
        logger.success("All {} items processed", len(items))

def process_item(item: dict) -> None:
    # Process individual item
    validate(item)
    save_to_db(item)
```

## Configuration Loading with Validation

```python
from errortools import (
    BaseErrorCodes,
    ignore,
    ConfigurationWarning,
    logger
)

def load_config(path: str) -> dict:
    with ignore(FileNotFoundError) as err:
        with open(path) as f:
            config = json.load(f)
    
    if err.be_ignore:
        ConfigurationWarning.emit(f"Config file {path} not found, using defaults")
        config = get_default_config()
    
    # Validate required fields
    required = ["host", "port", "database"]
    missing = [k for k in required if k not in config]
    
    if missing:
        raise BaseErrorCodes.configuration_error(
            f"Missing required config: {', '.join(missing)}"
        )
    
    logger.info("Configuration loaded from {}", path)
    return config
```

## Hot Path Optimization

```python
from errortools.future import super_fast_ignore

def process_large_dataset(data: list[dict]) -> list[str]:
    results = []
    
    for item in data:
        # Use super_fast_ignore in tight loops
        with super_fast_ignore(KeyError, TypeError):
            # Optional field processing
            value = transform(item.get("optional_field"))
            results.append(value)
    
    return results
```

## Structured Logging in Microservices

```python
from errortools.logging import logger
from errortools import ignore

# Service initialization
logger.add("logs/service.log", rotation=50_000_000, retention=10)
logger.add(sys.stderr, level="WARNING")

def handle_request(request_id: str, user_id: int):
    # Bind request context
    req_log = logger.bind(
        request_id=request_id,
        user_id=user_id,
        service="user-service"
    )
    
    req_log.info("Request started")
    
    try:
        # Process request
        result = process_user_request(user_id)
        req_log.success("Request completed in {ms}ms", ms=result.duration)
        return result
    except Exception:
        req_log.exception("Request failed")
        raise
```

## Deprecation Management

```python
from errortools import deprecated, ignore_warns, DeprecatedWarning

@deprecated("Use new_api_v2() instead. Will be removed in v3.0")
def old_api():
    return "legacy result"

# Suppress deprecation warnings in tests
with ignore_warns(DeprecatedWarning):
    result = old_api()  # No warning emitted
```

## Exception Type Conversion

```python
from errortools import reraise

class ServiceError(Exception):
    pass

def call_external_service():
    with reraise((ConnectionError, TimeoutError), ServiceError):
        # External library calls
        response = external_lib.request()
    
    # All connection/timeout errors converted to ServiceError
    return response
```

## Error Caching for Expensive Operations

```python
from errortools import error_cache, ignore

@error_cache(maxsize=128)
def validate_user_token(token: str) -> dict:
    # Expensive validation
    if not is_valid_format(token):
        raise ValueError("Invalid token format")
    
    response = auth_service.validate(token)
    if not response.ok:
        raise PermissionError("Token validation failed")
    
    return response.data

# First call with invalid token raises and caches
with ignore(ValueError):
    validate_user_token("bad-token")

# Second call returns cached exception immediately
with ignore(ValueError):
    validate_user_token("bad-token")  # No network call

print(validate_user_token.cache_info())
# CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)
```

## Multi-Level Error Handling

```python
from errortools import (
    ContextException,
    ignore_subclass,
    logger
)

class DataError(ContextException):
    code = 6000
    default_detail = "Data processing error"

class ValidationError(DataError):
    code = 6001
    default_detail = "Validation failed"

class TransformError(DataError):
    code = 6002
    default_detail = "Transform failed"

def process_pipeline(data: dict):
    # Catch all DataError subclasses
    with ignore_subclass(DataError) as err:
        validate_data(data)
        transform_data(data)
        save_data(data)
    
    if err.be_ignore:
        logger.error(
            "Pipeline failed: {} - {}",
            err.name,
            err.exception
        )
        # Handle error or re-raise
        return None
    
    return data
```
