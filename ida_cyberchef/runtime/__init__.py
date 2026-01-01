"""JavaScript runtime abstraction for CyberChef.

This module provides a unified interface for different JavaScript engines:
- QuickJS: Small, embeddable, always available as fallback
- STPyV8: Google V8 bindings, best compatibility
- PythonMonkey: Mozilla SpiderMonkey bindings

Usage:
    from ida_cyberchef.runtime import get_runtime, JSRuntime

    runtime = get_runtime()  # Auto-detect best available
    runtime.load("/path/to/CyberChef.js")
    result = runtime.bake(input_dish, recipe)
"""

from typing import TYPE_CHECKING

from .base import JSRuntime

if TYPE_CHECKING:
    pass

__all__ = ["JSRuntime", "get_runtime", "get_available_runtimes", "RuntimeNotAvailableError"]


class RuntimeNotAvailableError(ImportError):
    """Raised when no JavaScript runtime is available."""

    pass


def _try_import_quickjs() -> bool:
    """Check if QuickJS is available."""
    try:
        import quickjs  # noqa: F401

        return True
    except ImportError:
        return False


def _try_import_stpyv8() -> bool:
    """Check if STPyV8 is available."""
    try:
        import STPyV8  # noqa: F401

        return True
    except ImportError:
        return False


def _try_import_pythonmonkey() -> bool:
    """Check if PythonMonkey is available."""
    try:
        import pythonmonkey  # noqa: F401

        return True
    except ImportError:
        return False


def get_available_runtimes() -> list[str]:
    """Get list of available runtime names.

    Returns:
        List of available runtime names in order of preference
    """
    available = []

    # Order of preference: STPyV8 > PythonMonkey > QuickJS
    # STPyV8 has best compatibility (V8 engine, zlib works)
    # PythonMonkey is SpiderMonkey-based, good compatibility
    # QuickJS always available as fallback but needs compression workarounds

    if _try_import_stpyv8():
        available.append("stpyv8")
    if _try_import_pythonmonkey():
        available.append("pythonmonkey")
    if _try_import_quickjs():
        available.append("quickjs")

    return available


def get_runtime(preferred: str | None = None) -> JSRuntime:
    """Get JavaScript runtime instance.

    Args:
        preferred: Preferred runtime name ('quickjs', 'stpyv8', 'pythonmonkey').
                  If None, auto-selects best available.

    Returns:
        JSRuntime instance

    Raises:
        RuntimeNotAvailableError: If no runtime is available
        ValueError: If preferred runtime is not recognized
    """
    available = get_available_runtimes()

    if not available:
        raise RuntimeNotAvailableError(
            "No JavaScript runtime available. Install one of: "
            "quickjs, stpyv8, pythonmonkey"
        )

    # If preferred is specified, try to use it
    if preferred is not None:
        preferred = preferred.lower()
        valid_runtimes = {"quickjs", "stpyv8", "pythonmonkey"}

        if preferred not in valid_runtimes:
            raise ValueError(
                f"Unknown runtime '{preferred}'. Valid options: {valid_runtimes}"
            )

        if preferred not in available:
            raise RuntimeNotAvailableError(
                f"Requested runtime '{preferred}' is not available. "
                f"Available runtimes: {available}"
            )

        return _create_runtime(preferred)

    # Auto-select best available (first in preference order)
    return _create_runtime(available[0])


def _create_runtime(name: str) -> JSRuntime:
    """Create runtime instance by name.

    Args:
        name: Runtime name (lowercase)

    Returns:
        JSRuntime instance
    """
    if name == "quickjs":
        from .quickjs_runtime import QuickJSRuntime

        return QuickJSRuntime()
    elif name == "stpyv8":
        from .stpyv8_runtime import STPyV8Runtime

        return STPyV8Runtime()
    elif name == "pythonmonkey":
        from .pythonmonkey_runtime import PythonMonkeyRuntime

        return PythonMonkeyRuntime()
    else:
        raise ValueError(f"Unknown runtime: {name}")
