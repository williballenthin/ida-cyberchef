"""Operation-specific pytest configuration and fixtures.

This module provides fixtures and helpers specifically for testing individual
CyberChef operations, including operation availability checking and
operation-specific test data.
"""

import pytest

from ida_cyberchef.cyberchef import bake, get_chef, plate


# ============================================================================
# Operation Availability Checking
# ============================================================================


def is_operation_available(operation_name: str) -> bool:
    """Check if a CyberChef operation is available.

    This function attempts to execute an operation with minimal input to
    determine if it's available in the current CyberChef build.

    Args:
        operation_name: Name of the operation to check (e.g., "To Base64")

    Returns:
        bool: True if operation is available, False otherwise

    Example:
        if is_operation_available("AES Encrypt"):
            # Run AES tests
            pass
    """
    try:
        # Try to execute the operation with minimal input
        bake(b"test", [operation_name])
        return True
    except (AttributeError, KeyError, TypeError):
        # Operation doesn't exist or isn't callable
        return False
    except Exception:
        # Operation exists but failed for other reasons (still available)
        return True


def skip_if_unavailable(operation_name: str):
    """Pytest marker to skip test if operation is not available.

    This decorator checks if an operation is available and skips the test
    if it's not, with a clear message about why it was skipped.

    Args:
        operation_name: Name of the operation to check

    Returns:
        pytest.mark.skipif decorator

    Example:
        @skip_if_unavailable("AES Encrypt")
        def test_aes_encryption():
            result = bake(b"data", ["AES Encrypt"])
            assert result
    """
    return pytest.mark.skipif(
        not is_operation_available(operation_name),
        reason=f"Operation '{operation_name}' is not available",
    )


def require_operations(*operation_names: str):
    """Pytest marker to skip test if any of the required operations are unavailable.

    This decorator checks if all required operations are available and skips
    the test if any are missing.

    Args:
        *operation_names: Names of operations that must be available

    Returns:
        pytest.mark.skipif decorator

    Example:
        @require_operations("To Base64", "From Base64")
        def test_base64_roundtrip():
            assert roundtrip_test(b"data", ["To Base64"], ["From Base64"])
    """
    unavailable = [op for op in operation_names if not is_operation_available(op)]

    if unavailable:
        reason = f"Required operations not available: {', '.join(unavailable)}"
    else:
        reason = ""

    return pytest.mark.skipif(
        bool(unavailable),
        reason=reason,
    )


# ============================================================================
# Operation Test Data Fixtures
# ============================================================================


@pytest.fixture
def encoding_test_data():
    """Provide test data for encoding operations.

    Returns:
        dict: Dictionary of test data suitable for various encoding operations
    """
    return {
        "empty": b"",
        "simple": b"hello",
        "with_spaces": b"hello world",
        "special_chars": b"!@#$%^&*()",
        "all_bytes": bytes(range(256)),
        "utf8": "Hello 世界 🌍".encode("utf-8"),
    }


@pytest.fixture
def compression_test_data():
    """Provide test data for compression operations.

    Returns:
        dict: Dictionary of test data suitable for compression testing
    """
    return {
        "highly_compressible": b"A" * 1000,
        "moderately_compressible": b"Hello World! " * 100,
        "incompressible": bytes(range(256)) * 4,
        "empty": b"",
    }


@pytest.fixture
def encryption_test_data():
    """Provide test data for encryption operations.

    Returns:
        dict: Dictionary with test data and common encryption parameters
    """
    return {
        "plaintext": b"This is a secret message",
        "key_128": b"0123456789ABCDEF",  # 16 bytes
        "key_256": b"0123456789ABCDEF" * 2,  # 32 bytes
        "iv": b"FEDCBA9876543210",  # 16 bytes
        "empty": b"",
    }


@pytest.fixture
def hash_test_data():
    """Provide test data for hash operations.

    Returns:
        dict: Dictionary of test inputs suitable for hash testing
    """
    return {
        "empty": b"",
        "single_char": b"a",
        "simple": b"hello",
        "standard": b"The quick brown fox jumps over the lazy dog",
        "binary": bytes(range(256)),
    }


@pytest.fixture
def parsing_test_data():
    """Provide test data for parsing operations.

    Returns:
        dict: Dictionary of test data suitable for parsing operations
    """
    return {
        "ipv4": "192.168.1.1",
        "ipv6": "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        "ipv6_short": "2001:db8::1",
        "url": "https://example.com/path?query=value",
        "json": '{"key": "value", "number": 42}',
        "xml": '<?xml version="1.0"?><root><item>value</item></root>',
        "csv": "name,age,city\nAlice,30,NYC\nBob,25,LA",
    }


@pytest.fixture
def datetime_test_data():
    """Provide test data for datetime operations.

    Returns:
        dict: Dictionary of test datetime strings in various formats
    """
    return {
        "iso8601": "2023-01-15T14:30:00Z",
        "unix_timestamp": "1673789400",
        "human_readable": "January 15, 2023 2:30:00 PM",
        "date_only": "2023-01-15",
        "time_only": "14:30:00",
        "custom_format": "15/01/2023 14:30:00",
    }


# ============================================================================
# Operation Category Fixtures
# ============================================================================


@pytest.fixture
def operation_categories():
    """Provide mapping of operations by category.

    Returns:
        dict: Dictionary mapping category names to lists of operations

    Note:
        This is a partial list of common operations. The full list contains
        443 unique operations across 16 categories.
    """
    return {
        "Data format": [
            "To Base64",
            "From Base64",
            "To Hex",
            "From Hex",
            "To Hexdump",
            "From Hexdump",
            "URL Encode",
            "URL Decode",
        ],
        "Encryption / Encoding": [
            "AES Encrypt",
            "AES Decrypt",
            "Triple DES Encrypt",
            "Triple DES Decrypt",
            "RC4",
            "Blowfish Encrypt",
            "Blowfish Decrypt",
        ],
        "Public Key": [
            "RSA Encrypt",
            "RSA Decrypt",
            "RSA Sign",
            "RSA Verify",
        ],
        "Arithmetic / Logic": [
            "ADD",
            "SUB",
            "Multiply",
            "Divide",
            "XOR",
            "OR",
            "AND",
            "NOT",
        ],
        "Networking": [
            "Parse IP range",
            "Parse IPv6 address",
            "Parse URI",
            "Format MAC address",
            "Decode NetBIOS Name",
        ],
        "Language": [
            "From Morse Code",
            "To Morse Code",
            "From Braille",
            "To Braille",
        ],
        "Utils": [
            "To Upper case",
            "To Lower case",
            "Reverse",
            "Sort",
            "Unique",
            "Split",
        ],
        "Date / Time": [
            "From UNIX Timestamp",
            "To UNIX Timestamp",
            "Translate DateTime Format",
            "Parse DateTime",
        ],
        "Extraction / Compression": [
            "Unzip",
            "Gunzip",
            "Bzip2 Decompress",
            "Raw Inflate",
        ],
        "Hashing": [
            "MD5",
            "SHA1",
            "SHA2",
            "SHA3",
            "BLAKE2b",
            "BLAKE2s",
        ],
    }


@pytest.fixture
def reversible_operations():
    """Provide pairs of reversible encode/decode operations.

    Returns:
        list: List of (encode_op, decode_op) tuples that should roundtrip

    Example:
        @pytest.mark.parametrize("encode_op,decode_op", reversible_operations())
        def test_roundtrip(encode_op, decode_op):
            assert roundtrip_test(b"test", [encode_op], [decode_op])
    """
    return [
        ("To Base64", "From Base64"),
        ("To Hex", "From Hex"),
        ("URL Encode", "URL Decode"),
        ("To Base32", "From Base32"),
        ("To Base58", "From Base58"),
        ("Gzip", "Gunzip"),
        ("Bzip2 Compress", "Bzip2 Decompress"),
    ]


# ============================================================================
# Operation Testing Helpers
# ============================================================================


def test_operation_with_args(
    operation_name: str,
    input_data: bytes | str,
    args: dict,
    expected_type: type | None = None,
) -> tuple[bool, any]:
    """Test an operation with specific arguments.

    This helper executes an operation with given arguments and optionally
    checks the return type.

    Args:
        operation_name: Name of the operation
        input_data: Input data for the operation
        args: Dictionary of operation arguments
        expected_type: Optional expected type of the result

    Returns:
        tuple: (success: bool, result: any)

    Example:
        success, result = test_operation_with_args(
            "SHA2",
            b"hello",
            {"size": "256"},
            expected_type=str
        )
        assert success
        assert len(result) == 64  # SHA256 hex digest length
    """
    try:
        operation = {"op": operation_name, "args": args}
        result = bake(input_data, [operation])

        if expected_type is not None:
            if not isinstance(result, expected_type):
                return False, result

        return True, result
    except Exception as e:
        return False, e


def get_operation_output_type(operation_name: str, input_data: bytes | str = b"test"):
    """Determine the output type of an operation.

    This helper executes an operation and returns the type of its output,
    useful for determining if an operation returns bytes or str.

    Args:
        operation_name: Name of the operation
        input_data: Test input data

    Returns:
        type: The type of the operation's output, or None if operation fails

    Example:
        output_type = get_operation_output_type("To Base64")
        assert output_type == str

        output_type = get_operation_output_type("From Base64")
        assert output_type == bytes
    """
    try:
        result = bake(input_data, [operation_name])
        return type(result)
    except Exception:
        return None


def assert_operation_succeeds(
    operation_name: str,
    input_data: bytes | str,
    args: dict | None = None,
):
    """Assert that an operation executes without error.

    This helper verifies that an operation can be executed successfully,
    without checking the specific output value.

    Args:
        operation_name: Name of the operation
        input_data: Input data for the operation
        args: Optional dictionary of operation arguments

    Raises:
        AssertionError: If operation fails

    Example:
        assert_operation_succeeds("MD5", b"hello")
        assert_operation_succeeds("SHA2", b"hello", {"size": "256"})
    """
    try:
        if args:
            operation = {"op": operation_name, "args": args}
        else:
            operation = operation_name

        bake(input_data, [operation])
    except Exception as e:
        pytest.fail(
            f"Operation '{operation_name}' failed with {type(e).__name__}: {e}"
        )


def get_operation_module_name(operation_name: str) -> str:
    """Get the expected module name for an operation.

    Converts operation names to Python module names following the test
    naming convention.

    Args:
        operation_name: CyberChef operation name (e.g., "To Base64")

    Returns:
        str: Module name (e.g., "test_to_base64")

    Example:
        assert get_operation_module_name("To Base64") == "test_to_base64"
        assert get_operation_module_name("SHA2") == "test_sha2"
    """
    # Convert to lowercase and replace spaces with underscores
    module_name = operation_name.lower().replace(" ", "_")
    # Remove special characters
    module_name = "".join(c if c.isalnum() or c == "_" else "_" for c in module_name)
    # Collapse multiple underscores
    while "__" in module_name:
        module_name = module_name.replace("__", "_")
    return f"test_{module_name}"


# ============================================================================
# Bulk Operation Testing
# ============================================================================


@pytest.fixture
def operation_smoke_test():
    """Provide a fixture for smoke testing operations.

    Returns a function that performs basic smoke testing on an operation
    to ensure it can be called without crashing.

    Returns:
        Callable: Function that smoke tests an operation

    Example:
        def test_all_encoding_ops(operation_smoke_test):
            for op in ["To Base64", "To Hex", "URL Encode"]:
                operation_smoke_test(op)
    """

    def _smoke_test(operation_name: str, test_input: bytes | str = b"test"):
        """Smoke test an operation with minimal input.

        Args:
            operation_name: Name of the operation to test
            test_input: Optional test input (default: b"test")

        Raises:
            AssertionError: If operation fails unexpectedly
        """
        try:
            result = bake(test_input, [operation_name])
            # Just verify we got something back
            assert result is not None, f"Operation '{operation_name}' returned None"
        except (AttributeError, KeyError) as e:
            pytest.fail(f"Operation '{operation_name}' not found: {e}")
        except Exception as e:
            # Some operations might fail with certain inputs, but shouldn't crash
            pytest.fail(f"Operation '{operation_name}' crashed: {type(e).__name__}: {e}")

    return _smoke_test


# ============================================================================
# Operation Discovery
# ============================================================================


def get_all_operations(chef=None):
    """Get list of all available operations from CyberChef.

    This function inspects the CyberChef instance to discover all available
    operations.

    Args:
        chef: Optional CyberChef instance (will be created if not provided)

    Returns:
        list: List of operation names

    Note:
        This is a placeholder. The actual implementation would inspect the
        CyberChef JavaScript object to enumerate operations.
    """
    if chef is None:
        chef = get_chef()

    # This would need to introspect the CyberChef object
    # For now, return a placeholder
    return []


@pytest.fixture
def all_operations():
    """Provide list of all available CyberChef operations.

    Returns:
        list: List of all operation names

    Example:
        def test_all_ops_load(all_operations):
            assert len(all_operations) > 400  # Should have ~443 operations
    """
    return get_all_operations()
