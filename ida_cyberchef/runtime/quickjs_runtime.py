"""QuickJS runtime adapter for CyberChef.

QuickJS is a small, embeddable JavaScript engine with ES2023 support.
It requires JSON serialization for data passing between Python and JS.

Limitations:
- Stricter typed array bounds checking breaks CyberChef's zlib.js
- Compression operations need Python stdlib fallbacks
"""

import json
from typing import Any

from .base import JSRuntime


class QuickJSRuntime(JSRuntime):
    """QuickJS-based JavaScript runtime."""

    def __init__(self):
        self._ctx = None

    @property
    def name(self) -> str:
        return "QuickJS"

    @property
    def needs_compression_fallback(self) -> bool:
        # QuickJS typed array bounds checking breaks zlib.js Huffman encoding
        return True

    def load(self, cyberchef_path: str) -> None:
        """Load CyberChef into QuickJS context."""
        import quickjs

        self._ctx = quickjs.Context()

        # Set generous limits for CyberChef operations
        self._ctx.set_memory_limit(256 * 1024 * 1024)  # 256MB
        self._ctx.set_time_limit(-1)  # No time limit

        self.setup_environment()

        # Setup CommonJS module wrapper
        self._ctx.eval("const module = { exports: {} };")

        # Load CyberChef
        with open(cyberchef_path, "rb") as f:
            cyberchef_code = f.read().decode("utf-8")
        self._ctx.eval(cyberchef_code)

        # Store reference for bake operations
        self._ctx.eval("globalThis._cyberchef = module.exports;")

    def setup_environment(self) -> None:
        """Set up browser/Node polyfills for CyberChef."""
        self._ctx.eval("""
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
                    if (bytes instanceof ArrayBuffer) {
                        bytes = new Uint8Array(bytes);
                    }
                    const utf8 = Array.from(bytes).map(b => String.fromCharCode(b)).join('');
                    try {
                        return decodeURIComponent(escape(utf8));
                    } catch (e) {
                        return utf8;
                    }
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

        // Console polyfill
        if (typeof console === 'undefined') {
            globalThis.console = {
                log: function() {},
                warn: function() {},
                error: function() {},
                info: function() {},
                debug: function() {}
            };
        }
        """)

    def bake(self, input_dish: dict[str, Any], recipe: list) -> dict[str, Any]:
        """Execute CyberChef bake via JSON serialization."""
        if self._ctx is None:
            raise RuntimeError("QuickJS runtime not loaded. Call load() first.")

        # DishType constants
        ARRAY_BUFFER = 4
        BYTE_ARRAY = 0
        STRING = 1

        input_json = json.dumps(input_dish)
        recipe_json = json.dumps(recipe)

        result_json = self._ctx.eval(f"""
        (function() {{
            const inputDish = {input_json};
            const recipe = {recipe_json};

            // Create proper Dish object
            let dish;
            if (inputDish.type === {ARRAY_BUFFER} || inputDish.type === {BYTE_ARRAY}) {{
                const uint8 = new Uint8Array(inputDish.value);
                dish = new _cyberchef.Dish(uint8.buffer, _cyberchef.Dish.ARRAY_BUFFER);
            }} else if (inputDish.type === {STRING}) {{
                dish = new _cyberchef.Dish(inputDish.value, _cyberchef.Dish.STRING);
            }} else {{
                dish = new _cyberchef.Dish(inputDish.value, inputDish.type);
            }}

            // Execute bake
            const result = _cyberchef.bake(dish, recipe);

            // Convert result to JSON-serializable format
            const resultType = result.type;
            let resultValue = result.value;

            if (resultType === _cyberchef.Dish.ARRAY_BUFFER || resultType === _cyberchef.Dish.BYTE_ARRAY) {{
                if (resultValue instanceof ArrayBuffer) {{
                    resultValue = Array.from(new Uint8Array(resultValue));
                }} else if (resultValue instanceof Uint8Array) {{
                    resultValue = Array.from(resultValue);
                }}
            }}

            return JSON.stringify({{
                value: resultValue,
                type: resultType
            }});
        }})()
        """)

        return json.loads(result_json)
