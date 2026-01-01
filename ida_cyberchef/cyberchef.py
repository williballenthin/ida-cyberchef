"""CyberChef integration with pluggable JavaScript runtime support.

This module provides Python bindings to CyberChef operations via a
pluggable JavaScript runtime system. Supported runtimes:
- QuickJS: Small, embeddable (default fallback)
- STPyV8: Google V8 bindings (best compatibility)
- PythonMonkey: Mozilla SpiderMonkey bindings

The runtime is auto-detected based on what's installed, with fallback
to QuickJS. Some operations (compression) use Python stdlib when the
runtime has compatibility issues.
"""

import bz2
import gzip
import json
import zlib
from enum import IntEnum
from io import BytesIO
from pathlib import Path
from typing import Any, TypedDict

from .runtime import JSRuntime, get_runtime

_runtime_instance: JSRuntime | None = None


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


# =============================================================================
# Python Compression Fallbacks
# =============================================================================
# Some runtimes (QuickJS) have stricter typed array bounds checking that breaks
# CyberChef's embedded zlib.js. These Python implementations provide equivalent
# functionality using Python's standard library.


def _get_compression_level(args: dict) -> int:
    """Convert CyberChef compression type to zlib level.

    Args:
        args: Operation arguments dict

    Returns:
        zlib compression level (0-9)
    """
    compression_type = args.get("Compression type", "Dynamic Huffman Coding")
    if compression_type == "None (Store)":
        return 0
    elif compression_type == "Fixed Huffman Coding":
        return 1
    else:  # Dynamic Huffman Coding (default)
        return 6


def _python_zlib_deflate(data: bytes, args: dict) -> bytes:
    """Python implementation of Zlib Deflate."""
    level = _get_compression_level(args)
    return zlib.compress(data, level=level)


def _python_zlib_inflate(data: bytes, args: dict) -> bytes:
    """Python implementation of Zlib Inflate."""
    start_index = int(args.get("Start index", 0))
    if start_index > 0:
        data = data[start_index:]
    return zlib.decompress(data)


def _python_raw_deflate(data: bytes, args: dict) -> bytes:
    """Python implementation of Raw Deflate."""
    level = _get_compression_level(args)
    compressor = zlib.compressobj(level=level, wbits=-15)
    return compressor.compress(data) + compressor.flush()


def _python_raw_inflate(data: bytes, args: dict) -> bytes:
    """Python implementation of Raw Inflate."""
    start_index = int(args.get("Start index", 0))
    if start_index > 0:
        data = data[start_index:]
    return zlib.decompress(data, wbits=-15)


def _python_gzip_compress(data: bytes, args: dict) -> bytes:
    """Python implementation of Gzip."""
    level = _get_compression_level(args)
    if level == 0:
        level = 1  # gzip doesn't support level 0

    buf = BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=level) as f:
        f.write(data)
    return buf.getvalue()


def _python_gunzip(data: bytes, args: dict) -> bytes:
    """Python implementation of Gunzip."""
    buf = BytesIO(data)
    with gzip.GzipFile(fileobj=buf, mode="rb") as f:
        return f.read()


def _python_bzip2_compress(data: bytes, args: dict) -> bytes:
    """Python implementation of Bzip2 Compress."""
    block_size = int(args.get("Block size (100s of kb)", 9))
    block_size = max(1, min(9, block_size))
    return bz2.compress(data, compresslevel=block_size)


def _python_bzip2_decompress(data: bytes, args: dict) -> bytes:
    """Python implementation of Bzip2 Decompress."""
    return bz2.decompress(data)


# Map of operations that can use Python implementations
PYTHON_COMPRESSION_OVERRIDES: dict[str, callable] = {
    "Zlib Deflate": _python_zlib_deflate,
    "Zlib Inflate": _python_zlib_inflate,
    "Raw Deflate": _python_raw_deflate,
    "Raw Inflate": _python_raw_inflate,
    "Gzip": _python_gzip_compress,
    "Gunzip": _python_gunzip,
    "Bzip2 Compress": _python_bzip2_compress,
    "Bzip2 Decompress": _python_bzip2_decompress,
}


# =============================================================================
# Runtime Management
# =============================================================================


def get_chef() -> JSRuntime:
    """Get or create a cached CyberChef runtime instance.

    Returns:
        JSRuntime instance with CyberChef loaded
    """
    global _runtime_instance
    if _runtime_instance is None:
        _runtime_instance = load_cyberchef()
    return _runtime_instance


def load_cyberchef(path: str | None = None, preferred_runtime: str | None = None) -> JSRuntime:
    """Load CyberChef bundle into JavaScript runtime.

    Args:
        path: Path to CyberChef.js bundle. If None, uses package data path.
        preferred_runtime: Preferred runtime ('quickjs', 'stpyv8', 'pythonmonkey').
                          If None, auto-selects best available.

    Returns:
        JSRuntime instance with CyberChef loaded
    """
    if path is None:
        path = str(Path(__file__).parent / "data" / "CyberChef.js")

    runtime = get_runtime(preferred_runtime)
    runtime.load(path)

    return runtime


def set_runtime(runtime: JSRuntime | None) -> None:
    """Set the global runtime instance.

    Useful for testing or forcing a specific runtime.

    Args:
        runtime: JSRuntime instance to use, or None to clear
    """
    global _runtime_instance
    _runtime_instance = runtime


# =============================================================================
# Dish Conversion
# =============================================================================


def plate(v: Dish | Any, runtime: JSRuntime | None = None) -> Dish | Any:
    """Convert between Python types and CyberChef Dish objects.

    Args:
        v: Either a Dish object or a native Python type
        runtime: Optional runtime (unused, kept for API compatibility)

    Returns:
        Native Python type if input is Dish, Dish dict if input is Python type
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


# =============================================================================
# Core Bake Function
# =============================================================================


def _execute_python_operation(op_name: str, data: bytes | str, args: dict) -> bytes:
    """Execute a Python-implemented operation.

    Args:
        op_name: Name of the operation
        data: Input data (bytes or string)
        args: Operation arguments

    Returns:
        Result as bytes
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    func = PYTHON_COMPRESSION_OVERRIDES[op_name]
    return func(data, args)


def _bake_with_runtime(
    runtime: JSRuntime,
    input_data: bytes | str,
    recipe: list[str | RecipeOperation],
) -> bytes | str:
    """Execute recipe using JavaScript runtime.

    Args:
        runtime: JSRuntime instance
        input_data: Input data as bytes or string
        recipe: List of operations

    Returns:
        Result as bytes or string
    """
    # Convert input to Dish format
    if isinstance(input_data, bytes):
        input_dish = {"value": list(input_data), "type": int(DishType.ARRAY_BUFFER)}
    else:
        input_dish = {"value": input_data, "type": int(DishType.STRING)}

    # Execute via runtime
    result_dish = runtime.bake(input_dish, recipe)

    return plate(result_dish)


def bake(input_data: bytes | str, recipe: list[str | RecipeOperation]) -> bytes | str:
    """Execute CyberChef operations.

    This function intelligently routes operations based on runtime capabilities:
    - If runtime needs compression fallback, compression uses Python stdlib
    - All other operations use the JavaScript runtime

    Args:
        input_data: Input data as bytes or string
        recipe: List of operations. Each operation is either:
            - A string operation name: "To Base64"
            - A dict with op and args: {"op": "SHA2", "args": {"size": 256}}

    Returns:
        Result as bytes or string depending on the final operation output
    """
    if not recipe:
        return input_data

    runtime = get_chef()

    # If runtime doesn't need compression fallback, run everything through JS
    if not runtime.needs_compression_fallback:
        return _bake_with_runtime(runtime, input_data, recipe)

    # Otherwise, intelligently route operations
    current_data = input_data
    pending_recipe: list[str | RecipeOperation] = []

    for step in recipe:
        # Extract operation name and args
        if isinstance(step, str):
            op_name = step
            op_args = {}
        else:
            op_name = step.get("op", "")
            op_args = step.get("args", {})

        # Check if this operation should use Python implementation
        if op_name in PYTHON_COMPRESSION_OVERRIDES:
            # First, execute any pending JS operations
            if pending_recipe:
                current_data = _bake_with_runtime(runtime, current_data, pending_recipe)
                pending_recipe = []

            # Execute Python operation
            current_data = _execute_python_operation(op_name, current_data, op_args)
        else:
            # Queue for JS execution
            pending_recipe.append(step)

    # Execute any remaining JS operations
    if pending_recipe:
        current_data = _bake_with_runtime(runtime, current_data, pending_recipe)

    return current_data
