"""PythonMonkey runtime adapter for CyberChef.

PythonMonkey embeds Mozilla's SpiderMonkey JavaScript engine into Python.
It provides seamless interop between Python and JavaScript via proxy objects.

Advantages:
- SpiderMonkey engine (same as Firefox)
- Direct proxy object interop without JSON serialization
- WebAssembly support
- Active development

Note:
- Compression compatibility needs testing; may or may not need fallbacks
"""

import json
from typing import Any

from .base import JSRuntime


class PythonMonkeyRuntime(JSRuntime):
    """PythonMonkey (SpiderMonkey) JavaScript runtime."""

    def __init__(self):
        self._pm = None
        self._cyberchef = None
        self._needs_compression_fallback = None  # Determined at runtime

    @property
    def name(self) -> str:
        return "PythonMonkey"

    @property
    def needs_compression_fallback(self) -> bool:
        # Test compression on first use if not yet determined
        if self._needs_compression_fallback is None:
            self._needs_compression_fallback = self._test_compression()
        return self._needs_compression_fallback

    def _test_compression(self) -> bool:
        """Test if zlib.js works in this runtime."""
        if self._cyberchef is None:
            # Can't test yet, assume it needs fallback to be safe
            return True

        try:
            # Try a simple compression operation
            test_dish = {"value": list(b"test"), "type": 4}  # ARRAY_BUFFER
            self.bake(test_dish, ["Zlib Deflate"])
            return False  # Compression works!
        except Exception:
            return True  # Needs fallback

    def load(self, cyberchef_path: str) -> None:
        """Load CyberChef into SpiderMonkey context."""
        import pythonmonkey as pm

        self._pm = pm

        # Setup global environment
        self.setup_environment()

        # Load CyberChef via eval
        # PythonMonkey uses eval() directly on the module
        with open(cyberchef_path, "rb") as f:
            cyberchef_code = f.read().decode("utf-8")

        # Wrap in module pattern and execute
        wrapper = f"""
        (function() {{
            const module = {{ exports: {{}} }};
            {cyberchef_code}
            return module.exports;
        }})()
        """
        self._cyberchef = pm.eval(wrapper)

    def setup_environment(self) -> None:
        """Set up browser/Node polyfills for CyberChef."""
        self._pm.eval("""
        globalThis.global = globalThis;
        globalThis.window = globalThis;
        globalThis.self = globalThis;
        globalThis.document = {};

        // Minimal process polyfill
        globalThis.process = {
            platform: 'linux',
            env: {},
            cwd: () => '/',
            version: 'v18.0.0',
            versions: {node: 'v18.0.0'},
            nextTick: (fn) => fn()
        };

        // Timer polyfills
        if (typeof setTimeout === 'undefined') {
            globalThis.setTimeout = function(fn, ms) { fn(); return 0; };
        }
        if (typeof setInterval === 'undefined') {
            globalThis.setInterval = function(fn, ms) { return 0; };
        }
        globalThis.clearTimeout = globalThis.clearTimeout || function(id) {};
        globalThis.clearInterval = globalThis.clearInterval || function(id) {};
        """)

    def bake(self, input_dish: dict[str, Any], recipe: list) -> dict[str, Any]:
        """Execute CyberChef bake with SpiderMonkey proxy objects."""
        if self._cyberchef is None:
            raise RuntimeError("PythonMonkey runtime not loaded. Call load() first.")

        # DishType constants
        ARRAY_BUFFER = 4
        BYTE_ARRAY = 0
        STRING = 1

        dish_type = input_dish.get("type", STRING)
        dish_value = input_dish.get("value")

        # Create JS Dish object
        if dish_type in (ARRAY_BUFFER, BYTE_ARRAY) and isinstance(dish_value, list):
            # Create Uint8Array and Dish
            byte_json = json.dumps(dish_value)
            recipe_json = json.dumps(recipe)

            result = self._pm.eval(f"""
            (function(cyberchef) {{
                const byteArray = {byte_json};
                const uint8 = new Uint8Array(byteArray);
                const dish = new cyberchef.Dish(uint8.buffer, cyberchef.Dish.ARRAY_BUFFER);
                const recipe = {recipe_json};
                return cyberchef.bake(dish, recipe);
            }})
            """)(self._cyberchef)
        else:
            # String input
            recipe_json = json.dumps(recipe)
            value_json = json.dumps(dish_value)

            result = self._pm.eval(f"""
            (function(cyberchef) {{
                const dish = new cyberchef.Dish({value_json}, cyberchef.Dish.STRING);
                const recipe = {recipe_json};
                return cyberchef.bake(dish, recipe);
            }})
            """)(self._cyberchef)

        # Convert result to Python dict
        return self._convert_result(result)

    def _convert_result(self, result) -> dict[str, Any]:
        """Convert SpiderMonkey Dish proxy to Python dict."""
        result_type = int(result.type)
        result_value = result.value

        # DishType constants
        ARRAY_BUFFER = 4
        BYTE_ARRAY = 0

        if result_type in (ARRAY_BUFFER, BYTE_ARRAY):
            # Convert typed array to Python list
            if hasattr(result_value, "__iter__"):
                try:
                    result_value = list(result_value)
                except Exception:
                    # Fallback: convert via JSON
                    result_value = list(self._pm.eval("""
                    (function(v) { return Array.from(new Uint8Array(v)); })
                    """)(result_value))
            elif isinstance(result_value, (bytes, bytearray)):
                result_value = list(result_value)

        return {"value": result_value, "type": result_type}
