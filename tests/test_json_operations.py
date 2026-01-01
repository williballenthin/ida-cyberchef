"""Pytest integration for data-driven JSON operation tests.

This module discovers and runs all JSON-based operation tests from
tests/data/operations/. Each JSON file defines tests for a specific
CyberChef operation.

The test format is language-agnostic and can also be used by JavaScript
test runners to verify both Python and JS CyberChef implementations
produce identical results.

Example JSON test file structure:
{
    "operation": "To Base64",
    "category": "encoding",
    "description": "Base64 encoding tests",
    "tests": [
        {
            "name": "simple string",
            "input": {"type": "string", "value": "hello"},
            "operations": ["To Base64"],
            "expected": {"type": "string", "value": "aGVsbG8="}
        }
    ]
}
"""

import pytest

from tests.data.runner import collect_all_tests, decode_data_value, run_single_test


def pytest_generate_tests(metafunc):
    """Dynamically generate test cases from JSON files."""
    if "json_test_case" in metafunc.fixturenames:
        all_tests = collect_all_tests()
        if all_tests:
            ids, cases = zip(*all_tests)
            metafunc.parametrize("json_test_case", cases, ids=ids)
        else:
            # No tests found, parametrize with empty list
            metafunc.parametrize("json_test_case", [])


class TestJSONOperations:
    """Test class for JSON-driven operation tests."""

    def test_operation(self, json_test_case):
        """Run a single JSON test case.

        This test is parametrized by pytest_generate_tests to run once
        for each test case defined in the JSON files.
        """
        # Check for skip
        if json_test_case.get("skip", False):
            reason = json_test_case.get("skipReason", "Test marked as skip")
            pytest.skip(reason)

        # Run the test
        success, message = run_single_test(json_test_case)

        if not success:
            # Build detailed error message
            test_name = json_test_case.get("name", "unnamed")
            operation = json_test_case.get("_operation", "unknown")
            file_path = json_test_case.get("_file", "unknown")
            comment = json_test_case.get("comment", "")

            error_msg = f"\nTest: {test_name}"
            error_msg += f"\nOperation: {operation}"
            error_msg += f"\nFile: {file_path}"
            if comment:
                error_msg += f"\nComment: {comment}"
            error_msg += f"\nError: {message}"

            pytest.fail(error_msg)


class TestJSONTestRunner:
    """Tests for the JSON test runner infrastructure itself."""

    def test_decode_string(self):
        """Test decoding string type."""
        from tests.data.runner import decode_data_value

        result = decode_data_value({"type": "string", "value": "hello"})
        assert result == "hello"

    def test_decode_bytes_base64(self):
        """Test decoding bytes with base64 encoding."""
        from tests.data.runner import decode_data_value

        result = decode_data_value(
            {"type": "bytes", "encoding": "base64", "value": "aGVsbG8="}
        )
        assert result == b"hello"

    def test_decode_bytes_hex(self):
        """Test decoding bytes with hex encoding."""
        from tests.data.runner import decode_data_value

        result = decode_data_value(
            {"type": "bytes", "encoding": "hex", "value": "68656c6c6f"}
        )
        assert result == b"hello"

    def test_decode_bytes_default_encoding(self):
        """Test that bytes default to base64 encoding."""
        from tests.data.runner import decode_data_value

        # No encoding specified, should default to base64
        result = decode_data_value({"type": "bytes", "value": "aGVsbG8="})
        assert result == b"hello"

    def test_encode_string(self):
        """Test encoding string type."""
        from tests.data.runner import encode_data_value

        result = encode_data_value("hello")
        assert result == {"type": "string", "value": "hello"}

    def test_encode_bytes_base64(self):
        """Test encoding bytes with base64."""
        from tests.data.runner import encode_data_value

        result = encode_data_value(b"hello", encoding="base64")
        assert result == {"type": "bytes", "encoding": "base64", "value": "aGVsbG8="}

    def test_encode_bytes_hex(self):
        """Test encoding bytes with hex."""
        from tests.data.runner import encode_data_value

        result = encode_data_value(b"hello", encoding="hex")
        assert result == {"type": "bytes", "encoding": "hex", "value": "68656c6c6f"}

    def test_roundtrip_string(self):
        """Test string encode/decode roundtrip."""
        from tests.data.runner import decode_data_value, encode_data_value

        original = "Hello, World! 🌍"
        encoded = encode_data_value(original)
        decoded = decode_data_value(encoded)
        assert decoded == original

    def test_roundtrip_bytes(self):
        """Test bytes encode/decode roundtrip."""
        from tests.data.runner import decode_data_value, encode_data_value

        original = bytes(range(256))
        for encoding in ["base64", "hex"]:
            encoded = encode_data_value(original, encoding=encoding)
            decoded = decode_data_value(encoded)
            assert decoded == original, f"Failed for encoding {encoding}"
