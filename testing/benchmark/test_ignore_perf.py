"""Performance tests for _errortools/ignore.py — ErrorIgnoreWrapper.

These tests measure absolute latency (ns/op) rather than comparing against
std-lib ``contextlib.suppress``, because ``ignore`` captures full traceback
strings and exception metadata — work that ``suppress`` deliberately skips.
"""

import time
import warnings

from _errortools.ignore import ignore, fast_ignore
from _errortools.wrappers.ignore import ErrorIgnoreWrapper

ITERATIONS = 50_000


def _measure(fn, iterations=ITERATIONS):
    start = time.perf_counter_ns()
    for _ in range(iterations):
        fn()
    elapsed_ns = time.perf_counter_ns() - start
    return elapsed_ns / iterations


# =============================================================================
# ignore (ErrorIgnoreWrapper with traceback recording)
# =============================================================================


class TestIgnorePerf:
    def test_suppress_exception(self):
        def fn():
            with ignore(ValueError):
                raise ValueError("x")

        ns_per = _measure(fn)
        print(f"\nignore (suppress with traceback): {ns_per:.0f} ns/op")
        assert ns_per < 300_000

    def test_no_exception(self):
        def fn():
            with ignore(ValueError):
                pass

        ns_per = _measure(fn)
        print(f"\nignore (no-op): {ns_per:.0f} ns/op")
        assert ns_per < 50_000

    def test_as_decorator(self):
        @ignore(ZeroDivisionError)
        def func():
            return 1 / 0

        ns_per = _measure(func)
        print(f"\nignore (decorator): {ns_per:.0f} ns/op")
        assert ns_per < 300_000

    def test_reuse_resets_state(self):
        ig = ignore(ValueError)

        def fn():
            with ig:
                raise ValueError("x")

        ns_per = _measure(fn)
        print(f"\nignore (reused instance): {ns_per:.0f} ns/op")
        assert ns_per < 300_000


# =============================================================================
# fast_ignore (deprecated, no traceback)
# =============================================================================


class TestFastIgnorePerf:
    def test_suppress_exception(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)

            def fn():
                with fast_ignore(ValueError):
                    raise ValueError("x")

            ns_per = _measure(fn)
            print(f"\nfast_ignore (suppress, no traceback): {ns_per:.0f} ns/op")
            assert ns_per < 100_000

    def test_no_exception(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)

            def fn():
                with fast_ignore(ValueError):
                    pass

            ns_per = _measure(fn)
            print(f"\nfast_ignore (no-op): {ns_per:.0f} ns/op")
            assert ns_per < 100_000


# =============================================================================
# ErrorIgnoreWrapper direct
# =============================================================================


class TestErrorIgnoreWrapperPerf:
    def test_direct_ignore_perf(self):
        def fn():
            with ErrorIgnoreWrapper(KeyError):
                raise KeyError("x")

        ns_per = _measure(fn)
        print(f"\nErrorIgnoreWrapper: {ns_per:.0f} ns/op")
        assert ns_per < 300_000

    def test_direct_capture_attributes(self):
        def fn():
            with ErrorIgnoreWrapper(NameError) as err:
                raise NameError("x")
            # Touch all recorded attributes to ensure they are materialised.
            _ = err.name
            _ = err.be_ignore
            _ = err.count
            _ = err.traceback
            _ = err.exception

        ns_per = _measure(fn)
        print(f"\nErrorIgnoreWrapper (capture all): {ns_per:.0f} ns/op")
        assert ns_per < 300_000

    def test_direct_no_exception(self):
        def fn():
            with ErrorIgnoreWrapper(ValueError):
                pass

        ns_per = _measure(fn)
        print(f"\nErrorIgnoreWrapper (no-op): {ns_per:.0f} ns/op")
        assert ns_per < 50_000

    def test_direct_multiple_types(self):
        def fn():
            with ErrorIgnoreWrapper(KeyError, ValueError, TypeError):
                raise TypeError("x")

        ns_per = _measure(fn)
        print(f"\nErrorIgnoreWrapper (multiple types): {ns_per:.0f} ns/op")
        assert ns_per < 300_000
