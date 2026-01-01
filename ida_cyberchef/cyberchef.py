import json
from enum import IntEnum
from typing import Any, TypedDict

import quickjs

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

    Returns: CyberChef module exports object (QuickJS Context)
    """
    global _chef_instance
    if _chef_instance is None:
        _chef_instance = load_cyberchef()
    return _chef_instance


def load_cyberchef(path: str | None = None):
    """Load CyberChef bundle into QuickJS context and return exports.

    Args:
        path: Path to CyberChef.js bundle. If None, uses package data path.

    Returns: QuickJS Context with CyberChef loaded
    """
    if path is None:
        from pathlib import Path

        path = str(Path(__file__).parent / "data" / "CyberChef.js")

    ctx = quickjs.Context()

    # Set generous limits for CyberChef operations
    ctx.set_memory_limit(256 * 1024 * 1024)  # 256MB
    ctx.set_time_limit(-1)  # No time limit initially

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

    # Setup minimal CommonJS environment
    ctx.eval("const module = { exports: {} };")

    # Load and execute CyberChef
    with open(path, "rb") as f:
        cyberchef_code = f.read().decode("utf-8")
    ctx.eval(cyberchef_code)

    # Store reference to exports
    ctx.eval("globalThis._cyberchef = module.exports;")

    return ctx


def plate(v: Dish | Any, chef=None) -> Dish | Any:
    """Convert between Python types and CyberChef Dish objects.

    Args:
        v: Either a Dish object or a native Python type
        chef: Optional CyberChef context (QuickJS Context) for creating proper Dish instances from bytes

    Returns: Native Python type if input is Dish, Dish dict/instance if input is Python type
    """
    is_dish_object = isinstance(v, dict) and "value" in v and "type" in v

    if is_dish_object:
        dish_type = DishType(int(v["type"]))
        value = v["value"]

        if dish_type == DishType.BYTE_ARRAY:
            if isinstance(value, list):
                if value and isinstance(value[0], float):
                    return bytes(int(x) for x in value)
                elif value and isinstance(value[0], int):
                    return bytes(value)
                return b""
            return value if isinstance(value, bytes) else b""
        elif dish_type == DishType.STRING:
            return str(value)
        elif dish_type == DishType.NUMBER:
            return float(value)
        elif dish_type == DishType.HTML:
            return str(value)
        elif dish_type == DishType.ARRAY_BUFFER:
            if isinstance(value, list):
                if value and isinstance(value[0], float):
                    return bytes(int(x) for x in value)
                elif value and isinstance(value[0], int):
                    return bytes(value)
                return b""
            return value if isinstance(value, bytes) else b""
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
            return {"value": list(v), "type": int(DishType.ARRAY_BUFFER)}
        elif isinstance(v, str):
            return {"value": v, "type": int(DishType.STRING)}
        elif isinstance(v, (int, float)):
            return {"value": v, "type": int(DishType.NUMBER)}
        elif isinstance(v, (dict, list)):
            return {"value": v, "type": int(DishType.JSON)}
        else:
            return {"value": str(v), "type": int(DishType.STRING)}


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

    # Convert input to Dish format
    if isinstance(input_data, bytes):
        input_dish = plate(input_data)
    elif isinstance(input_data, str):
        input_dish = plate(input_data)
    else:
        input_dish = {"value": input_data, "type": int(DishType.STRING)}

    input_json = json.dumps(input_dish)
    recipe_json = json.dumps(recipe)

    # Execute bake and get result as JSON
    result_json = chef.eval(f"""
    (function() {{
        const inputDish = {input_json};
        const recipe = {recipe_json};

        // Create a proper Dish object from the input
        let dish;
        if (inputDish.type === {int(DishType.ARRAY_BUFFER)} || inputDish.type === {int(DishType.BYTE_ARRAY)}) {{
            const uint8 = new Uint8Array(inputDish.value);
            dish = new _cyberchef.Dish(uint8.buffer, _cyberchef.Dish.ARRAY_BUFFER);
        }} else if (inputDish.type === {int(DishType.STRING)}) {{
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
            }} else if (Array.isArray(resultValue)) {{
                resultValue = resultValue;
            }}
        }}

        return JSON.stringify({{
            value: resultValue,
            type: resultType
        }});
    }})()
    """)

    result = json.loads(result_json)
    return plate(result)  # type: ignore[return-value]
