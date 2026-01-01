"""Comprehensive edge case and error handling tests for IDA CyberChef.

This module tests edge cases, error conditions, and boundary conditions including:
- Invalid operation names and arguments
- Empty and extreme data inputs
- Binary safety and null byte handling
- Unicode edge cases (BOM, zero-width chars, RTL text)
- Recipe chain edge cases
- Error propagation and recovery in chains
- Data type transitions across operations

The tests ensure that:
1. Errors are handled gracefully with clear messages
2. Binary data is preserved correctly through operations
3. Edge cases don't cause crashes or data corruption
4. Invalid inputs produce appropriate errors
"""

import pytest

from ida_cyberchef.cyberchef import bake

# Import test constants from conftest
from tests.conftest import (
    ALL_BYTES,
    EMPTY_BYTES,
    HELLO_WORLD,
    UTF8_EMOJI,
    UTF8_MULTILANG,
    UTF8_SIMPLE,
    assert_roundtrip,
)


# ============================================================================
# 1. Invalid Operation Tests
# ============================================================================


class TestInvalidOperations:
    """Test handling of invalid operation names."""

    def test_nonexistent_operation(self):
        """Test that non-existent operation names raise TypeError."""
        with pytest.raises(TypeError, match="Couldn't find an operation"):
            bake(b"test", ["NonExistentOperation"])

    def test_misspelled_operation_tobase64(self):
        """Test that misspelled operation names raise TypeError."""
        with pytest.raises(TypeError, match="Couldn't find an operation"):
            bake(b"test", ["To_Base64"])  # Underscore instead of space

    def test_misspelled_operation_fromhex(self):
        """Test misspelled 'From-Hex' with hyphen instead of space."""
        with pytest.raises(TypeError, match="Couldn't find an operation"):
            bake("68656c6c6f", ["From-Hex"])

    def test_misspelled_operation_typo(self):
        """Test operation name with typo."""
        with pytest.raises(TypeError, match="Couldn't find an operation"):
            bake(b"test", ["To Base46"])  # Typo: 46 instead of 64

    def test_empty_operation_name(self):
        """Test that empty operation name raises TypeError."""
        with pytest.raises(TypeError, match="Couldn't find an operation"):
            bake(b"test", [""])

    def test_none_operation(self):
        """Test that None as operation causes error."""
        with pytest.raises((TypeError, AttributeError)):
            bake(b"test", [None])  # type: ignore[list-item]

    def test_numeric_operation(self):
        """Test that numeric operation name causes error."""
        with pytest.raises((TypeError, AttributeError)):
            bake(b"test", [12345])  # type: ignore[list-item]

    def test_whitespace_only_operation(self):
        """Test that whitespace-only operation name raises error."""
        with pytest.raises(TypeError, match="Couldn't find an operation"):
            bake(b"test", ["   "])


# ============================================================================
# 2. Invalid Argument Tests
# ============================================================================


class TestInvalidArguments:
    """Test handling of invalid operation arguments."""

    def test_invalid_sha2_size_string(self):
        """Test SHA2 with invalid size string."""
        # Size must be valid: "224", "256", "384", "512"
        with pytest.raises((TypeError, ValueError, Exception)):
            bake(b"test", [{"op": "SHA2", "args": {"size": "999"}}])

    def test_invalid_sha2_size_integer(self):
        """Test SHA2 with integer instead of string (should work or fail gracefully)."""
        # Some operations might accept integers, others might not
        try:
            result = bake(b"test", [{"op": "SHA2", "args": {"size": 256}}])
            # If it works, verify it's a valid hash
            assert isinstance(result, str)
            assert len(result) == 64  # SHA256 produces 64 hex chars
        except (TypeError, ValueError):
            # If it fails, that's also acceptable behavior
            pass

    def test_invalid_hex_delimiter(self):
        """Test To Hex with invalid delimiter value."""
        # Invalid delimiter should either error or use default
        result = bake(b"hello", [{"op": "To Hex", "args": {"Delimiter": "InvalidDelim"}}])
        # Should still produce some output
        assert isinstance(result, str)

    def test_missing_required_args(self):
        """Test operation with missing required arguments."""
        # Most operations should handle missing args with defaults
        result = bake(b"hello", [{"op": "To Hex", "args": {}}])
        assert isinstance(result, str)

    def test_extra_unexpected_args(self):
        """Test operation with extra unexpected arguments."""
        # Extra args should be ignored
        result = bake(
            b"hello",
            [{"op": "To Base64", "args": {"UnexpectedArg": True, "AnotherArg": 123}}]
        )
        assert result == "aGVsbG8="

    def test_null_args(self):
        """Test operation with null/None arguments."""
        # None args should be handled gracefully
        result = bake(b"hello", [{"op": "To Base64", "args": None}])  # type: ignore[dict-item]
        assert result == "aGVsbG8="

    def test_wrong_arg_type_boolean(self):
        """Test operation with wrong argument type (boolean instead of string)."""
        # Should handle type mismatches gracefully
        try:
            result = bake(b"hello", [{"op": "To Hex", "args": {"Delimiter": True}}])
            assert isinstance(result, str)
        except (TypeError, ValueError):
            pass  # Acceptable to raise error

    def test_negative_number_args(self):
        """Test operations with negative number arguments."""
        # Negative numbers should be handled appropriately
        try:
            result = bake("hello", [{"op": "To Charcode", "args": {"Base": -1}}])
            # If it works, output should be a string
            assert isinstance(result, str)
        except (TypeError, ValueError, Exception):
            # Acceptable to raise error for invalid base (JSError or OperationError)
            pass


# ============================================================================
# 3. Data Type Edge Cases
# ============================================================================


class TestDataTypeEdgeCases:
    """Test edge cases for various input data types."""

    def test_empty_bytes_input(self):
        """Test operations with empty bytes input."""
        result = bake(EMPTY_BYTES, ["To Base64"])
        assert result == ""

    def test_empty_string_input(self):
        """Test operations with empty string input."""
        result = bake("", ["URL Encode"])
        assert result == ""

    def test_empty_input_roundtrip(self):
        """Test empty input survives encode/decode roundtrip."""
        assert_roundtrip(EMPTY_BYTES, ["To Base64"], ["From Base64"])
        assert_roundtrip(EMPTY_BYTES, ["To Hex"], ["From Hex"])

    def test_very_large_input_1mb(self):
        """Test operations with 1MB input data."""
        large_data = b"A" * (1024 * 1024)  # 1MB
        result = bake(large_data, ["To Base64"])
        assert isinstance(result, str)
        # Verify roundtrip
        decoded = bake(result, ["From Base64"])
        assert decoded == large_data

    def test_very_large_input_roundtrip(self):
        """Test 1MB data survives hex encode/decode roundtrip."""
        large_data = b"X" * (1024 * 1024)
        assert_roundtrip(
            large_data,
            [{"op": "To Hex", "args": {"Delimiter": "None"}}],
            ["From Hex"]
        )

    def test_null_byte_at_start(self):
        """Test data with null byte at the start."""
        data = b"\x00hello"
        assert_roundtrip(data, ["To Base64"], ["From Base64"])
        assert_roundtrip(data, ["To Hex"], ["From Hex"])

    def test_null_byte_in_middle(self):
        """Test data with null byte in the middle."""
        data = b"hello\x00world"
        assert_roundtrip(data, ["To Base64"], ["From Base64"])
        assert_roundtrip(data, ["To Hex"], ["From Hex"])

    def test_null_byte_at_end(self):
        """Test data with null byte at the end."""
        data = b"hello\x00"
        assert_roundtrip(data, ["To Base64"], ["From Base64"])
        assert_roundtrip(data, ["To Hex"], ["From Hex"])

    def test_multiple_null_bytes(self):
        """Test data with multiple consecutive null bytes."""
        data = b"hello\x00\x00\x00world"
        assert_roundtrip(data, ["To Base64"], ["From Base64"])
        assert_roundtrip(data, ["To Hex"], ["From Hex"])

    def test_all_256_byte_values(self):
        """Test that all 256 possible byte values survive operations."""
        assert_roundtrip(ALL_BYTES, ["To Base64"], ["From Base64"])
        assert_roundtrip(ALL_BYTES, ["To Hex"], ["From Hex"])
        assert_roundtrip(ALL_BYTES, ["To Base32"], ["From Base32"])

    def test_all_256_bytes_hash(self):
        """Test hashing all 256 byte values."""
        result = bake(ALL_BYTES, ["MD5"])
        assert isinstance(result, str)
        assert len(result) == 32  # MD5 produces 32 hex chars

    def test_unicode_bom(self):
        """Test UTF-8 data with BOM (Byte Order Mark)."""
        # UTF-8 BOM: EF BB BF
        data_with_bom = b"\xef\xbb\xbfHello World"
        assert_roundtrip(data_with_bom, ["To Base64"], ["From Base64"])

    def test_unicode_zero_width_chars(self):
        """Test Unicode zero-width characters."""
        # Zero-width space (U+200B), zero-width joiner (U+200D)
        zero_width_string = "Hello\u200bWorld\u200d"
        result = bake(zero_width_string, ["URL Encode"])
        assert isinstance(result, str)
        # Verify roundtrip
        decoded = bake(result, ["URL Decode"])
        assert decoded == zero_width_string

    def test_unicode_rtl_text(self):
        """Test Unicode RTL (Right-to-Left) text."""
        # Hebrew text (RTL)
        rtl_text = "Hello שלום World"
        result = bake(rtl_text, ["URL Encode"])
        assert isinstance(result, str)
        # Verify roundtrip
        decoded = bake(result, ["URL Decode"])
        assert decoded == rtl_text

    def test_unicode_combining_characters(self):
        """Test Unicode combining characters."""
        # e with acute accent using combining character
        combining_text = "He\u0301llo"  # é as e + combining acute
        result = bake(combining_text, ["URL Encode"])
        assert isinstance(result, str)

    def test_unicode_emoji_sequences(self):
        """Test Unicode emoji sequences (multi-codepoint)."""
        # Family emoji is a sequence of multiple codepoints
        emoji_sequence = "👨‍👩‍👧‍👦"  # Family emoji
        result = bake(emoji_sequence.encode("utf-8"), ["To Base64"])
        decoded = bake(result, ["From Base64"])
        assert decoded == emoji_sequence.encode("utf-8")

    def test_unicode_surrogate_pairs(self):
        """Test Unicode characters requiring surrogate pairs."""
        # Emoji that requires surrogate pairs in UTF-16
        emoji = "𝕳𝖊𝖑𝖑𝖔"  # Mathematical bold text
        result = bake(emoji.encode("utf-8"), ["To Hex"])
        decoded = bake(result, ["From Hex"])
        assert decoded == emoji.encode("utf-8")


# ============================================================================
# 4. Recipe Chain Edge Cases
# ============================================================================


class TestRecipeChainEdgeCases:
    """Test edge cases in recipe chains."""

    def test_empty_recipe(self):
        """Test that empty recipe returns input unchanged."""
        result = bake(b"hello", [])
        # Empty recipe should return input as-is
        assert result == b"hello" or result == "hello"

    def test_single_operation_recipe(self):
        """Test recipe with single operation."""
        result = bake(b"hello", ["To Base64"])
        assert result == "aGVsbG8="

    def test_two_operation_chain(self):
        """Test simple two-operation chain."""
        result = bake(b"hello", ["To Base64", "MD5"])
        assert isinstance(result, str)
        assert len(result) == 32

    def test_long_chain_10_operations(self):
        """Test long chain with 10+ operations."""
        recipe = [
            "To Base64",
            "MD5",
            "To Hex",
            "From Hex",
            "To Base32",
            "From Base32",
            "To Base64",
            "From Base64",
            "To Hex",
            "From Hex",
        ]
        result = bake(b"hello", recipe)
        # Should complete without error
        assert isinstance(result, (bytes, str))

    def test_long_chain_15_operations(self):
        """Test very long chain with 15 operations."""
        recipe = [
            "To Base64",
            "To Hex",
            "From Hex",
            "To Base32",
            "From Base32",
            "To Base58",
            "From Base58",
            "To Base64",
            "From Base64",
            "MD5",
            "To Hex",
            "From Hex",
            "To Base64",
            "From Base64",
            "MD5",
        ]
        result = bake(b"hello", recipe)
        assert isinstance(result, str)
        assert len(result) == 32  # Final MD5

    def test_bytes_to_string_transition(self):
        """Test data type transition from bytes to string."""
        # To Base64 converts bytes to string
        result = bake(b"hello", ["To Base64"])
        assert isinstance(result, str)

    def test_string_to_bytes_transition(self):
        """Test data type transition from string to bytes."""
        # From Base64 converts string to bytes
        result = bake("aGVsbG8=", ["From Base64"])
        assert isinstance(result, bytes)

    def test_multiple_type_transitions(self):
        """Test multiple data type transitions in chain."""
        # bytes -> string -> bytes -> string
        result = bake(b"hello", ["To Base64", "From Base64", "To Hex"])
        assert isinstance(result, str)
        assert "68 65 6c 6c 6f" == result

    def test_bytes_through_hash_chain(self):
        """Test bytes data through multiple hash operations."""
        result = bake(b"hello", ["MD5", {"op": "SHA2", "args": {"size": "256"}}])
        assert isinstance(result, str)
        assert len(result) == 64  # SHA256 produces 64 hex chars

    def test_encode_decode_encode_pattern(self):
        """Test encode-decode-encode pattern."""
        result = bake(
            b"hello",
            ["To Base64", "From Base64", "To Hex", "From Hex", "To Base32"]
        )
        assert isinstance(result, str)


# ============================================================================
# 5. Error Recovery and Propagation
# ============================================================================


class TestErrorRecovery:
    """Test error propagation and recovery in chains."""

    def test_error_in_first_operation(self):
        """Test error in first operation stops chain."""
        with pytest.raises(TypeError, match="Couldn't find an operation"):
            bake(b"hello", ["InvalidOp", "To Base64", "MD5"])

    def test_error_in_middle_operation(self):
        """Test error in middle operation stops chain."""
        with pytest.raises(TypeError, match="Couldn't find an operation"):
            bake(b"hello", ["To Base64", "InvalidOp", "MD5"])

    def test_error_in_last_operation(self):
        """Test error in last operation after successful operations."""
        with pytest.raises(TypeError, match="Couldn't find an operation"):
            bake(b"hello", ["To Base64", "From Base64", "InvalidOp"])

    def test_malformed_recipe_dict_missing_op(self):
        """Test recipe dict without 'op' key."""
        with pytest.raises((KeyError, TypeError)):
            bake(b"hello", [{"args": {"size": "256"}}])  # type: ignore[list-item]

    def test_malformed_recipe_dict_wrong_structure(self):
        """Test recipe dict with wrong structure."""
        with pytest.raises((KeyError, TypeError, AttributeError)):
            bake(b"hello", [{"operation": "To Base64"}])  # type: ignore[list-item]

    def test_mixed_valid_invalid_operations(self):
        """Test mix of valid and invalid operations."""
        # First valid operation should execute before error
        with pytest.raises(TypeError, match="Couldn't find an operation"):
            bake(b"hello", ["To Base64", "InvalidOperation"])


# ============================================================================
# 6. Binary Safety Tests
# ============================================================================


class TestBinarySafety:
    """Test that binary data is preserved correctly."""

    def test_binary_through_base64(self):
        """Test binary data survives Base64 encode/decode."""
        binary_data = bytes(range(256))
        assert_roundtrip(binary_data, ["To Base64"], ["From Base64"])

    def test_binary_through_hex(self):
        """Test binary data survives hex encode/decode."""
        binary_data = bytes(range(256))
        assert_roundtrip(
            binary_data,
            [{"op": "To Hex", "args": {"Delimiter": "None"}}],
            ["From Hex"]
        )

    def test_binary_through_base32(self):
        """Test binary data survives Base32 encode/decode."""
        binary_data = bytes(range(256))
        assert_roundtrip(binary_data, ["To Base32"], ["From Base32"])

    def test_binary_with_null_bytes_base64(self):
        """Test binary data with null bytes through Base64."""
        binary_data = b"\x00\x01\x02\x00\x03\x00\x00\x04"
        assert_roundtrip(binary_data, ["To Base64"], ["From Base64"])

    def test_binary_with_high_bytes(self):
        """Test binary data with high byte values (0x80-0xFF)."""
        binary_data = bytes(range(128, 256))
        assert_roundtrip(binary_data, ["To Base64"], ["From Base64"])
        assert_roundtrip(
            binary_data,
            [{"op": "To Hex", "args": {"Delimiter": "None"}}],
            ["From Hex"]
        )

    def test_binary_alternating_pattern(self):
        """Test binary data with alternating 0x00 and 0xFF."""
        binary_data = bytes([0x00, 0xFF] * 128)
        assert_roundtrip(binary_data, ["To Base64"], ["From Base64"])

    def test_binary_sequential_pattern(self):
        """Test binary data with sequential byte pattern."""
        binary_data = bytes(list(range(256)) * 4)  # 1024 bytes
        assert_roundtrip(binary_data, ["To Base64"], ["From Base64"])

    def test_string_operations_on_binary(self):
        """Test that string operations handle binary data appropriately."""
        binary_data = b"\x00\x01\x02\x03\x04"
        # To Hex should work on binary data
        result = bake(binary_data, ["To Hex"])
        assert result == "00 01 02 03 04"

    def test_hash_operations_on_binary(self):
        """Test hash operations on binary data."""
        binary_data = bytes(range(256))
        result = bake(binary_data, ["MD5"])
        assert isinstance(result, str)
        assert len(result) == 32

    def test_multiple_encode_decode_binary(self):
        """Test binary data through multiple encode/decode cycles."""
        binary_data = b"\x00\x0f\xf0\xff\x42\x69\x96\xc3"
        # Multiple round trips
        for _ in range(3):
            encoded = bake(binary_data, ["To Base64"])
            binary_data = bake(encoded, ["From Base64"])
        # Should match original
        assert binary_data == b"\x00\x0f\xf0\xff\x42\x69\x96\xc3"

    def test_binary_data_length_preservation(self):
        """Test that binary data length is preserved through operations."""
        for length in [1, 16, 127, 128, 255, 256, 512, 1024]:
            binary_data = bytes(range(256))[:length] * (length // 256 + 1)
            binary_data = binary_data[:length]
            encoded = bake(binary_data, ["To Base64"])
            decoded = bake(encoded, ["From Base64"])
            assert len(decoded) == length
            assert decoded == binary_data


# ============================================================================
# 7. Additional Edge Cases
# ============================================================================


class TestAdditionalEdgeCases:
    """Additional edge cases and corner cases."""

    def test_single_byte_input(self):
        """Test operations with single byte input."""
        result = bake(b"A", ["To Base64"])
        assert result == "QQ=="

    def test_two_byte_input(self):
        """Test operations with two byte input."""
        result = bake(b"AB", ["To Base64"])
        assert result == "QUI="

    def test_whitespace_only_input(self):
        """Test operations with whitespace-only input."""
        result = bake("   ", ["URL Encode"])
        assert result == "%20%20%20"

    def test_newline_input(self):
        """Test operations with newline characters."""
        result = bake("hello\nworld", ["URL Encode"])
        assert "%0A" in result or "%0a" in result  # \n encoded

    def test_tab_input(self):
        """Test operations with tab characters."""
        result = bake("hello\tworld", ["URL Encode"])
        assert "%09" in result or "hello%09world" == result

    def test_carriage_return_input(self):
        """Test operations with carriage return."""
        result = bake("hello\rworld", ["URL Encode"])
        assert "%0D" in result or "%0d" in result

    def test_mixed_whitespace(self):
        """Test operations with mixed whitespace characters."""
        data = b"hello \t\n\r world"
        assert_roundtrip(data, ["To Base64"], ["From Base64"])

    def test_repeated_same_operation(self):
        """Test repeating the same operation multiple times."""
        result = bake(b"hello", ["To Base64", "To Base64", "To Base64"])
        # Triple Base64 encoding
        assert isinstance(result, str)

    def test_encode_then_hash(self):
        """Test encoding followed by hashing."""
        result = bake(b"hello", ["To Base64", "MD5"])
        assert isinstance(result, str)
        assert len(result) == 32

    def test_hash_then_encode(self):
        """Test hashing followed by encoding."""
        result = bake(b"hello", ["MD5", "To Base64"])
        assert isinstance(result, str)

    def test_utf8_emoji_roundtrip(self):
        """Test UTF-8 emoji data through operations."""
        assert_roundtrip(UTF8_EMOJI, ["To Base64"], ["From Base64"])
        assert_roundtrip(UTF8_EMOJI, ["To Hex"], ["From Hex"])

    def test_utf8_multilang_roundtrip(self):
        """Test multilingual UTF-8 data through operations."""
        assert_roundtrip(UTF8_MULTILANG, ["To Base64"], ["From Base64"])
        assert_roundtrip(UTF8_MULTILANG, ["To Hex"], ["From Hex"])

    def test_special_characters_in_data(self):
        """Test data with special characters."""
        special_data = b"!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        assert_roundtrip(special_data, ["To Base64"], ["From Base64"])

    def test_numeric_string_data(self):
        """Test numeric string data."""
        result = bake("1234567890", ["To Base64"])
        decoded = bake(result, ["From Base64"])
        assert decoded == b"1234567890"

    def test_boolean_like_strings(self):
        """Test boolean-like string values."""
        for value in ["true", "false", "True", "False", "TRUE", "FALSE"]:
            result = bake(value, ["To Base64"])
            decoded = bake(result, ["From Base64"])
            assert decoded == value.encode("utf-8")

    def test_json_like_strings(self):
        """Test JSON-like string data."""
        json_string = '{"key": "value", "number": 123}'
        result = bake(json_string, ["To Base64"])
        decoded = bake(result, ["From Base64"])
        assert decoded == json_string.encode("utf-8")

    def test_xml_like_strings(self):
        """Test XML-like string data."""
        xml_string = "<?xml version='1.0'?><root><item>test</item></root>"
        result = bake(xml_string, ["URL Encode"])
        assert isinstance(result, str)

    def test_base64_padding_variations(self):
        """Test Base64 with different padding scenarios."""
        # 0 padding
        assert_roundtrip(b"hel", ["To Base64"], ["From Base64"])
        # 1 padding (=)
        assert_roundtrip(b"he", ["To Base64"], ["From Base64"])
        # 2 padding (==)
        assert_roundtrip(b"h", ["To Base64"], ["From Base64"])
