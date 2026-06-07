"""Tests for _errortools/plugins — ultra-lightweight plugin system."""

import pytest

from _errortools.plugins import (
    register,
    get,
    has,
    run,
    list_all,
    remove,
    clear,
    Registry,
)

# =============================================================================
# register & run
# =============================================================================


class TestPluginRegisterAndRun:
    def test_register_decorator(self):
        @register("test_func")
        def f():
            return "ok"

        assert run("test_func") == "ok"

    def test_run_raises_when_not_registered(self):
        with pytest.raises(ValueError, match="Plugin 'nonexistent' is not registered"):
            run("nonexistent")

    def test_plugin_with_args_kwargs(self):
        @register("add")
        def add(a, b):
            return a + b

        assert run("add", 2, 3) == 5
        assert run("add", a=10, b=20) == 30

    def test_get_returns_correct_function(self):
        @register("myfunc")
        def f():
            return "test"

        assert get("myfunc") is f

    def test_get_with_default(self):
        assert get("missing", default=42) == 42

    def test_get_with_none_default(self):
        assert get("missing", default=None) is None

    def test_register_overwrites(self):
        @register("overwrite_me")
        def first():
            return "first"

        @register("overwrite_me")
        def second():
            return "second"

        assert run("overwrite_me") == "second"

    def test_run_forwards_all_args(self):
        @register("variadic")
        def variadic(*args, **kwargs):
            return (args, kwargs)

        assert run("variadic", 1, 2, x=3) == ((1, 2), {"x": 3})


# =============================================================================
# has
# =============================================================================


class TestPluginHas:
    def test_has_true(self):
        @register("exists")
        def f():
            pass

        assert has("exists") is True

    def test_has_false(self):
        assert has("never_registered") is False


# =============================================================================
# list_all
# =============================================================================


class TestPluginList:
    def test_list_all_includes_registered_plugins(self):
        @register("plugin1")
        def f1():
            pass

        @register("plugin2")
        def f2():
            pass

        plugins = list_all()
        assert "plugin1" in plugins
        assert "plugin2" in plugins


# =============================================================================
# remove
# =============================================================================


class TestPluginRemove:
    def test_remove_existing_plugin(self):
        @register("toremove")
        def f():
            pass

        remove("toremove")
        with pytest.raises(ValueError):
            get("toremove")

    def test_remove_nonexistent_is_safe(self):
        # Should not raise
        remove("never_existed")

    def test_remove_returns_none(self):
        @register("for_remove")
        def f():
            pass

        assert remove("for_remove") is None


# =============================================================================
# clear
# =============================================================================


class TestPluginClear:
    def test_clear_removes_all(self):
        @register("a")
        def a():
            pass

        @register("b")
        def b():
            pass

        clear()
        assert list_all() == []
        assert has("a") is False
        assert has("b") is False


# =============================================================================
# Registry class (static)
# =============================================================================


class TestRegistryClass:
    def test_static_register_and_get(self):
        def my_static_func():
            return "static"

        Registry.register("static_plugin", my_static_func)
        assert Registry.get("static_plugin") is my_static_func

    def test_static_list_all(self):
        @register("listme")
        def f():
            pass

        assert "listme" in Registry.list_all()

    def test_registry_get_raises_when_missing(self):
        with pytest.raises(ValueError, match="Plugin 'missing' is not registered"):
            Registry.get("missing")

    def test_registry_register_overwrites(self):
        def first():
            return "first"

        def second():
            return "second"

        Registry.register("overwrite_registry", first)
        assert Registry.get("overwrite_registry") is first
        Registry.register("overwrite_registry", second)
        assert Registry.get("overwrite_registry") is second

    def test_registry_remove(self):
        @register("registry_remove_me")
        def f():
            pass

        Registry.remove("registry_remove_me")
        assert has("registry_remove_me") is False
