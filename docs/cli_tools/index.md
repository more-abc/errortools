# Command-Line Interface

errortools ships two CLI entry points: `python -m errortools` for package information, and `logger` for emitting log messages from the shell.

## Installation

Both commands become available after installing the package:

```bash
pip install errortools
```

## `errortools` command

Display package metadata and run tests.

### Usage

```bash
python -m errortools [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--version` | `-v` | Show version and exit |
| `--copyrights` | `-c` | Show copyright information |
| `--author` | `-a` | Show author name |
| `--email` | `-e` | Show author email |
| `--license` | `-l` | Show license type |
| `--url` | `-u` | Show project URL |
| `--info` | `-i` | Show all package information |
| `--run-tests` | | Run the test suite using pytest |

### Examples

```bash
# Print version
$ python -m errortools -v
v3.1.2

# Print all metadata
$ python -m errortools -i
errortools vx.x.x
  errortools - a toolset for working with Python exceptions and warnings and logging.
  Author:    Evan Yang <quantbit@126.com>
  License:   MIT
  URL:       https://github.com/more-abc/errortools
  Copyright: Copyright 2026 (C) aiwonderland Evan Yang

# Run the test suite
$ errortools --run-tests
...
```

## `logger` command

Emit a single log message from the command line using the errortools structured logger.

### Usage

```bash
logger MESSAGE [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--level` | `-l` | Log level: `trace`, `debug`, `info`, `success`, `warning`, `error`, `critical` (default: `info`) |
| `--output` | `-o` | Output stream: `stderr` or `stdout` (default: `stderr`) |

### Examples

```bash
# Info-level message (default)
$ logger "Deployment complete"

# Error-level message
$ logger "Connection failed" -l error

# Write to stdout instead of stderr
$ logger "Build started" -l info -o stdout
```

### Interactive shell

Launch an interactive Python REPL with pre-imported logging shortcuts:

```bash
logger shell
```

```
errortools Logger Shell REPL 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)] on win32
Pre-imported shortcuts: info, debug, error, warning, critical, trace, success, exception, catch
Pre-imported types: logger, Level, LEVELS, BaseLogger, Record, StreamSink, FileSink, CallableSink
Pre-imported std-lib: Logger, Handler, Filter, Formatter
Type "help", "copyright", "credits" or "license" for more information.
>>> info("Hello from the shell")
>>> debug("Variable x = {}", 42)
>>> with catch():
...     1 / 0
```
