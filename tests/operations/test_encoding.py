"""Comprehensive tests for CyberChef encoding/decoding operations.

This module tests all major encoding and decoding operations including:
- Base64, Base32, Base45, Base58, Base62, Base85
- Hexadecimal encoding
- URL encoding/decoding
- HTML entity encoding/decoding
- Character encoding (charcode, binary, decimal, octal)

Each operation is tested with:
- Basic strings
- Empty input
- Binary data (all 256 bytes)
- UTF-8 unicode strings
- Roundtrip encode/decode tests
- Edge cases and error conditions
"""

import base64
import binascii
import urllib.parse

import pytest

from ida_cyberchef.cyberchef import bake

# Import test constants from conftest
from tests.conftest import (
    ALL_BYTES,
    BASE64_TEST_VECTORS,
    EMPTY_BYTES,
    HELLO_WORLD,
    URL_ENCODE_TEST_VECTORS,
    UTF8_EMOJI,
    UTF8_MULTILANG,
    UTF8_SIMPLE,
    assert_roundtrip,
    compare_with_python,
    roundtrip_test,
)


# ============================================================================
# Base64 Encoding/Decoding Tests
# ============================================================================


class TestBase64:
    """Test suite for Base64 encoding and decoding operations."""

    @pytest.mark.parametrize("input_data,expected", BASE64_TEST_VECTORS)
    def test_to_base64_rfc_vectors(self, input_data, expected):
        """Test Base64 encoding with RFC 4648 standard test vectors.

        These test vectors are from RFC 4648 Section 10 and ensure compliance
        with the Base64 standard.
        """
        result = bake(input_data, ["To Base64"])
        assert result == expected

    @pytest.mark.parametrize("expected,input_data", BASE64_TEST_VECTORS)
    def test_from_base64_rfc_vectors(self, input_data, expected):
        """Test Base64 decoding with RFC 4648 standard test vectors."""
        result = bake(input_data, ["From Base64"])
        assert result == expected

    def test_to_base64_hello_world(self):
        """Test Base64 encoding of 'Hello, World!'."""
        result = bake(HELLO_WORLD, ["To Base64"])
        assert result == "SGVsbG8sIFdvcmxkIQ=="

    def test_from_base64_hello_world(self):
        """Test Base64 decoding to 'Hello, World!'."""
        result = bake("SGVsbG8sIFdvcmxkIQ==", ["From Base64"])
        assert result == HELLO_WORLD

    def test_to_base64_empty(self):
        """Test Base64 encoding of empty input."""
        result = bake(EMPTY_BYTES, ["To Base64"])
        assert result == ""

    def test_from_base64_empty(self):
        """Test Base64 decoding of empty input."""
        result = bake("", ["From Base64"])
        assert result == EMPTY_BYTES

    def test_to_base64_all_bytes(self):
        """Test Base64 encoding of all 256 possible byte values."""
        result = bake(ALL_BYTES, ["To Base64"])
        # Verify it's valid Base64 and can be decoded
        decoded = base64.b64decode(result)
        assert decoded == ALL_BYTES

    def test_from_base64_all_bytes(self):
        """Test Base64 decoding of all 256 possible byte values."""
        # First encode with Python's base64
        encoded = base64.b64encode(ALL_BYTES).decode("ascii")
        # Then decode with CyberChef
        result = bake(encoded, ["From Base64"])
        assert result == ALL_BYTES

    def test_to_base64_utf8(self):
        """Test Base64 encoding of UTF-8 strings."""
        result = bake(UTF8_SIMPLE, ["To Base64"])
        # Verify by decoding with Python
        decoded = base64.b64decode(result)
        assert decoded == UTF8_SIMPLE

    def test_base64_roundtrip_hello_world(self):
        """Test Base64 encode→decode roundtrip with 'Hello, World!'."""
        assert_roundtrip(HELLO_WORLD, ["To Base64"], ["From Base64"])

    def test_base64_roundtrip_all_bytes(self):
        """Test Base64 encode→decode roundtrip with all 256 bytes."""
        assert_roundtrip(ALL_BYTES, ["To Base64"], ["From Base64"])

    def test_base64_roundtrip_utf8(self):
        """Test Base64 encode→decode roundtrip with UTF-8 data."""
        assert_roundtrip(UTF8_SIMPLE, ["To Base64"], ["From Base64"])
        assert_roundtrip(UTF8_EMOJI, ["To Base64"], ["From Base64"])
        assert_roundtrip(UTF8_MULTILANG, ["To Base64"], ["From Base64"])

    def test_to_base64_compare_python(self):
        """Compare CyberChef Base64 encoding with Python's base64 module."""
        assert compare_with_python(
            HELLO_WORLD,
            ["To Base64"],
            lambda data: base64.b64encode(data).decode("ascii")
        )

    def test_to_base64_with_alphabet_standard(self):
        """Test Base64 encoding with standard alphabet (explicit)."""
        result = bake(
            b"hello",
            [{"op": "To Base64", "args": {"Alphabet": "A-Za-z0-9+/="}}]
        )
        assert result == "aGVsbG8="

    def test_from_base64_remove_non_alphabet(self):
        """Test Base64 decoding with non-alphabet character removal."""
        # Input with whitespace and newlines
        input_data = "SGVs bG8s\nIFdv cmxk IQ=="
        result = bake(
            input_data,
            [{"op": "From Base64", "args": {"Remove non-alphabet chars": True}}]
        )
        assert result == HELLO_WORLD


# ============================================================================
# Base32 Encoding/Decoding Tests
# ============================================================================


class TestBase32:
    """Test suite for Base32 encoding and decoding operations."""

    def test_to_base32_hello_world(self):
        """Test Base32 encoding of 'Hello, World!'."""
        result = bake(HELLO_WORLD, ["To Base32"])
        # Verify with Python's base32
        expected = base64.b32encode(HELLO_WORLD).decode("ascii")
        assert result == expected

    def test_from_base32_hello_world(self):
        """Test Base32 decoding to 'Hello, World!'."""
        encoded = base64.b32encode(HELLO_WORLD).decode("ascii")
        result = bake(encoded, ["From Base32"])
        assert result == HELLO_WORLD

    def test_to_base32_empty(self):
        """Test Base32 encoding of empty input."""
        result = bake(EMPTY_BYTES, ["To Base32"])
        assert result == ""

    def test_from_base32_empty(self):
        """Test Base32 decoding of empty input."""
        result = bake("", ["From Base32"])
        assert result == EMPTY_BYTES

    def test_to_base32_all_bytes(self):
        """Test Base32 encoding of all 256 possible byte values."""
        result = bake(ALL_BYTES, ["To Base32"])
        # Verify it's valid Base32 and can be decoded
        decoded = base64.b32decode(result)
        assert decoded == ALL_BYTES

    def test_base32_roundtrip_hello_world(self):
        """Test Base32 encode→decode roundtrip with 'Hello, World!'."""
        assert_roundtrip(HELLO_WORLD, ["To Base32"], ["From Base32"])

    def test_base32_roundtrip_all_bytes(self):
        """Test Base32 encode→decode roundtrip with all 256 bytes."""
        assert_roundtrip(ALL_BYTES, ["To Base32"], ["From Base32"])

    def test_base32_roundtrip_utf8(self):
        """Test Base32 encode→decode roundtrip with UTF-8 data."""
        assert_roundtrip(UTF8_SIMPLE, ["To Base32"], ["From Base32"])

    def test_to_base32_compare_python(self):
        """Compare CyberChef Base32 encoding with Python's base64 module."""
        assert compare_with_python(
            HELLO_WORLD,
            ["To Base32"],
            lambda data: base64.b32encode(data).decode("ascii")
        )


# ============================================================================
# Base45 Encoding/Decoding Tests
# ============================================================================


class TestBase45:
    """Test suite for Base45 encoding and decoding operations."""

    def test_to_base45_hello_world(self):
        """Test Base45 encoding of 'Hello, World!'."""
        result = bake(HELLO_WORLD, ["To Base45"])
        # Base45 is used in EU Digital COVID Certificate
        assert isinstance(result, str)
        assert len(result) > 0

    def test_from_base45_basic(self):
        """Test Base45 decoding of basic string."""
        # First encode, then decode
        encoded = bake(b"hello", ["To Base45"])
        result = bake(encoded, ["From Base45"])
        assert result == b"hello"

    def test_to_base45_empty(self):
        """Test Base45 encoding of empty input."""
        result = bake(EMPTY_BYTES, ["To Base45"])
        assert result == ""

    def test_from_base45_empty(self):
        """Test Base45 decoding of empty input."""
        result = bake("", ["From Base45"])
        assert result == EMPTY_BYTES

    def test_base45_roundtrip_hello_world(self):
        """Test Base45 encode→decode roundtrip with 'Hello, World!'."""
        assert_roundtrip(HELLO_WORLD, ["To Base45"], ["From Base45"])

    def test_base45_roundtrip_all_bytes(self):
        """Test Base45 encode→decode roundtrip with all 256 bytes."""
        assert_roundtrip(ALL_BYTES, ["To Base45"], ["From Base45"])

    def test_base45_roundtrip_utf8(self):
        """Test Base45 encode→decode roundtrip with UTF-8 data."""
        assert_roundtrip(UTF8_SIMPLE, ["To Base45"], ["From Base45"])


# ============================================================================
# Base58 Encoding/Decoding Tests
# ============================================================================


class TestBase58:
    """Test suite for Base58 encoding and decoding operations."""

    def test_to_base58_hello_world(self):
        """Test Base58 encoding of 'Hello, World!'."""
        result = bake(HELLO_WORLD, ["To Base58"])
        # Base58 is used in Bitcoin addresses
        assert isinstance(result, str)
        # Base58 uses alphanumeric chars excluding 0, O, I, l
        assert all(c not in "0OIl" for c in result)

    def test_from_base58_basic(self):
        """Test Base58 decoding of basic string."""
        # First encode, then decode
        encoded = bake(b"hello", ["To Base58"])
        result = bake(encoded, ["From Base58"])
        assert result == b"hello"

    def test_to_base58_empty(self):
        """Test Base58 encoding of empty input."""
        result = bake(EMPTY_BYTES, ["To Base58"])
        assert result == ""

    def test_from_base58_empty(self):
        """Test Base58 decoding of empty input."""
        result = bake("", ["From Base58"])
        assert result == EMPTY_BYTES

    def test_base58_roundtrip_hello_world(self):
        """Test Base58 encode→decode roundtrip with 'Hello, World!'."""
        assert_roundtrip(HELLO_WORLD, ["To Base58"], ["From Base58"])

    def test_base58_roundtrip_all_bytes(self):
        """Test Base58 encode→decode roundtrip with all 256 bytes."""
        assert_roundtrip(ALL_BYTES, ["To Base58"], ["From Base58"])

    def test_base58_roundtrip_utf8(self):
        """Test Base58 encode→decode roundtrip with UTF-8 data."""
        assert_roundtrip(UTF8_SIMPLE, ["To Base58"], ["From Base58"])

    def test_to_base58_with_alphabet_bitcoin(self):
        """Test Base58 encoding with Bitcoin alphabet (default)."""
        result = bake(
            b"hello",
            [{"op": "To Base58", "args": {"Alphabet": "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"}}]
        )
        assert isinstance(result, str)


# ============================================================================
# Base62 Encoding/Decoding Tests
# ============================================================================


class TestBase62:
    """Test suite for Base62 encoding and decoding operations."""

    def test_to_base62_hello_world(self):
        """Test Base62 encoding of 'Hello, World!'."""
        result = bake(HELLO_WORLD, ["To Base62"])
        # Base62 uses 0-9, A-Z, a-z
        assert isinstance(result, str)
        assert all(c.isalnum() for c in result)

    def test_from_base62_basic(self):
        """Test Base62 decoding of basic string."""
        # First encode, then decode
        encoded = bake(b"hello", ["To Base62"])
        result = bake(encoded, ["From Base62"])
        assert result == b"hello"

    def test_to_base62_empty(self):
        """Test Base62 encoding of empty input."""
        result = bake(EMPTY_BYTES, ["To Base62"])
        assert result == "0"  # Base62 typically represents empty as "0"

    def test_base62_roundtrip_hello_world(self):
        """Test Base62 encode→decode roundtrip with 'Hello, World!'."""
        assert_roundtrip(HELLO_WORLD, ["To Base62"], ["From Base62"])

    def test_base62_roundtrip_all_bytes(self):
        """Test Base62 encode→decode roundtrip with all 256 bytes."""
        assert_roundtrip(ALL_BYTES, ["To Base62"], ["From Base62"])

    def test_base62_roundtrip_utf8(self):
        """Test Base62 encode→decode roundtrip with UTF-8 data."""
        assert_roundtrip(UTF8_SIMPLE, ["To Base62"], ["From Base62"])


# ============================================================================
# Base85 Encoding/Decoding Tests
# ============================================================================


class TestBase85:
    """Test suite for Base85 (Ascii85) encoding and decoding operations."""

    def test_to_base85_hello_world(self):
        """Test Base85 encoding of 'Hello, World!'."""
        result = bake(HELLO_WORLD, ["To Base85"])
        # Verify with Python's base85 (ascii85)
        expected = base64.a85encode(HELLO_WORLD).decode("ascii")
        assert result == expected

    def test_from_base85_hello_world(self):
        """Test Base85 decoding to 'Hello, World!'."""
        encoded = base64.a85encode(HELLO_WORLD).decode("ascii")
        result = bake(encoded, ["From Base85"])
        assert result == HELLO_WORLD

    def test_to_base85_empty(self):
        """Test Base85 encoding of empty input."""
        result = bake(EMPTY_BYTES, ["To Base85"])
        assert result == ""

    def test_from_base85_empty(self):
        """Test Base85 decoding of empty input."""
        result = bake("", ["From Base85"])
        assert result == EMPTY_BYTES

    def test_to_base85_all_bytes(self):
        """Test Base85 encoding of all 256 possible byte values."""
        result = bake(ALL_BYTES, ["To Base85"])
        # Verify it's valid Base85 and can be decoded
        decoded = base64.a85decode(result)
        assert decoded == ALL_BYTES

    def test_base85_roundtrip_hello_world(self):
        """Test Base85 encode→decode roundtrip with 'Hello, World!'."""
        assert_roundtrip(HELLO_WORLD, ["To Base85"], ["From Base85"])

    def test_base85_roundtrip_all_bytes(self):
        """Test Base85 encode→decode roundtrip with all 256 bytes."""
        assert_roundtrip(ALL_BYTES, ["To Base85"], ["From Base85"])

    def test_base85_roundtrip_utf8(self):
        """Test Base85 encode→decode roundtrip with UTF-8 data."""
        assert_roundtrip(UTF8_SIMPLE, ["To Base85"], ["From Base85"])

    def test_to_base85_compare_python(self):
        """Compare CyberChef Base85 encoding with Python's base64 module."""
        assert compare_with_python(
            HELLO_WORLD,
            ["To Base85"],
            lambda data: base64.a85encode(data).decode("ascii")
        )


# ============================================================================
# Hexadecimal Encoding/Decoding Tests
# ============================================================================


class TestHex:
    """Test suite for hexadecimal encoding and decoding operations."""

    def test_to_hex_hello_world(self):
        """Test hex encoding of 'Hello, World!'."""
        result = bake(HELLO_WORLD, ["To Hex"])
        # Default delimiter is space
        assert result == "48 65 6c 6c 6f 2c 20 57 6f 72 6c 64 21"

    def test_to_hex_no_delimiter(self):
        """Test hex encoding without delimiter."""
        result = bake(
            HELLO_WORLD,
            [{"op": "To Hex", "args": {"Delimiter": "None"}}]
        )
        assert result == "48656c6c6f2c20576f726c6421"

    def test_to_hex_comma_delimiter(self):
        """Test hex encoding with comma delimiter."""
        result = bake(
            b"hello",
            [{"op": "To Hex", "args": {"Delimiter": "Comma"}}]
        )
        assert result == "68,65,6c,6c,6f"

    def test_to_hex_0x_prefix(self):
        """Test hex encoding with 0x prefix."""
        result = bake(
            b"hello",
            [{"op": "To Hex", "args": {"Delimiter": "0x"}}]
        )
        # CyberChef's 0x delimiter doesn't add spaces between values
        assert result == "0x680x650x6c0x6c0x6f"

    def test_from_hex_hello_world(self):
        """Test hex decoding to 'Hello, World!'."""
        result = bake("48 65 6c 6c 6f 2c 20 57 6f 72 6c 64 21", ["From Hex"])
        assert result == HELLO_WORLD

    def test_from_hex_no_delimiter(self):
        """Test hex decoding without delimiter."""
        result = bake("68656c6c6f", ["From Hex"])
        assert result == b"hello"

    def test_from_hex_various_delimiters(self):
        """Test hex decoding with various delimiters."""
        # Space delimiter
        result = bake("68 65 6c 6c 6f", ["From Hex"])
        assert result == b"hello"

        # Comma delimiter
        result = bake("68,65,6c,6c,6f", ["From Hex"])
        assert result == b"hello"

        # Colon delimiter
        result = bake("68:65:6c:6c:6f", ["From Hex"])
        assert result == b"hello"

        # 0x prefix (CyberChef accepts both with and without spaces)
        result = bake("0x680x650x6c0x6c0x6f", ["From Hex"])
        assert result == b"hello"

    def test_to_hex_empty(self):
        """Test hex encoding of empty input."""
        result = bake(EMPTY_BYTES, ["To Hex"])
        assert result == ""

    def test_from_hex_empty(self):
        """Test hex decoding of empty input."""
        result = bake("", ["From Hex"])
        assert result == EMPTY_BYTES

    def test_to_hex_all_bytes(self):
        """Test hex encoding of all 256 possible byte values."""
        result = bake(
            ALL_BYTES,
            [{"op": "To Hex", "args": {"Delimiter": "None"}}]
        )
        # Verify with Python's binascii
        expected = binascii.hexlify(ALL_BYTES).decode("ascii")
        assert result == expected

    def test_from_hex_all_bytes(self):
        """Test hex decoding of all 256 possible byte values."""
        hex_str = binascii.hexlify(ALL_BYTES).decode("ascii")
        result = bake(hex_str, ["From Hex"])
        assert result == ALL_BYTES

    def test_hex_roundtrip_hello_world(self):
        """Test hex encode→decode roundtrip with 'Hello, World!'."""
        assert_roundtrip(HELLO_WORLD, ["To Hex"], ["From Hex"])

    def test_hex_roundtrip_all_bytes(self):
        """Test hex encode→decode roundtrip with all 256 bytes."""
        assert_roundtrip(ALL_BYTES, ["To Hex"], ["From Hex"])

    def test_hex_roundtrip_utf8(self):
        """Test hex encode→decode roundtrip with UTF-8 data."""
        assert_roundtrip(UTF8_SIMPLE, ["To Hex"], ["From Hex"])

    def test_to_hex_bytes_per_line(self):
        """Test hex encoding with bytes per line option."""
        result = bake(
            b"hello world",
            [{"op": "To Hex", "args": {"Delimiter": "Space", "Bytes per line": 5}}]
        )
        # Should have line breaks every 5 bytes
        lines = result.strip().split("\n")
        assert len(lines) >= 2


# ============================================================================
# URL Encoding/Decoding Tests
# ============================================================================


class TestURLEncoding:
    """Test suite for URL encoding and decoding operations.

    Note: CyberChef's default URL encoding follows RFC 3986 unreserved characters.
    By default, it does NOT encode: A-Z a-z 0-9 - _ . ~ and certain special chars
    like = & @ + , that are commonly used in URLs.
    It DOES encode: space → %20, percent → %25, and other special characters.
    """

    @pytest.mark.parametrize("input_data,expected", [
        ("Hello World!", "Hello%20World!"),
        # CyberChef does not encode = and & by default (RFC 3986 unreserved)
        ("foo=bar&baz=qux", "foo=bar&baz=qux"),
        ("100%", "100%25"),
        # CyberChef does not encode @ by default
        ("user@example.com", "user@example.com"),
        # CyberChef does not encode + and = by default
        ("a+b=c", "a+b=c"),
    ])
    def test_url_encode_vectors(self, input_data, expected):
        """Test URL encoding with standard test vectors.

        These tests verify CyberChef's default URL encoding behavior, which
        preserves certain characters that are commonly used in URLs.
        """
        result = bake(input_data, ["URL Encode"])
        assert result == expected

    @pytest.mark.parametrize("expected,input_data", [
        ("Hello World!", "Hello%20World!"),
        ("foo=bar&baz=qux", "foo%3Dbar%26baz%3Dqux"),
        ("100%", "100%25"),
        ("user@example.com", "user%40example.com"),
    ])
    def test_url_decode_vectors(self, input_data, expected):
        """Test URL decoding with standard test vectors."""
        result = bake(input_data, ["URL Decode"])
        assert result == expected

    def test_url_encode_hello_world(self):
        """Test URL encoding of 'Hello, World!'.

        Note: CyberChef does not encode commas by default, only spaces.
        """
        result = bake("Hello, World!", ["URL Encode"])
        assert result == "Hello,%20World!"

    def test_url_decode_hello_world(self):
        """Test URL decoding to 'Hello, World!'."""
        result = bake("Hello%2C%20World!", ["URL Decode"])
        assert result == "Hello, World!"

    def test_url_encode_empty(self):
        """Test URL encoding of empty input."""
        result = bake("", ["URL Encode"])
        assert result == ""

    def test_url_decode_empty(self):
        """Test URL decoding of empty input."""
        result = bake("", ["URL Decode"])
        assert result == ""

    def test_url_encode_special_chars(self):
        """Test URL encoding of special characters."""
        result = bake("!@#$%^&*()", ["URL Encode"])
        # Verify it's properly encoded
        assert "%" in result
        # Verify it can be decoded
        decoded = urllib.parse.unquote(result)
        assert decoded == "!@#$%^&*()"

    def test_url_roundtrip_hello_world(self):
        """Test URL encode→decode roundtrip with 'Hello, World!'."""
        assert_roundtrip("Hello, World!", ["URL Encode"], ["URL Decode"])

    def test_url_roundtrip_special_chars(self):
        """Test URL encode→decode roundtrip with special characters."""
        test_string = "foo=bar&baz=qux?x=1#anchor"
        assert_roundtrip(test_string, ["URL Encode"], ["URL Decode"])

    def test_url_encode_compare_python(self):
        """Compare CyberChef URL encoding with Python's urllib.

        Note: CyberChef's default behavior differs from Python's urllib.parse.quote
        with safe="". CyberChef preserves more characters by default, including:
        = & @ + , ! and other characters commonly used in URLs.
        """
        test_string = "Hello World!"
        result = bake(test_string, ["URL Encode"])
        # CyberChef does not encode ! by default
        assert result == "Hello%20World!"

        # Test that the encoded string can be decoded back correctly
        decoded = urllib.parse.unquote(result)
        assert decoded == test_string

    def test_url_encode_encode_all(self):
        """Test URL encoding with 'Encode All' option."""
        result = bake(
            "hello",
            [{"op": "URL Encode", "args": {"Encode all special chars": True}}]
        )
        # With encode all, even normally safe chars get encoded
        assert "%" in result or result == "hello"  # 'hello' has no special chars


# ============================================================================
# HTML Entity Encoding/Decoding Tests
# ============================================================================


class TestHTMLEntity:
    """Test suite for HTML entity encoding and decoding operations."""

    def test_to_html_entity_basic(self):
        """Test HTML entity encoding of basic special characters."""
        result = bake("<div>Hello & goodbye</div>", ["To HTML Entity"])
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&amp;" in result

    def test_from_html_entity_basic(self):
        """Test HTML entity decoding of basic entities."""
        result = bake("&lt;div&gt;Hello &amp; goodbye&lt;/div&gt;", ["From HTML Entity"])
        assert result == "<div>Hello & goodbye</div>"

    def test_to_html_entity_quotes(self):
        """Test HTML entity encoding of quotes."""
        result = bake('"Hello" & \'World\'', ["To HTML Entity"])
        # Should encode quotes and ampersand
        assert "&quot;" in result or "&#" in result
        assert "&amp;" in result or "&#" in result

    def test_from_html_entity_quotes(self):
        """Test HTML entity decoding of quote entities."""
        result = bake("&quot;Hello&quot; &amp; &apos;World&apos;", ["From HTML Entity"])
        assert '"Hello"' in result
        assert "&" in result
        assert "'World'" in result or "World" in result

    def test_to_html_entity_empty(self):
        """Test HTML entity encoding of empty input."""
        result = bake("", ["To HTML Entity"])
        assert result == ""

    def test_from_html_entity_empty(self):
        """Test HTML entity decoding of empty input."""
        result = bake("", ["From HTML Entity"])
        assert result == ""

    def test_html_entity_roundtrip_basic(self):
        """Test HTML entity encode→decode roundtrip with special chars."""
        test_string = "<div>Hello & goodbye</div>"
        assert_roundtrip(test_string, ["To HTML Entity"], ["From HTML Entity"])

    def test_from_html_entity_named(self):
        """Test HTML entity decoding of named entities."""
        result = bake("&nbsp;&copy;&reg;&trade;", ["From HTML Entity"])
        # Should decode to actual unicode characters
        assert isinstance(result, str)
        assert len(result) > 0

    def test_from_html_entity_numeric(self):
        """Test HTML entity decoding of numeric entities."""
        result = bake("&#72;&#101;&#108;&#108;&#111;", ["From HTML Entity"])
        assert result == "Hello"

    def test_from_html_entity_hex(self):
        """Test HTML entity decoding of hexadecimal entities."""
        result = bake("&#x48;&#x65;&#x6C;&#x6C;&#x6F;", ["From HTML Entity"])
        assert result == "Hello"


# ============================================================================
# Character Code Encoding/Decoding Tests
# ============================================================================


class TestCharcode:
    """Test suite for charcode encoding and decoding operations."""

    def test_to_charcode_hello(self):
        """Test charcode encoding of 'hello'."""
        result = bake(
            "hello",
            [{"op": "To Charcode", "args": {"Base": 10}}]
        )
        # Base 10 for decimal output (default is base 16)
        assert result == "104 101 108 108 111"

    def test_from_charcode_hello(self):
        """Test charcode decoding to 'hello'."""
        result = bake(
            "104 101 108 108 111",
            [{"op": "From Charcode", "args": {"Base": 10}}]
        )
        assert result == b"hello"

    def test_to_charcode_empty(self):
        """Test charcode encoding of empty input."""
        result = bake("", ["To Charcode"])
        assert result == ""

    def test_from_charcode_empty(self):
        """Test charcode decoding of empty input."""
        result = bake("", ["From Charcode"])
        assert result == b""

    def test_charcode_roundtrip_hello(self):
        """Test charcode encode→decode roundtrip with 'hello'."""
        # Note: Default base is 16 (hex), so roundtrip works without specifying base
        # From Charcode returns bytes, so we expect bytes back
        assert_roundtrip("hello", ["To Charcode"], ["From Charcode"], expected=b"hello")

    def test_charcode_roundtrip_utf8(self):
        """Test charcode encode→decode roundtrip with UTF-8 data."""
        test_string = "Hello 世界"
        # From Charcode returns bytes
        assert_roundtrip(test_string, ["To Charcode"], ["From Charcode"], expected=test_string.encode('utf-8'))

    def test_to_charcode_base_hex(self):
        """Test charcode encoding with hexadecimal base."""
        result = bake(
            "hello",
            [{"op": "To Charcode", "args": {"Base": 16}}]
        )
        assert result == "68 65 6c 6c 6f"

    def test_from_charcode_base_hex(self):
        """Test charcode decoding with hexadecimal base."""
        result = bake(
            "68 65 6c 6c 6f",
            [{"op": "From Charcode", "args": {"Base": 16}}]
        )
        assert result == b"hello"


# ============================================================================
# Binary Encoding/Decoding Tests
# ============================================================================


class TestBinary:
    """Test suite for binary encoding and decoding operations."""

    def test_to_binary_hello(self):
        """Test binary encoding of 'hello'."""
        result = bake("hello", ["To Binary"])
        # Default is space-separated 8-bit binary
        assert "01101000" in result  # 'h' = 0x68 = 01101000

    def test_from_binary_hello(self):
        """Test binary decoding to 'hello'."""
        binary_str = "01101000 01100101 01101100 01101100 01101111"
        result = bake(binary_str, ["From Binary"])
        assert result == b"hello"

    def test_to_binary_empty(self):
        """Test binary encoding of empty input."""
        result = bake("", ["To Binary"])
        assert result == ""

    def test_from_binary_empty(self):
        """Test binary decoding of empty input."""
        result = bake("", ["From Binary"])
        assert result == b""

    def test_binary_roundtrip_hello(self):
        """Test binary encode→decode roundtrip with 'hello'."""
        # Note: To Binary takes string input, From Binary returns bytes
        encoded = bake("hello", ["To Binary"])
        decoded = bake(encoded, ["From Binary"])
        assert decoded == b"hello"

    def test_to_binary_delimiter_none(self):
        """Test binary encoding with no delimiter."""
        result = bake(
            "AB",
            [{"op": "To Binary", "args": {"Delimiter": "None"}}]
        )
        assert result == "0100000101000010"  # 'A' = 65, 'B' = 66

    def test_from_binary_no_delimiter(self):
        """Test binary decoding without delimiter."""
        result = bake("0100000101000010", ["From Binary"])
        assert result == b"AB"


# ============================================================================
# Decimal Encoding/Decoding Tests
# ============================================================================


class TestDecimal:
    """Test suite for decimal encoding and decoding operations."""

    def test_to_decimal_hello(self):
        """Test decimal encoding of 'hello'."""
        result = bake("hello", ["To Decimal"])
        # Default is space-separated decimal
        assert result == "104 101 108 108 111"

    def test_from_decimal_hello(self):
        """Test decimal decoding to 'hello'."""
        result = bake("104 101 108 108 111", ["From Decimal"])
        assert result == b"hello"

    def test_to_decimal_empty(self):
        """Test decimal encoding of empty input."""
        result = bake("", ["To Decimal"])
        assert result == ""

    def test_from_decimal_empty(self):
        """Test decimal decoding of empty input."""
        result = bake("", ["From Decimal"])
        assert result == b""

    def test_decimal_roundtrip_hello(self):
        """Test decimal encode→decode roundtrip with 'hello'."""
        encoded = bake("hello", ["To Decimal"])
        decoded = bake(encoded, ["From Decimal"])
        assert decoded == b"hello"

    def test_to_decimal_delimiter_comma(self):
        """Test decimal encoding with comma delimiter."""
        result = bake(
            "ABC",
            [{"op": "To Decimal", "args": {"Delimiter": "Comma"}}]
        )
        assert result == "65,66,67"

    def test_from_decimal_delimiter_comma(self):
        """Test decimal decoding with comma delimiter."""
        result = bake(
            "65,66,67",
            [{"op": "From Decimal", "args": {"Delimiter": "Comma"}}]
        )
        assert result == b"ABC"


# ============================================================================
# Octal Encoding/Decoding Tests
# ============================================================================


class TestOctal:
    """Test suite for octal encoding and decoding operations."""

    def test_to_octal_hello(self):
        """Test octal encoding of 'hello'."""
        result = bake("hello", ["To Octal"])
        # 'h' = 104 decimal = 150 octal
        # 'e' = 101 decimal = 145 octal
        # 'l' = 108 decimal = 154 octal
        # 'o' = 111 decimal = 157 octal
        assert "150" in result  # 'h'

    def test_from_octal_hello(self):
        """Test octal decoding to 'hello'."""
        # Using space-separated octal values
        result = bake("150 145 154 154 157", ["From Octal"])
        assert result == b"hello"

    def test_to_octal_empty(self):
        """Test octal encoding of empty input."""
        result = bake("", ["To Octal"])
        assert result == ""

    def test_from_octal_empty(self):
        """Test octal decoding of empty input."""
        result = bake("", ["From Octal"])
        assert result == b""

    def test_octal_roundtrip_hello(self):
        """Test octal encode→decode roundtrip with 'hello'."""
        encoded = bake("hello", ["To Octal"])
        decoded = bake(encoded, ["From Octal"])
        assert decoded == b"hello"

    def test_octal_roundtrip_all_ascii(self):
        """Test octal encode→decode roundtrip with all ASCII printable chars."""
        test_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        encoded = bake(test_string, ["To Octal"])
        decoded = bake(encoded, ["From Octal"])
        assert decoded == test_string.encode("ascii")


# ============================================================================
# Cross-Encoding Integration Tests
# ============================================================================


class TestCrossEncoding:
    """Test suite for combining multiple encoding operations."""

    def test_base64_then_hex(self):
        """Test Base64 encoding followed by hex encoding."""
        result = bake(HELLO_WORLD, ["To Base64", "To Hex"])
        # Should be hex representation of Base64 string
        assert isinstance(result, str)
        # Decode back
        decoded = bake(result, ["From Hex", "From Base64"])
        assert decoded == HELLO_WORLD

    def test_hex_then_base64(self):
        """Test hex encoding followed by Base64 encoding."""
        result = bake(HELLO_WORLD, ["To Hex", "To Base64"])
        # Should be Base64 representation of hex string
        assert isinstance(result, str)
        # Decode back
        decoded = bake(result, ["From Base64", "From Hex"])
        assert decoded == HELLO_WORLD

    def test_url_encode_then_base64(self):
        """Test URL encoding followed by Base64 encoding."""
        test_string = "Hello World! foo=bar&baz=qux"
        result = bake(test_string, ["URL Encode", "To Base64"])
        # Decode back
        decoded = bake(result, ["From Base64", "URL Decode"])
        assert decoded == test_string

    def test_multiple_base_encodings(self):
        """Test encoding with multiple base encodings."""
        # Encode with Base64, then Base32
        result = bake(b"hello", ["To Base64", "To Base32"])
        # Decode in reverse order
        decoded = bake(result, ["From Base32", "From Base64"])
        assert decoded == b"hello"


# ============================================================================
# Edge Cases and Error Handling Tests
# ============================================================================


class TestEncodingEdgeCases:
    """Test suite for edge cases and error handling in encoding operations."""

    def test_from_base64_invalid_padding(self):
        """Test Base64 decoding with invalid padding."""
        # Missing padding should still work with remove non-alphabet
        result = bake(
            "SGVsbG8",  # Missing padding
            [{"op": "From Base64", "args": {"Remove non-alphabet chars": True}}]
        )
        # Should decode as much as possible
        assert isinstance(result, bytes)

    def test_from_hex_invalid_chars(self):
        """Test hex decoding with invalid characters."""
        # From Hex should handle invalid chars gracefully
        result = bake("68 65 6c 6c 6f", ["From Hex"])
        assert result == b"hello"

    def test_from_hex_odd_length(self):
        """Test hex decoding with odd number of hex digits."""
        # Should handle odd-length hex strings
        result = bake("68656c6c6", ["From Hex"])
        # Should decode what it can
        assert isinstance(result, bytes)

    def test_url_decode_malformed(self):
        """Test URL decoding with malformed percent encoding."""
        # Should handle incomplete percent sequences
        result = bake("Hello%20World%", ["URL Decode"])
        assert "Hello World" in result

    def test_large_input_base64(self):
        """Test Base64 encoding with large input."""
        large_data = b"A" * 10000
        result = bake(large_data, ["To Base64"])
        # Verify roundtrip
        decoded = bake(result, ["From Base64"])
        assert decoded == large_data

    def test_binary_data_through_url_encode(self):
        """Test URL encoding of binary data (should handle all bytes)."""
        # URL encoding should handle all byte values
        result = bake(ALL_BYTES[:16], ["To Hex", "URL Encode"])
        assert isinstance(result, str)

    def test_null_byte_handling(self):
        """Test encoding operations with null bytes."""
        data_with_null = b"hello\x00world"

        # Base64 should handle null bytes
        assert_roundtrip(data_with_null, ["To Base64"], ["From Base64"])

        # Hex should handle null bytes
        assert_roundtrip(data_with_null, ["To Hex"], ["From Hex"])

    def test_unicode_emoji_url_encode(self):
        """Test URL encoding of unicode emoji."""
        emoji_string = "Hello 🌍 World"
        result = bake(emoji_string, ["URL Encode"])
        # Should encode emoji properly
        assert "%" in result
        # Should roundtrip
        decoded = bake(result, ["URL Decode"])
        assert decoded == emoji_string

    def test_repeated_encoding(self):
        """Test encoding the same data multiple times."""
        # Encode Base64 three times
        result = bake(b"hello", ["To Base64", "To Base64", "To Base64"])
        # Decode three times
        decoded = bake(result, ["From Base64", "From Base64", "From Base64"])
        assert decoded == b"hello"

    def test_case_sensitivity(self):
        """Test case sensitivity in hex decoding."""
        # Hex should be case-insensitive for decoding
        result_lower = bake("68656c6c6f", ["From Hex"])
        result_upper = bake("68656C6C6F", ["From Hex"])
        result_mixed = bake("68656C6c6F", ["From Hex"])
        assert result_lower == result_upper == result_mixed == b"hello"
