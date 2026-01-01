import json
from enum import IntEnum
from typing import Any, TypedDict

import STPyV8

_chef_instance = None


class DishType(IntEnum):
    """CyberChef Dish type enumeration."""

    BYTE_ARRAY = 0
    STRING = 1
    NUMBER = 2
    HTML = 3
    ARRAY_BUFFER = 4
    BIG_NUMBER = 5
    JSON = 6
    FILE = 7
    LIST_FILE = 8


class Dish(TypedDict):
    """CyberChef Dish object structure."""

    value: Any
    type: DishType


class RecipeOperation(TypedDict, total=False):
    """CyberChef recipe operation structure.

    Either a string operation name or a dict with op and args.
    """

    op: str
    args: dict[str, Any]


def get_chef():
    """Get or create a cached CyberChef instance.

    Returns: CyberChef module exports object
    """
    global _chef_instance
    if _chef_instance is None:
        _chef_instance = load_cyberchef()
    return _chef_instance


def load_cyberchef(path: str | None = None):
    """Load CyberChef bundle into V8 context and return exports.

    Args:
        path: Path to CyberChef.js bundle. If None, uses package data path.

    Returns: CyberChef module exports object
    """
    if path is None:
        from pathlib import Path

        path = str(Path(__file__).parent / "data" / "CyberChef.js")
    ctx = STPyV8.JSContext()
    ctx.enter()

    # Setup minimal global environment for CyberChef
    ctx.eval("""
    globalThis.global = globalThis;
    globalThis.window = globalThis;
    globalThis.self = globalThis;
    globalThis.document = {};

    // CyberChef app polyfill for window.app.options
    // The 'From Charcode' and similar operations check window.app.options.attemptHighlight
    // to control syntax highlighting behavior. In non-browser environments, we disable it.
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

    // Timer polyfills (minimal implementation for CyberChef)
    globalThis.setTimeout = function(fn, ms) {
        fn();
        return 0;
    };
    globalThis.setInterval = function(fn, ms) {
        return 0;
    };
    globalThis.clearTimeout = function(id) {};
    globalThis.clearInterval = function(id) {};
    """)

    # Setup minimal CommonJS environment
    ctx.eval("const module = { exports: {} };")

    # Load and execute CyberChef
    with open(path, "rb") as f:
        ctx.eval(f.read().decode("utf-8"))

    # Fix for operations that return Promises but aren't detected as async
    # Some operations like Bzip2 Compress return Promises manually instead of using async/await
    # The CyberChef wrapper only detects async functions, not Promise-returning functions
    # We need to patch these wrapped operations to handle Promises correctly
    ctx.eval("""
    (function() {
        // List of operations known to return Promises but not marked as async
        const asyncOps = ['bzip2Compress', 'bzip2Decompress', 'LZMACompress', 'LZMADecompress'];

        asyncOps.forEach(opName => {
            if (module.exports[opName]) {
                const originalOp = module.exports[opName];
                module.exports[opName] = function(...args) {
                    globalThis.__patchCalled = globalThis.__patchCalled || [];
                    globalThis.__patchCalled.push(opName);

                    try {
                        const result = originalOp.apply(this, args);
                        // If result is a Promise, we need to wait for it in our sync environment
                        if (result && typeof result.then === 'function') {
                            let resolved = false;
                            let finalResult = null;
                            let error = null;

                            result.then(r => {
                                resolved = true;
                                finalResult = r;
                            }).catch(e => {
                                resolved = true;
                                error = e;
                            });

                            // The promise should resolve immediately in our environment
                            // but pump a few times to be sure
                            let attempts = 0;
                            while (!resolved && attempts < 1000) {
                                attempts++;
                            }

                            if (error) throw error;
                            if (!resolved) throw new Error('Promise did not resolve in time');
                            return finalResult;
                        }
                        return result;
                    } catch (e) {
                        globalThis.__patchError = e.message;
                        throw e;
                    }
                };
                // Copy properties from original
                module.exports[opName].opName = originalOp.opName;
            }
        });
    })();
    """)

    # Extract exports and attach context for later use
    chef = ctx.eval("module.exports")
    chef._stpyv8_context = ctx
    return chef


def plate(v: Dish | Any, chef=None) -> Dish | Any:
    """Convert between Python types and CyberChef Dish objects.

    Args:
        v: Either a Dish object or a native Python type
        chef: Optional CyberChef module for creating proper Dish instances from bytes

    Returns: Native Python type if input is Dish, Dish dict/instance if input is Python type
    """
    is_dish_object = (isinstance(v, dict) and "value" in v and "type" in v) or (
        hasattr(v, "value") and hasattr(v, "type")
    )

    if is_dish_object:
        dish_type = DishType(int(v["type"] if isinstance(v, dict) else v.type))
        value = v["value"] if isinstance(v, dict) else v.value

        if dish_type == DishType.BYTE_ARRAY:
            if isinstance(value, list) or hasattr(value, "__iter__"):
                value_list = list(value) if not isinstance(value, list) else value
                if value_list and isinstance(value_list[0], float):
                    return bytes(int(v) for v in value_list)
                elif value_list and isinstance(value_list[0], int):
                    return bytes(value_list)
                elif value_list:
                    raise NotImplementedError
                return b""

            return value
        elif dish_type == DishType.STRING:
            return str(value)
        elif dish_type == DishType.NUMBER:
            return float(value)
        elif dish_type == DishType.HTML:
            return str(value)
        elif dish_type == DishType.ARRAY_BUFFER:
            if isinstance(value, STPyV8.JSObject):
                if chef and hasattr(chef, "_stpyv8_context"):
                    ctx = chef._stpyv8_context
                    ctx.locals.array_buffer_value = value
                    array_data = ctx.eval("""
                    (function() {
                        return Array.from(new Uint8Array(array_buffer_value));
                    })
                    """)()
                    return bytes(list(array_data))
                else:
                    return value
            elif isinstance(value, list) or hasattr(value, "__iter__"):
                return bytes(list(value))
            return value
        elif dish_type == DishType.BIG_NUMBER:
            return int(value) if isinstance(value, (int, float)) else value
        elif dish_type == DishType.JSON:
            return value
        elif dish_type in (DishType.FILE, DishType.LIST_FILE):
            return value
        else:
            return value
    else:
        if isinstance(v, bytes):
            if chef is not None and hasattr(chef, "_stpyv8_context"):
                byte_list = list(v)
                byte_json = json.dumps(byte_list)
                ctx = chef._stpyv8_context
                dish = ctx.eval(f"""
                (function() {{
                    const byteArray = {byte_json};
                    const uint8 = new Uint8Array(byteArray);
                    return new module.exports.Dish(uint8.buffer, module.exports.Dish.ARRAY_BUFFER);
                }})
                """)()
                return dish
            else:
                return {"value": list(v), "type": DishType.ARRAY_BUFFER}
        elif isinstance(v, str):
            if chef is not None and hasattr(chef, "_stpyv8_context"):
                str_json = json.dumps(v)
                ctx = chef._stpyv8_context
                dish = ctx.eval(f"""
                (function() {{
                    const str = {str_json};
                    return new module.exports.Dish(str, module.exports.Dish.STRING);
                }})
                """)()
                return dish
            else:
                return {"value": v, "type": DishType.STRING}
        elif isinstance(v, (int, float)):
            return {"value": v, "type": DishType.NUMBER}
        elif isinstance(v, (dict, list)):
            return {"value": v, "type": DishType.JSON}
        else:
            return {"value": str(v), "type": DishType.STRING}


def bake(input_data: bytes | str, recipe: list[str | RecipeOperation]) -> bytes | str:
    """Execute CyberChef operations using native bake() function.

    Args:
        input_data: Input data as bytes or string
        recipe: List of operations. Each operation is either:
            - A string operation name: "To Base64"
            - A dict with op and args: {"op": "SHA2", "args": {"size": 256}}

    Returns: Result as bytes or string depending on the final operation output
    """
    chef = get_chef()

    if isinstance(input_data, bytes):
        input_dish = plate(input_data, chef)
    elif isinstance(input_data, str):
        input_dish = plate(input_data, chef)
    else:
        input_dish = input_data

    recipe_json = json.dumps(recipe)

    ctx = chef._stpyv8_context
    ctx.locals.input_dish = input_dish
    result = ctx.eval(f"""
    (function() {{
        const recipe = {recipe_json};
        const result = module.exports.bake(input_dish, recipe);

        // Handle async operations that return Promises
        // For async operations, bake may return a Promise that needs to be resolved
        if (result && typeof result.then === 'function') {{
            // This is a Promise - we need to wait for it
            let resolved = false;
            let finalResult = null;
            let error = null;

            result.then(r => {{
                resolved = true;
                finalResult = r;
            }}).catch(e => {{
                resolved = true;
                error = e;
            }});

            // Pump the microtask queue until the promise resolves
            let attempts = 0;
            while (!resolved && attempts < 1000) {{
                // Each eval pumps the microtask queue
                void 0;
                attempts++;
            }}

            if (error) throw error;
            if (!resolved) throw new Error('Promise did not resolve');
            return finalResult;
        }}

        return result;
    }})
    """)()

    return plate(result, chef)  # type: ignore[return-value]
