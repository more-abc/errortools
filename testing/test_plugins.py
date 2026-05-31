"""Tests for _errortools/plugins — ultra-lightweight plugin system."""

import pytest

from _errortools.plugins import (
    register,
    get,
    run,
    list_all,
    remove,
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
