"""Tests for the JavaScript runtime abstraction layer."""

import pytest

from ida_cyberchef.runtime import (
    JSRuntime,
    get_available_runtimes,
    get_runtime,
    RuntimeNotAvailableError,
)
from ida_cyberchef.cyberchef import bake, get_chef, set_runtime, load_cyberchef


class TestRuntimeDiscovery:
    """Test runtime discovery and selection."""

    def test_get_available_runtimes(self):
        """At least one runtime should be available."""
        available = get_available_runtimes()
        assert len(available) > 0
        assert "quickjs" in available  # QuickJS is always our fallback

    def test_get_runtime_returns_jsruntime(self):
        """get_runtime should return a JSRuntime instance."""
        runtime = get_runtime()
        assert isinstance(runtime, JSRuntime)

    def test_get_runtime_quickjs(self):
        """Explicitly request QuickJS runtime."""
        runtime = get_runtime("quickjs")
        assert runtime.name == "QuickJS"

    def test_get_runtime_invalid(self):
        """Invalid runtime name should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown runtime"):
            get_runtime("nonexistent")


class TestRuntimeInterface:
    """Test runtime interface compliance."""

    def test_runtime_has_name(self):
        """Runtime should have a name property."""
        runtime = get_runtime()
        assert isinstance(runtime.name, str)
        assert len(runtime.name) > 0

    def test_runtime_needs_compression_fallback(self):
        """Runtime should report compression fallback requirement."""
        runtime = get_runtime()
        assert isinstance(runtime.needs_compression_fallback, bool)

    def test_quickjs_needs_compression_fallback(self):
        """QuickJS should need compression fallback."""
        runtime = get_runtime("quickjs")
        assert runtime.needs_compression_fallback is True


class TestRuntimeExecution:
    """Test runtime execution capabilities."""

    def test_load_cyberchef(self):
        """Test loading CyberChef into runtime."""
        runtime = load_cyberchef()
        assert runtime is not None
        assert isinstance(runtime, JSRuntime)

    def test_bake_basic(self):
        """Test basic bake operation through runtime."""
        result = bake("hello", ["To Base64"])
        assert result == "aGVsbG8="

    def test_bake_bytes_input(self):
        """Test bake with bytes input."""
        result = bake(b"hello", ["To Hex"])
        assert "68 65 6c 6c 6f" in result

    def test_bake_chain(self):
        """Test chained operations."""
        result = bake("hello", ["To Base64", "From Base64"])
        assert result == b"hello"

    def test_set_runtime(self):
        """Test setting custom runtime."""
        # Clear runtime
        set_runtime(None)

        # Get fresh runtime
        runtime = get_chef()
        assert runtime is not None

        # Reset
        set_runtime(None)


class TestRuntimeCompression:
    """Test compression with runtime fallbacks."""

    def test_compression_with_quickjs(self):
        """Compression should work via Python fallback with QuickJS."""
        set_runtime(None)  # Clear cached runtime

        # Force QuickJS
        runtime = load_cyberchef(preferred_runtime="quickjs")
        set_runtime(runtime)

        try:
            # This uses Python fallback
            result = bake(b"hello world", ["Gzip", "Gunzip"])
            assert result == b"hello world"
        finally:
            set_runtime(None)

    def test_mixed_js_and_python_ops(self):
        """Mixed JS and Python operations should work."""
        result = bake(b"hello", ["To Base64", "Gzip", "Gunzip", "From Base64"])
        assert result == b"hello"


class TestRuntimeProperties:
    """Test runtime-specific properties."""

    def test_quickjs_properties(self):
        """Test QuickJS-specific properties."""
        from ida_cyberchef.runtime.quickjs_runtime import QuickJSRuntime

        runtime = QuickJSRuntime()
        assert runtime.name == "QuickJS"
        assert runtime.needs_compression_fallback is True
