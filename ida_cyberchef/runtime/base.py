"""Abstract base class for JavaScript runtime adapters.

Each runtime (QuickJS, STPyV8, PythonMonkey) implements this interface
to provide CyberChef execution capabilities.
"""

from abc import ABC, abstractmethod
from typing import Any


class JSRuntime(ABC):
    """Abstract base class for JavaScript runtimes.

    Implementations must provide:
    - Loading CyberChef bundle
    - Executing bake() with input dish and recipe
    - Converting results back to Python types
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this runtime."""
        ...

    @property
    def needs_compression_fallback(self) -> bool:
        """Whether this runtime needs Python fallbacks for compression.

        QuickJS has stricter typed array bounds checking that breaks
        CyberChef's zlib.js. STPyV8 (V8) handles it fine.

        Returns:
            True if compression operations should use Python stdlib
        """
        return False

    @abstractmethod
    def load(self, cyberchef_path: str) -> None:
        """Load CyberChef bundle into the runtime.

        Args:
            cyberchef_path: Path to CyberChef.js bundle file
        """
        ...

    @abstractmethod
    def bake(self, input_dish: dict[str, Any], recipe: list) -> dict[str, Any]:
        """Execute CyberChef bake operation.

        Args:
            input_dish: Input data as Dish dict with 'value' and 'type' keys
            recipe: List of operations (strings or dicts with 'op' and 'args')

        Returns:
            Result Dish dict with 'value' and 'type' keys
        """
        ...

    def setup_environment(self) -> None:
        """Set up minimal browser/Node environment for CyberChef.

        Override if runtime needs custom setup. Default implementation
        provides common polyfills via eval().
        """
        pass
