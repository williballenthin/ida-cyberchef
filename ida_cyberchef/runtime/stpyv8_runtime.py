"""STPyV8 runtime adapter for CyberChef.

STPyV8 provides Python bindings to Google's V8 JavaScript engine.
It offers direct object interop between Python and JavaScript.

Advantages:
- Full V8 compatibility (same engine as Chrome/Node.js)
- Direct Python/JS object interop without JSON serialization
- CyberChef's zlib.js works correctly

Disadvantages:
- Large binary size (~50MB)
- Complex build requirements
- Platform-specific issues
"""

import json
from typing import Any

from .base import JSRuntime


class STPyV8Runtime(JSRuntime):
    """STPyV8 (V8) JavaScript runtime."""

    def __init__(self):
        self._ctx = None
        self._chef = None

    @property
    def name(self) -> str:
        return "STPyV8"

    @property
    def needs_compression_fallback(self) -> bool:
        # V8 handles zlib.js correctly
        return False

    def load(self, cyberchef_path: str) -> None:
        """Load CyberChef into V8 context."""
        import STPyV8

        self._ctx = STPyV8.JSContext()
        self._ctx.enter()

        self.setup_environment()

        # Setup CommonJS module wrapper
        self._ctx.eval("const module = { exports: {} };")

        # Load CyberChef
        with open(cyberchef_path, "rb") as f:
            self._ctx.eval(f.read().decode("utf-8"))

        # Store reference to exports
        self._chef = self._ctx.eval("module.exports")

    def setup_environment(self) -> None:
        """Set up browser/Node polyfills for CyberChef."""
        self._ctx.eval("""
        globalThis.global = globalThis;
        globalThis.window = globalThis;
        globalThis.self = globalThis;
        globalThis.document = {};

        // CyberChef app polyfill for window.app.options
        globalThis.window.app = {
            options: {
                attemptHighlight: false
            }
        };

        // Minimal process polyfill
        globalThis.process = {
            platform: 'linux',
            env: {},
            cwd: () => '/',
            version: 'v18.0.0',
            versions: {node: 'v18.0.0'},
            nextTick: (fn) => setTimeout(fn, 0)
        };

        // TextEncoder/TextDecoder polyfill
        if (typeof TextEncoder === 'undefined') {
            globalThis.TextEncoder = class TextEncoder {
                encode(str) {
                    const utf8 = unescape(encodeURIComponent(str));
                    const result = new Uint8Array(utf8.length);
                    for (let i = 0; i < utf8.length; i++) {
                        result[i] = utf8.charCodeAt(i);
                    }
                    return result;
                }
            };
        }

        if (typeof TextDecoder === 'undefined') {
            globalThis.TextDecoder = class TextDecoder {
                decode(bytes) {
                    const utf8 = Array.from(bytes).map(b => String.fromCharCode(b)).join('');
                    return decodeURIComponent(escape(utf8));
                }
            };
        }

        // Crypto API polyfill
        if (typeof crypto === 'undefined') {
            globalThis.crypto = {};
        }
        if (!globalThis.crypto.getRandomValues) {
            globalThis.crypto.getRandomValues = function(array) {
                for (let i = 0; i < array.length; i++) {
                    array[i] = Math.floor(Math.random() * 256);
                }
                return array;
            };
        }

        // Timer polyfills
        globalThis.setTimeout = function(fn, ms) { fn(); return 0; };
        globalThis.setInterval = function(fn, ms) { return 0; };
        globalThis.clearTimeout = function(id) {};
        globalThis.clearInterval = function(id) {};
        """)

    def bake(self, input_dish: dict[str, Any], recipe: list) -> dict[str, Any]:
        """Execute CyberChef bake with direct V8 object interop."""
        import STPyV8

        if self._ctx is None:
            raise RuntimeError("STPyV8 runtime not loaded. Call load() first.")

        # DishType constants
        ARRAY_BUFFER = 4
        BYTE_ARRAY = 0

        # For bytes input, create proper Dish via JS
        dish_type = input_dish.get("type", 1)
        dish_value = input_dish.get("value")

        if dish_type in (ARRAY_BUFFER, BYTE_ARRAY) and isinstance(dish_value, list):
            # Create Dish from byte array via JS
            byte_json = json.dumps(dish_value)
            js_dish = self._ctx.eval(f"""
            (function() {{
                const byteArray = {byte_json};
                const uint8 = new Uint8Array(byteArray);
                return new module.exports.Dish(uint8.buffer, module.exports.Dish.ARRAY_BUFFER);
            }})()
            """)
        else:
            # String or other input - pass directly
            js_dish = dish_value

        # Execute bake
        recipe_json = json.dumps(recipe)
        self._ctx.locals.input_dish = js_dish
        result = self._ctx.eval(f"""
        (function() {{
            const recipe = {recipe_json};
            return module.exports.bake(input_dish, recipe);
        }})()
        """)

        # Convert result to Python dict
        return self._convert_result(result)

    def _convert_result(self, result) -> dict[str, Any]:
        """Convert V8 Dish object to Python dict."""
        import STPyV8

        result_type = int(result.type)
        result_value = result.value

        # DishType constants
        ARRAY_BUFFER = 4
        BYTE_ARRAY = 0

        if result_type in (ARRAY_BUFFER, BYTE_ARRAY):
            if isinstance(result_value, STPyV8.JSObject):
                # Convert ArrayBuffer to list via JS
                self._ctx.locals.array_buffer_value = result_value
                result_value = list(self._ctx.eval("""
                (function() {
                    return Array.from(new Uint8Array(array_buffer_value));
                })()
                """))
            elif hasattr(result_value, "__iter__"):
                result_value = list(result_value)

        return {"value": result_value, "type": result_type}
