"""Performance tests for _errortools/future.py utilities."""

import contextlib
import time


from _errortools.future import (
    super_fast_ignore,
    super_fast_catch,
    super_fast_reraise,
    ExceptionCollector,
)

ITERATIONS = 50_000


def _measure(fn, iterations=ITERATIONS):
    start = time.perf_counter_ns()
    for _ in range(iterations):
        fn()
    elapsed_ns = time.perf_counter_ns() - start
    return elapsed_ns / iterations


# =============================================================================
# Baselines (stdlib contextlib.suppress / try-except)
# =============================================================================


def _baseline_suppress():
    with contextlib.suppress(ValueError):
        raise ValueError("x")


def _baseline_try_except_ignore():
    try:
        raise ValueError("x")
    except ValueError:
        pass


def _baseline_try_except_reraise():
    try:
        raise KeyError("x")
    except KeyError as e:
        raise ValueError(str(e)) from e


# =============================================================================
# super_fast_ignore
# =============================================================================


class TestSuperFastIgnorePerf:
    def test_suppress_exception(self):
        def fn():
            with super_fast_ignore(ValueError):
                raise ValueError("x")

        ns_per = _measure(fn)
        baseline_ns = _measure(_baseline_suppress)
        ratio = ns_per / baseline_ns
        print(f"\nsuper_fast_ignore (suppress): {ns_per:.0f} ns/op, "
              f"baseline: {baseline_ns:.0f} ns/op, ratio: {ratio:.2f}x")
        assert ratio < 3.0, f"Too slow: {ratio:.2f}x vs contextlib.suppress"

    def test_no_exception(self):
        def fn():
            with super_fast_ignore(ValueError):
                pass

        def baseline():
            with contextlib.suppress(ValueError):
                pass

        ns_per = _measure(fn)
        baseline_ns = _measure(baseline)
        ratio = ns_per / baseline_ns
        print(f"\nsuper_fast_ignore (no-op): {ns_per:.0f} ns/op, "
              f"baseline: {baseline_ns:.0f} ns/op, ratio: {ratio:.2f}x")
        assert ratio < 3.0

    def test_faster_than_stdlib_suppress(self):
        def fn():
            with super_fast_ignore(ValueError):
                raise ValueError("x")

        ns_ours = _measure(fn)
        ns_stdlib = _measure(_baseline_suppress)
        print(f"\nsuper_fast_ignore: {ns_ours:.0f} ns/op vs "
              f"contextlib.suppress: {ns_stdlib:.0f} ns/op")


# =============================================================================
# super_fast_catch
# =============================================================================


class TestSuperFastCatchPerf:
    def test_catch_exception(self):
        def fn():
            with super_fast_catch(ValueError) as ctx:
                raise ValueError("x")
            _ = ctx.exception

        def baseline():
            with contextlib.suppress(ValueError):
                raise ValueError("x")

        ns_per = _measure(fn)
        baseline_ns = _measure(baseline)
        ratio = ns_per / baseline_ns
        print(f"\nsuper_fast_catch: {ns_per:.0f} ns/op, "
              f"baseline (suppress): {baseline_ns:.0f} ns/op, ratio: {ratio:.2f}x")
        assert ratio < 5.0

    def test_no_exception(self):
        def fn():
            with super_fast_catch(ValueError):
                pass

        def baseline():
            with contextlib.suppress(ValueError):
                pass

        ns_per = _measure(fn)
        baseline_ns = _measure(baseline)
        ratio = ns_per / baseline_ns
        print(f"\nsuper_fast_catch (no-op): {ns_per:.0f} ns/op, "
              f"baseline (suppress): {baseline_ns:.0f} ns/op, ratio: {ratio:.2f}x")
        assert ratio < 5.0


# =============================================================================
# super_fast_reraise
# =============================================================================


class TestSuperFastReraisePerf:
    def test_reraise_exception(self):
        def fn():
            try:
                with super_fast_reraise(KeyError, ValueError):
                    raise KeyError("x")
            except ValueError:
                pass

        def baseline():
            try:
                _baseline_try_except_reraise()
            except ValueError:
                pass

        ns_per = _measure(fn)
        baseline_ns = _measure(baseline)
        ratio = ns_per / baseline_ns
        print(f"\nsuper_fast_reraise: {ns_per:.0f} ns/op, "
              f"baseline: {baseline_ns:.0f} ns/op, ratio: {ratio:.2f}x")
        assert ratio < 5.0


# =============================================================================
# ExceptionCollector
# =============================================================================


class TestExceptionCollectorPerf:
    def test_catch_many(self):
        def fn():
            c = ExceptionCollector()
            for _ in range(100):
                c.catch(int, "bad")

        def baseline():
            errs = []
            for _ in range(100):
                try:
                    int("bad")
                except Exception as e:
                    errs.append(e)

        iters = ITERATIONS // 10
        ns_per = _measure(fn, iters)
        baseline_ns = _measure(baseline, iters)
        ratio = ns_per / baseline_ns
        print(f"\nExceptionCollector.catch x100: {ns_per:.0f} ns/op, "
              f"baseline: {baseline_ns:.0f} ns/op, ratio: {ratio:.2f}x")
        assert ratio < 5.0

    def test_add_many(self):
        exc = ValueError("x")

        def fn():
            c = ExceptionCollector()
            for _ in range(1000):
                c.add(exc)

        def baseline():
            errs = []
            for _ in range(1000):
                errs.append(exc)

        iters = ITERATIONS // 50
        ns_per = _measure(fn, iters)
        baseline_ns = _measure(baseline, iters)
        ratio = ns_per / baseline_ns
        print(f"\nExceptionCollector.add x1000: {ns_per:.0f} ns/op, "
              f"baseline: {baseline_ns:.0f} ns/op, ratio: {ratio:.2f}x")
        assert ratio < 5.0

    def test_context_manager_overhead(self):
        def fn():
            with ExceptionCollector():
                pass

        def baseline():
            try:
                pass
            except Exception:
                pass

        ns_per = _measure(fn)
        baseline_ns = _measure(baseline)
        ratio = ns_per / baseline_ns
        print(f"\nExceptionCollector CM overhead: {ns_per:.0f} ns/op, "
              f"baseline: {baseline_ns:.0f} ns/op, ratio: {ratio:.2f}x")
        assert ratio < 20.0
