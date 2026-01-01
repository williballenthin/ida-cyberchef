"""Data-driven test runner for CyberChef operations.

This module provides infrastructure to load and execute tests from JSON files.
The JSON format is designed to be language-agnostic, allowing the same test
data to be used by both Python and JavaScript test runners.

Usage:
    # Load tests from a JSON file
    test_suite = load_test_file("tests/data/operations/encoding/base64.json")

    # Run all tests
    results = run_tests(test_suite)

    # Or use with pytest via the test_json_operations.py module
"""

import base64
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

# Import cyberchef.py directly without triggering ida_cyberchef/__init__.py
# This avoids Qt dependencies that may not be available in all environments
_cyberchef_path = Path(__file__).parent.parent.parent / "ida_cyberchef" / "cyberchef.py"
_spec = importlib.util.spec_from_file_location("cyberchef", _cyberchef_path)
_cyberchef = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cyberchef)
bake = _cyberchef.bake


def decode_data_value(data_value: dict[str, Any]) -> bytes | str:
    """Decode a data value from JSON format to Python type.

    Args:
        data_value: Dict with 'type', 'value', and optional 'encoding' keys

    Returns:
        bytes or str depending on the 'type' field

    Examples:
        >>> decode_data_value({"type": "string", "value": "hello"})
        "hello"
        >>> decode_data_value({"type": "bytes", "encoding": "hex", "value": "68656c6c6f"})
        b"hello"
        >>> decode_data_value({"type": "bytes", "encoding": "base64", "value": "aGVsbG8="})
        b"hello"
        >>> decode_data_value({"type": "string", "encoding": "latin-1", "value": "68656c6c6f"})
        "hello"  # hex decoded, then interpreted as latin-1 string
    """
    data_type = data_value["type"]
    value = data_value["value"]

    if data_type == "string":
        encoding = data_value.get("encoding")
        if encoding == "latin-1":
            # Value is hex-encoded, decode to bytes then interpret as latin-1 string
            return bytes.fromhex(value).decode("latin-1")
        elif encoding is None:
            return value
        else:
            raise ValueError(f"Unknown string encoding: {encoding}")
    elif data_type == "bytes":
        encoding = data_value.get("encoding", "base64")
        if encoding == "base64":
            return base64.b64decode(value)
        elif encoding == "hex":
            return bytes.fromhex(value)
        else:
            raise ValueError(f"Unknown bytes encoding: {encoding}")
    else:
        raise ValueError(f"Unknown data type: {data_type}")


def encode_data_value(value: bytes | str, encoding: str = "base64") -> dict[str, Any]:
    """Encode a Python value to JSON data value format.

    Args:
        value: Python bytes or str to encode
        encoding: For bytes, use "base64" or "hex"

    Returns:
        Dict with 'type', 'value', and optionally 'encoding' keys

    Examples:
        >>> encode_data_value("hello")
        {"type": "string", "value": "hello"}
        >>> encode_data_value(b"hello", encoding="hex")
        {"type": "bytes", "encoding": "hex", "value": "68656c6c6f"}
    """
    if isinstance(value, str):
        return {"type": "string", "value": value}
    elif isinstance(value, bytes):
        if encoding == "base64":
            encoded = base64.b64encode(value).decode("ascii")
        elif encoding == "hex":
            encoded = value.hex()
        else:
            raise ValueError(f"Unknown encoding: {encoding}")
        return {"type": "bytes", "encoding": encoding, "value": encoded}
    else:
        raise TypeError(f"Cannot encode type {type(value)}")


def load_test_file(path: str | Path) -> dict[str, Any]:
    """Load a test suite from a JSON file.

    Args:
        path: Path to the JSON test file

    Returns:
        Parsed test suite dict
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_test_files(base_path: str | Path = None) -> list[dict[str, Any]]:
    """Load all test files from the data directory.

    Args:
        base_path: Base path to search. Defaults to tests/data/operations

    Returns:
        List of test suite dicts
    """
    if base_path is None:
        base_path = Path(__file__).parent / "operations"
    else:
        base_path = Path(base_path)

    test_suites = []
    for json_file in base_path.rglob("*.json"):
        try:
            test_suites.append(load_test_file(json_file))
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse {json_file}: {e}")

    return test_suites


def run_single_test(test_case: dict[str, Any]) -> tuple[bool, str | None]:
    """Run a single test case.

    Args:
        test_case: Test case dict with 'input', 'operations', 'expected' keys

    Returns:
        Tuple of (success: bool, error_message: str | None)
    """
    try:
        # Check if test should be skipped
        if test_case.get("skip", False):
            return True, f"SKIPPED: {test_case.get('skipReason', 'No reason given')}"

        # Decode input
        input_data = decode_data_value(test_case["input"])

        # Get operations
        operations = test_case["operations"]

        # Execute
        result = bake(input_data, operations)

        # Decode expected output
        expected = decode_data_value(test_case["expected"])

        # Compare
        if result == expected:
            return True, None
        else:
            return False, f"Expected {expected!r}, got {result!r}"

    except Exception as e:
        return False, f"Exception: {type(e).__name__}: {e}"


def run_tests(test_suite: dict[str, Any]) -> dict[str, Any]:
    """Run all tests in a test suite.

    Args:
        test_suite: Test suite dict with 'operation', 'tests' keys

    Returns:
        Results dict with 'passed', 'failed', 'skipped', 'results' keys
    """
    results = {
        "operation": test_suite.get("operation", "unknown"),
        "category": test_suite.get("category", "unknown"),
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "results": []
    }

    for test_case in test_suite.get("tests", []):
        success, message = run_single_test(test_case)

        test_result = {
            "name": test_case.get("name", "unnamed"),
            "success": success,
            "message": message
        }
        results["results"].append(test_result)

        if test_case.get("skip", False):
            results["skipped"] += 1
        elif success:
            results["passed"] += 1
        else:
            results["failed"] += 1

    return results


def generate_pytest_params(test_suite: dict[str, Any]) -> list[tuple]:
    """Generate pytest parametrize arguments from a test suite.

    Args:
        test_suite: Test suite dict

    Returns:
        List of (test_id, test_case) tuples for pytest.mark.parametrize
    """
    params = []
    for test_case in test_suite.get("tests", []):
        test_id = test_case.get("name", "unnamed").replace(" ", "_")
        params.append((test_id, test_case))
    return params


def collect_all_tests() -> list[tuple[str, dict[str, Any]]]:
    """Collect all tests from all JSON files for pytest.

    Returns:
        List of (test_id, test_case) tuples including file context
    """
    all_tests = []
    base_path = Path(__file__).parent / "operations"

    for json_file in base_path.rglob("*.json"):
        try:
            test_suite = load_test_file(json_file)
            operation = test_suite.get("operation", json_file.stem)
            category = test_suite.get("category", "unknown")

            for test_case in test_suite.get("tests", []):
                test_name = test_case.get("name", "unnamed")
                # Create a unique test ID
                test_id = f"{category}/{operation}/{test_name}".replace(" ", "_")

                # Add metadata to test case for better error reporting
                enriched_case = {
                    **test_case,
                    "_file": str(json_file),
                    "_operation": operation,
                    "_category": category,
                }
                all_tests.append((test_id, enriched_case))

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Failed to load {json_file}: {e}")

    return all_tests
