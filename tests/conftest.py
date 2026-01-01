"""Pytest configuration and fixtures for IDA CyberChef testing.

This module provides common test infrastructure for testing CyberChef operations,
including standard test constants, fixtures for common scenarios, and helper
functions for roundtrip testing.
"""

import hashlib
import string
from typing import Any, Callable

import pytest

from ida_cyberchef.cyberchef import bake, get_chef, plate


# ============================================================================
# Standard Test Constants
# ============================================================================

# All 256 possible byte values (0x00 through 0xFF)
ALL_BYTES = bytes(range(256))

# Common test strings
HELLO_WORLD = b"Hello, World!"
EMPTY_STRING = b""
EMPTY_BYTES = b""

# ASCII printable characters
ASCII_PRINTABLE = string.printable.encode("ascii")

# UTF-8 test strings
UTF8_SIMPLE = "Hello, World! 你好世界 🌍".encode("utf-8")
UTF8_EMOJI = "🎉🚀💻🔥⭐".encode("utf-8")
UTF8_MULTILANG = "Hello مرحبا こんにちは 안녕하세요 Привет".encode("utf-8")

# Binary test data
BINARY_ZEROS = bytes(16)
BINARY_ONES = bytes([0xFF] * 16)
BINARY_ALTERNATING = bytes([0xAA, 0x55] * 8)
BINARY_SEQUENTIAL = bytes(range(32))

# Base64 test vectors (standard from RFC 4648)
BASE64_TEST_VECTORS = [
    (b"", ""),
    (b"f", "Zg=="),
    (b"fo", "Zm8="),
    (b"foo", "Zm9v"),
    (b"foob", "Zm9vYg=="),
    (b"fooba", "Zm9vYmE="),
    (b"foobar", "Zm9vYmFy"),
]

# Hex test vectors
HEX_TEST_VECTORS = [
    (b"hello", "68 65 6c 6c 6f"),
    (b"\x00\x01\x02\x03", "00 01 02 03"),
    (b"\xff\xfe\xfd", "ff fe fd"),
]

# Hash test vectors (from standard test vectors)
HASH_TEST_VECTORS = {
    "md5": [
        (b"", "d41d8cd98f00b204e9800998ecf8427e"),
        (b"a", "0cc175b9c0f1b6a831c399e269772661"),
        (b"abc", "900150983cd24fb0d6963f7d28e17f72"),
        (b"message digest", "f96b697d7cb7938d525a2f31aaf161d0"),
        (b"hello", "5d41402abc4b2a76b9719d911017c592"),
    ],
    "sha1": [
        (b"", "da39a3ee5e6b4b0d3255bfef95601890afd80709"),
        (b"abc", "a9993e364706816aba3e25717850c26c9cd0d89d"),
        (
            b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
            "84983e441c3bd26ebaae4aa1f95129e5e54670f1",
        ),
    ],
    "sha256": [
        (
            b"",
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        ),
        (
            b"abc",
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        ),
        (
            b"hello",
            "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
        ),
    ],
    "sha512": [
        (
            b"",
            "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e",
        ),
        (
            b"abc",
            "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f",
        ),
    ],
}

# URL encoding test vectors
# Note: CyberChef follows RFC 3986 and does not encode certain characters
# like = & @ + , by default. It DOES encode: space → %20, percent → %25
URL_ENCODE_TEST_VECTORS = [
    ("Hello World!", "Hello%20World!"),
    ("foo=bar&baz=qux", "foo=bar&baz=qux"),  # = and & not encoded by default
    ("100%", "100%25"),  # % is always encoded
]

# Common CyberChef test data (from upstream test suite)
LOREM_IPSUM = b"""Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."""

# Test data for compression operations
COMPRESSIBLE_DATA = b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" * 10


# ============================================================================
# Pytest Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def chef():
    """Get a cached CyberChef instance for the entire test session.

    This fixture provides access to the low-level CyberChef JavaScript API
    for tests that need direct access to the chef object.

    Returns:
        CyberChef module instance
    """
    return get_chef()


@pytest.fixture
def bake_fn() -> Callable[[bytes | str, list[str | dict[str, Any]]], bytes | str]:
    """Provide the bake function for tests.

    This fixture provides the main bake() API function for testing CyberChef
    operations. It's useful for tests that want to explicitly use fixtures
    rather than direct imports.

    Returns:
        The bake function from ida_cyberchef.cyberchef

    Example:
        def test_encoding(bake_fn):
            result = bake_fn(b"hello", ["To Base64"])
            assert result == "aGVsbG8="
    """
    return bake


@pytest.fixture
def plate_fn():
    """Provide the plate function for tests.

    This fixture provides the plate() function for converting between Python
    types and CyberChef Dish objects.

    Returns:
        The plate function from ida_cyberchef.cyberchef
    """
    return plate


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def all_bytes():
    """Provide all 256 byte values for testing.

    Returns:
        bytes: All possible byte values from 0x00 to 0xFF
    """
    return ALL_BYTES


@pytest.fixture
def hello_world():
    """Provide standard 'Hello, World!' test string.

    Returns:
        bytes: The string 'Hello, World!' as bytes
    """
    return HELLO_WORLD


@pytest.fixture
def utf8_test_strings():
    """Provide various UTF-8 test strings.

    Returns:
        dict: Dictionary of UTF-8 test strings including emoji and multilingual text
    """
    return {
        "simple": UTF8_SIMPLE,
        "emoji": UTF8_EMOJI,
        "multilang": UTF8_MULTILANG,
    }


@pytest.fixture
def binary_test_data():
    """Provide various binary test patterns.

    Returns:
        dict: Dictionary of binary test patterns (zeros, ones, alternating, etc.)
    """
    return {
        "zeros": BINARY_ZEROS,
        "ones": BINARY_ONES,
        "alternating": BINARY_ALTERNATING,
        "sequential": BINARY_SEQUENTIAL,
    }


@pytest.fixture
def base64_vectors():
    """Provide standard Base64 test vectors from RFC 4648.

    Returns:
        list: List of (input, expected_output) tuples
    """
    return BASE64_TEST_VECTORS


@pytest.fixture
def hash_vectors():
    """Provide standard hash test vectors.

    Returns:
        dict: Dictionary mapping hash algorithm names to test vectors
    """
    return HASH_TEST_VECTORS


# ============================================================================
# Helper Functions
# ============================================================================


def roundtrip_test(
    input_data: bytes | str,
    encode_recipe: list[str | dict[str, Any]],
    decode_recipe: list[str | dict[str, Any]],
    expected: bytes | str | None = None,
) -> bool:
    """Test that encode→decode returns the original input.

    This helper function performs a roundtrip test: it encodes the input data
    using the encode recipe, then decodes the result using the decode recipe,
    and verifies that the final output matches the original input (or expected
    value if provided).

    Args:
        input_data: The original input data to test
        encode_recipe: Recipe to encode the data
        decode_recipe: Recipe to decode the encoded data
        expected: Optional expected value after roundtrip (defaults to input_data)

    Returns:
        bool: True if roundtrip successful, False otherwise

    Example:
        # Test that To Hex → From Hex returns original
        assert roundtrip_test(
            b"hello",
            ["To Hex"],
            ["From Hex"]
        )

        # Test Base64 encoding/decoding
        assert roundtrip_test(
            b"test data",
            ["To Base64"],
            ["From Base64"]
        )
    """
    if expected is None:
        expected = input_data

    try:
        # Encode
        encoded = bake(input_data, encode_recipe)

        # Decode
        decoded = bake(encoded, decode_recipe)

        # Compare
        return decoded == expected
    except Exception:
        return False


def verify_hash(
    input_data: bytes,
    operation: str | dict[str, Any],
    expected_hash: str,
) -> bool:
    """Verify that a CyberChef hash operation produces the expected hash.

    This helper verifies that a hash operation produces the correct result
    by comparing it with the expected hash value.

    Args:
        input_data: Input data to hash
        operation: Hash operation name or operation dict
        expected_hash: Expected hash output (as hex string)

    Returns:
        bool: True if hash matches expected value

    Example:
        assert verify_hash(
            b"hello",
            {"op": "SHA2", "args": {"size": "256"}},
            "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        )
    """
    try:
        result = bake(input_data, [operation])
        return result.lower() == expected_hash.lower()
    except Exception:
        return False


def get_python_hash(input_data: bytes, algorithm: str) -> str:
    """Get hash using Python's hashlib for comparison.

    This helper computes a hash using Python's standard hashlib module,
    useful for verifying that CyberChef's hash operations match standard
    implementations.

    Args:
        input_data: Data to hash
        algorithm: Hash algorithm name (md5, sha1, sha256, sha512, etc.)

    Returns:
        str: Hex digest of the hash

    Example:
        expected = get_python_hash(b"hello", "sha256")
        result = bake(b"hello", [{"op": "SHA2", "args": {"size": "256"}}])
        assert result == expected
    """
    h = hashlib.new(algorithm, input_data)
    return h.hexdigest()


def assert_roundtrip(
    input_data: bytes | str,
    encode_recipe: list[str | dict[str, Any]],
    decode_recipe: list[str | dict[str, Any]],
    expected: bytes | str | None = None,
) -> None:
    """Assert that encode→decode returns the original input.

    Like roundtrip_test but raises AssertionError with detailed information
    on failure instead of returning bool.

    Args:
        input_data: The original input data to test
        encode_recipe: Recipe to encode the data
        decode_recipe: Recipe to decode the encoded data
        expected: Optional expected value after roundtrip (defaults to input_data)

    Raises:
        AssertionError: If roundtrip fails

    Example:
        assert_roundtrip(
            b"hello",
            ["To Hex"],
            ["From Hex"]
        )
    """
    if expected is None:
        expected = input_data

    # Encode
    encoded = bake(input_data, encode_recipe)

    # Decode
    decoded = bake(encoded, decode_recipe)

    # Compare with detailed error message
    assert decoded == expected, (
        f"Roundtrip failed:\n"
        f"  Input:    {input_data!r}\n"
        f"  Encoded:  {encoded!r}\n"
        f"  Decoded:  {decoded!r}\n"
        f"  Expected: {expected!r}\n"
        f"  Encode recipe: {encode_recipe}\n"
        f"  Decode recipe: {decode_recipe}"
    )


def compare_with_python(
    input_data: bytes,
    cyberchef_recipe: list[str | dict[str, Any]],
    python_func: Callable[[bytes], Any],
) -> bool:
    """Compare CyberChef result with Python standard library implementation.

    This helper is useful for verifying that CyberChef operations match
    standard Python implementations (e.g., hashlib for hashes, base64 for
    encoding, etc.).

    Args:
        input_data: Input data to process
        cyberchef_recipe: CyberChef recipe to execute
        python_func: Python function that should produce equivalent result

    Returns:
        bool: True if results match

    Example:
        import base64
        assert compare_with_python(
            b"hello",
            ["To Base64"],
            lambda data: base64.b64encode(data).decode()
        )
    """
    try:
        cyberchef_result = bake(input_data, cyberchef_recipe)
        python_result = python_func(input_data)
        return cyberchef_result == python_result
    except Exception:
        return False


# ============================================================================
# Parametrize Helpers
# ============================================================================


def generate_test_cases(test_vectors: list[tuple], ids: list[str] | None = None):
    """Generate pytest parametrize arguments from test vectors.

    This helper converts test vectors into the format expected by pytest's
    parametrize decorator.

    Args:
        test_vectors: List of tuples (input, expected) or similar
        ids: Optional list of test IDs for better test output

    Returns:
        tuple: (argnames, argvalues, ids) for use with pytest.mark.parametrize

    Example:
        test_cases = [
            (b"hello", "aGVsbG8="),
            (b"world", "d29ybGQ="),
        ]
        @pytest.mark.parametrize(*generate_test_cases(test_cases))
        def test_encoding(input_data, expected):
            result = bake(input_data, ["To Base64"])
            assert result == expected
    """
    if not test_vectors:
        return ("input_data,expected", [], [])

    # Determine number of items in each tuple
    num_args = len(test_vectors[0])

    if num_args == 2:
        argnames = "input_data,expected"
    else:
        argnames = ",".join(f"arg{i}" for i in range(num_args))

    return (argnames, test_vectors, ids)
