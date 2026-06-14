# Command-Line Interface

errortools ships two CLI entry points: `python -m errortools` (or simply `errortools` after install) for package information and developer tooling, and `logger` for emitting log messages from the shell.

## Installation

Both commands become available after installing the package:

```bash
pip install errortools
```

```{note}
After installation you can use the `errortools` and `logger` console scripts directly. The examples below show both forms interchangeably.
```

## `errortools` command

Display package metadata and run the test suite.

### Usage

```bash
errortools [OPTIONS]
# or, equivalently:
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
# Print version (matches the format used by --info)
$ errortools -v
errortools 3.4.9

# Print all metadata
$ errortools -i
errortools v3.4.9
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

Emit a single log message from the command line, or open an interactive debug shell, using the errortools structured logger.

### Usage

```bash
logger <subcommand> [OPTIONS]
```

### Subcommands

| Subcommand | Description |
|------------|-------------|
| `emit` | Emit a single log message to stdout or stderr |
| `shell` | Launch an interactive logger REPL debug shell |

### `logger emit`

```bash
logger emit MESSAGE [OPTIONS]
```

#### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--level` | `-l` | Log level: `trace`, `debug`, `info`, `success`, `warning`, `error`, `critical` (default: `info`) |
| `--output` | `-o` | Output stream: `stderr` or `stdout` (default: `stderr`) |

#### Examples

```bash
# Info-level message (default) to stderr
$ logger emit "Deployment complete"

# Error-level message
$ logger emit "Connection failed" --level error

# Short flags
$ logger emit "Build started" -l info -o stdout
```

### `logger shell`

Launch an interactive Python REPL with pre-imported logging shortcuts.

#### Examples

```bash
$ logger shell
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

## Mode detection

The `errortools` module dispatches between the two CLI families by inspecting the **basename** of `sys.argv[0]`. If it resolves to `logger` (with optional `.exe` / `.py` suffix), the logger dispatcher is used; otherwise the errortools dispatcher is used. This means paths such as `my_logger_tool` are no longer mistaken for the `logger` command.
