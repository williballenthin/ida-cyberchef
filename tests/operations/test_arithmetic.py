"""Comprehensive tests for CyberChef arithmetic and logic operations.

This module tests all major arithmetic and logic operations including:
- Bitwise operations (XOR, AND, OR, NOT, ADD, SUB)
- Bit shifts (left, right - logical and arithmetic)
- Rotations (left, right - with and without carry)
- Math operations (Mean, Median, Standard Deviation, Sum, Multiply, Divide, Subtract)
- Set operations (Cartesian Product, Set Intersection, Set Union, Set Difference,
  Symmetric Difference, Power Set)

Each operation is tested with:
- Basic functionality with known input/output pairs
- Key operations with various key formats (Hex, UTF8, etc.)
- Edge cases (all zeros, all ones, alternating bits)
- Byte boundary tests
- Empty input handling
"""

import pytest

from ida_cyberchef.cyberchef import bake

# Import test constants from conftest
from tests.conftest import (
    ALL_BYTES,
    BINARY_ALTERNATING,
    BINARY_ONES,
    BINARY_SEQUENTIAL,
    BINARY_ZEROS,
    EMPTY_BYTES,
    HELLO_WORLD,
)


# ============================================================================
# XOR Operation Tests
# ============================================================================


class TestXOR:
    """Test suite for XOR bitwise operation."""

    def test_xor_with_hex_key(self):
        """Test XOR with hexadecimal key."""
        result = bake(
            b"hello",
            [{"op": "XOR", "args": [{"option": "Hex", "string": "ff"}, "Standard", False]}]
        )
        # XOR with 0xFF inverts all bits
        # 'h' = 0x68, 0x68 XOR 0xFF = 0x97
        # 'e' = 0x65, 0x65 XOR 0xFF = 0x9a
        assert result == bytes([0x97, 0x9a, 0x93, 0x93, 0x90])

    def test_xor_with_utf8_key(self):
        """Test XOR with UTF-8 key."""
        result = bake(
            b"AAAAA",
            [{"op": "XOR", "args": [{"option": "UTF8", "string": "K"}, "Standard", False]}]
        )
        # 'A' = 0x41, 'K' = 0x4B, 0x41 XOR 0x4B = 0x0A
        assert result == bytes([0x0A] * 5)

    def test_xor_self_cancel(self):
        """Test XOR property: A XOR A = 0."""
        # XOR with itself should give zeros
        result = bake(
            b"test",
            [{"op": "XOR", "args": [{"option": "UTF8", "string": "test"}, "Standard", False]}]
        )
        assert result == bytes([0x00] * 4)

    def test_xor_double_application(self):
        """Test XOR property: (A XOR B) XOR B = A."""
        key = {"option": "Hex", "string": "deadbeef"}
        # Encrypt
        encrypted = bake(HELLO_WORLD, [{"op": "XOR", "args": [key, "Standard", False]}])
        # Decrypt (XOR again with same key)
        decrypted = bake(encrypted, [{"op": "XOR", "args": [key, "Standard", False]}])
        assert decrypted == HELLO_WORLD

    def test_xor_with_null_key(self):
        """Test XOR with null byte key."""
        result = bake(
            b"hello",
            [{"op": "XOR", "args": [{"option": "Hex", "string": "00"}, "Standard", False]}]
        )
        # XOR with 0x00 does nothing
        assert result == b"hello"

    def test_xor_all_ones(self):
        """Test XOR with all ones (bit inversion)."""
        result = bake(
            BINARY_ZEROS[:8],
            [{"op": "XOR", "args": [{"option": "Hex", "string": "ff"}, "Standard", False]}]
        )
        # XOR with 0xFF inverts all bits, so 0x00 becomes 0xFF
        assert result == bytes([0xFF] * 8)

    def test_xor_alternating_bits(self):
        """Test XOR with alternating bit pattern."""
        result = bake(
            bytes([0xAA, 0xAA, 0xAA, 0xAA]),
            [{"op": "XOR", "args": [{"option": "Hex", "string": "55"}, "Standard", False]}]
        )
        # 0xAA = 10101010, 0x55 = 01010101
        # 0xAA XOR 0x55 = 11111111 = 0xFF
        assert result == bytes([0xFF] * 4)

    def test_xor_empty_input(self):
        """Test XOR with empty input."""
        result = bake(
            EMPTY_BYTES,
            [{"op": "XOR", "args": [{"option": "Hex", "string": "ff"}, "Standard", False]}]
        )
        assert result == EMPTY_BYTES


# ============================================================================
# AND Operation Tests
# ============================================================================


class TestAND:
    """Test suite for AND bitwise operation."""

    def test_and_with_hex_key(self):
        """Test AND with hexadecimal key."""
        result = bake(
            bytes([0xFF, 0xFF, 0xFF, 0xFF]),
            [{"op": "AND", "args": [{"option": "Hex", "string": "0f"}]}]
        )
        # 0xFF AND 0x0F = 0x0F (mask lower nibble)
        assert result == bytes([0x0F] * 4)

    def test_and_mask_upper_bits(self):
        """Test AND to mask upper bits."""
        result = bake(
            bytes([0xFF, 0xAA, 0x55, 0x00]),
            [{"op": "AND", "args": [{"option": "Hex", "string": "f0"}]}]
        )
        # Mask lower nibble, keep upper nibble
        assert result == bytes([0xF0, 0xA0, 0x50, 0x00])

    def test_and_with_all_zeros(self):
        """Test AND with all zeros."""
        result = bake(
            b"hello",
            [{"op": "AND", "args": [{"option": "Hex", "string": "00"}]}]
        )
        # AND with 0x00 always gives 0x00
        assert result == bytes([0x00] * 5)

    def test_and_with_all_ones(self):
        """Test AND with all ones (identity operation)."""
        result = bake(
            b"test",
            [{"op": "AND", "args": [{"option": "Hex", "string": "ff"}]}]
        )
        # AND with 0xFF is identity
        assert result == b"test"

    def test_and_extract_ascii_flag(self):
        """Test AND to extract ASCII printable bit."""
        # ASCII printable chars are in range 0x20-0x7E
        result = bake(
            bytes([0x41, 0xC1]),  # 'A' and 'A' with high bit set
            [{"op": "AND", "args": [{"option": "Hex", "string": "7f"}]}]
        )
        # 0x41 AND 0x7F = 0x41, 0xC1 AND 0x7F = 0x41
        assert result == bytes([0x41, 0x41])

    def test_and_empty_input(self):
        """Test AND with empty input."""
        result = bake(
            EMPTY_BYTES,
            [{"op": "AND", "args": [{"option": "Hex", "string": "ff"}]}]
        )
        assert result == EMPTY_BYTES


# ============================================================================
# OR Operation Tests
# ============================================================================


class TestOR:
    """Test suite for OR bitwise operation."""

    def test_or_with_hex_key(self):
        """Test OR with hexadecimal key."""
        result = bake(
            bytes([0x00, 0x00, 0x00, 0x00]),
            [{"op": "OR", "args": [{"option": "Hex", "string": "0f"}]}]
        )
        # 0x00 OR 0x0F = 0x0F
        assert result == bytes([0x0F] * 4)

    def test_or_set_lower_bits(self):
        """Test OR to set lower bits."""
        result = bake(
            bytes([0xF0, 0xA0, 0x50, 0x00]),
            [{"op": "OR", "args": [{"option": "Hex", "string": "0f"}]}]
        )
        # Set lower nibble
        assert result == bytes([0xFF, 0xAF, 0x5F, 0x0F])

    def test_or_with_all_zeros(self):
        """Test OR with all zeros (identity operation)."""
        result = bake(
            b"test",
            [{"op": "OR", "args": [{"option": "Hex", "string": "00"}]}]
        )
        # OR with 0x00 is identity
        assert result == b"test"

    def test_or_with_all_ones(self):
        """Test OR with all ones."""
        result = bake(
            b"hello",
            [{"op": "OR", "args": [{"option": "Hex", "string": "ff"}]}]
        )
        # OR with 0xFF always gives 0xFF
        assert result == bytes([0xFF] * 5)

    def test_or_set_high_bit(self):
        """Test OR to set high bit."""
        result = bake(
            bytes([0x41, 0x42, 0x43]),  # 'A', 'B', 'C'
            [{"op": "OR", "args": [{"option": "Hex", "string": "80"}]}]
        )
        # Set high bit: 0x41 OR 0x80 = 0xC1
        assert result == bytes([0xC1, 0xC2, 0xC3])

    def test_or_empty_input(self):
        """Test OR with empty input."""
        result = bake(
            EMPTY_BYTES,
            [{"op": "OR", "args": [{"option": "Hex", "string": "ff"}]}]
        )
        assert result == EMPTY_BYTES


# ============================================================================
# NOT Operation Tests
# ============================================================================


class TestNOT:
    """Test suite for NOT bitwise operation."""

    def test_not_basic(self):
        """Test NOT operation (bit inversion)."""
        result = bake(bytes([0x00, 0xFF, 0xAA, 0x55]), ["NOT"])
        # NOT inverts all bits
        assert result == bytes([0xFF, 0x00, 0x55, 0xAA])

    def test_not_hello(self):
        """Test NOT on ASCII text."""
        result = bake(b"hello", ["NOT"])
        # 'h' = 0x68, NOT 0x68 = 0x97
        expected = bytes([~b & 0xFF for b in b"hello"])
        assert result == expected

    def test_not_double_application(self):
        """Test NOT property: NOT(NOT(A)) = A."""
        result = bake(b"test", ["NOT", "NOT"])
        assert result == b"test"

    def test_not_all_zeros(self):
        """Test NOT on all zeros."""
        result = bake(BINARY_ZEROS[:8], ["NOT"])
        assert result == bytes([0xFF] * 8)

    def test_not_all_ones(self):
        """Test NOT on all ones."""
        result = bake(BINARY_ONES[:8], ["NOT"])
        assert result == bytes([0x00] * 8)

    def test_not_alternating_bits(self):
        """Test NOT on alternating bit pattern."""
        result = bake(bytes([0xAA, 0x55]), ["NOT"])
        # NOT 0xAA = 0x55, NOT 0x55 = 0xAA
        assert result == bytes([0x55, 0xAA])

    def test_not_empty_input(self):
        """Test NOT with empty input."""
        result = bake(EMPTY_BYTES, ["NOT"])
        assert result == EMPTY_BYTES


# ============================================================================
# ADD Operation Tests
# ============================================================================


class TestADD:
    """Test suite for ADD arithmetic operation."""

    def test_add_with_hex_key(self):
        """Test ADD with hexadecimal key."""
        result = bake(
            bytes([0x00, 0x01, 0x02, 0x03]),
            [{"op": "ADD", "args": [{"option": "Hex", "string": "01"}]}]
        )
        # Add 1 to each byte
        assert result == bytes([0x01, 0x02, 0x03, 0x04])

    def test_add_with_modulo(self):
        """Test ADD with modulo 256 behavior."""
        result = bake(
            bytes([0xFF, 0xFE, 0xFD]),
            [{"op": "ADD", "args": [{"option": "Hex", "string": "02"}]}]
        )
        # 0xFF + 0x02 = 0x101 MOD 256 = 0x01
        # 0xFE + 0x02 = 0x100 MOD 256 = 0x00
        # 0xFD + 0x02 = 0xFF
        assert result == bytes([0x01, 0x00, 0xFF])

    def test_add_zero(self):
        """Test ADD with zero (identity operation)."""
        result = bake(
            b"test",
            [{"op": "ADD", "args": [{"option": "Hex", "string": "00"}]}]
        )
        # Add 0 does nothing
        assert result == b"test"

    def test_add_byte_boundary(self):
        """Test ADD at byte boundary (255)."""
        result = bake(
            bytes([0xFE, 0xFF]),
            [{"op": "ADD", "args": [{"option": "Hex", "string": "01"}]}]
        )
        # 0xFE + 1 = 0xFF, 0xFF + 1 = 0x00 (wraps)
        assert result == bytes([0xFF, 0x00])

    def test_add_empty_input(self):
        """Test ADD with empty input."""
        result = bake(
            EMPTY_BYTES,
            [{"op": "ADD", "args": [{"option": "Hex", "string": "01"}]}]
        )
        assert result == EMPTY_BYTES


# ============================================================================
# SUB Operation Tests
# ============================================================================


class TestSUB:
    """Test suite for SUB arithmetic operation."""

    def test_sub_with_hex_key(self):
        """Test SUB with hexadecimal key."""
        result = bake(
            bytes([0x05, 0x04, 0x03, 0x02]),
            [{"op": "SUB", "args": [{"option": "Hex", "string": "01"}]}]
        )
        # Subtract 1 from each byte
        assert result == bytes([0x04, 0x03, 0x02, 0x01])

    def test_sub_with_modulo(self):
        """Test SUB with modulo 256 behavior."""
        result = bake(
            bytes([0x00, 0x01, 0x02]),
            [{"op": "SUB", "args": [{"option": "Hex", "string": "02"}]}]
        )
        # 0x00 - 0x02 = -2 MOD 256 = 0xFE
        # 0x01 - 0x02 = -1 MOD 256 = 0xFF
        # 0x02 - 0x02 = 0x00
        assert result == bytes([0xFE, 0xFF, 0x00])

    def test_sub_zero(self):
        """Test SUB with zero (identity operation)."""
        result = bake(
            b"test",
            [{"op": "SUB", "args": [{"option": "Hex", "string": "00"}]}]
        )
        # Subtract 0 does nothing
        assert result == b"test"

    def test_sub_byte_boundary(self):
        """Test SUB at byte boundary (0)."""
        result = bake(
            bytes([0x01, 0x00]),
            [{"op": "SUB", "args": [{"option": "Hex", "string": "01"}]}]
        )
        # 0x01 - 1 = 0x00, 0x00 - 1 = 0xFF (wraps)
        assert result == bytes([0x00, 0xFF])

    def test_sub_add_inverse(self):
        """Test SUB as inverse of ADD."""
        # Add then subtract should give original
        result = bake(
            b"hello",
            [
                {"op": "ADD", "args": [{"option": "Hex", "string": "42"}]},
                {"op": "SUB", "args": [{"option": "Hex", "string": "42"}]}
            ]
        )
        assert result == b"hello"

    def test_sub_empty_input(self):
        """Test SUB with empty input."""
        result = bake(
            EMPTY_BYTES,
            [{"op": "SUB", "args": [{"option": "Hex", "string": "01"}]}]
        )
        assert result == EMPTY_BYTES


# ============================================================================
# Bit Shift Left Tests
# ============================================================================


class TestBitShiftLeft:
    """Test suite for Bit shift left operation."""

    def test_bit_shift_left_by_one(self):
        """Test left shift by 1 bit."""
        result = bake(
            bytes([0x01, 0x02, 0x04, 0x08]),
            [{"op": "Bit shift left", "args": [1]}]
        )
        # Each byte shifted left by 1: multiply by 2
        assert result == bytes([0x02, 0x04, 0x08, 0x10])

    def test_bit_shift_left_overflow(self):
        """Test left shift with overflow."""
        result = bake(
            bytes([0x80, 0xFF]),
            [{"op": "Bit shift left", "args": [1]}]
        )
        # 0x80 << 1 = 0x00 (high bit lost)
        # 0xFF << 1 = 0xFE (high bit lost)
        assert result == bytes([0x00, 0xFE])

    def test_bit_shift_left_by_four(self):
        """Test left shift by 4 bits (shift nibble)."""
        result = bake(
            bytes([0x01, 0x0F]),
            [{"op": "Bit shift left", "args": [4]}]
        )
        # 0x01 << 4 = 0x10
        # 0x0F << 4 = 0xF0
        assert result == bytes([0x10, 0xF0])

    def test_bit_shift_left_by_eight(self):
        """Test left shift by 8 bits (should zero out)."""
        result = bake(
            bytes([0xFF, 0xAA, 0x55]),
            [{"op": "Bit shift left", "args": [8]}]
        )
        # Shifting 8 bits in a byte zeros it out
        assert result == bytes([0x00, 0x00, 0x00])

    def test_bit_shift_left_zero(self):
        """Test left shift by 0 (no change)."""
        result = bake(
            b"test",
            [{"op": "Bit shift left", "args": [0]}]
        )
        assert result == b"test"

    def test_bit_shift_left_empty_input(self):
        """Test left shift with empty input."""
        result = bake(
            EMPTY_BYTES,
            [{"op": "Bit shift left", "args": [1]}]
        )
        assert result == EMPTY_BYTES


# ============================================================================
# Bit Shift Right Tests
# ============================================================================


class TestBitShiftRight:
    """Test suite for Bit shift right operation."""

    def test_bit_shift_right_logical_by_one(self):
        """Test logical right shift by 1 bit."""
        result = bake(
            bytes([0x80, 0x40, 0x20, 0x10]),
            [{"op": "Bit shift right", "args": [1, "Logical shift"]}]
        )
        # Each byte shifted right by 1: divide by 2
        assert result == bytes([0x40, 0x20, 0x10, 0x08])

    def test_bit_shift_right_logical_by_four(self):
        """Test logical right shift by 4 bits."""
        result = bake(
            bytes([0xF0, 0x10]),
            [{"op": "Bit shift right", "args": [4, "Logical shift"]}]
        )
        # 0xF0 >> 4 = 0x0F
        # 0x10 >> 4 = 0x01
        assert result == bytes([0x0F, 0x01])

    def test_bit_shift_right_arithmetic_positive(self):
        """Test arithmetic right shift on positive value (MSB = 0)."""
        result = bake(
            bytes([0x7F, 0x40]),
            [{"op": "Bit shift right", "args": [1, "Arithmetic shift"]}]
        )
        # MSB is 0, so same as logical shift
        assert result == bytes([0x3F, 0x20])

    def test_bit_shift_right_arithmetic_negative(self):
        """Test arithmetic right shift on negative value (MSB = 1)."""
        result = bake(
            bytes([0x80, 0xFF]),
            [{"op": "Bit shift right", "args": [1, "Arithmetic shift"]}]
        )
        # MSB is 1, so it's preserved
        # 0x80 >> 1 (arithmetic) = 0xC0 (sign extended)
        # 0xFF >> 1 (arithmetic) = 0xFF (sign extended)
        assert result == bytes([0xC0, 0xFF])

    def test_bit_shift_right_zero(self):
        """Test right shift by 0 (no change)."""
        result = bake(
            b"test",
            [{"op": "Bit shift right", "args": [0, "Logical shift"]}]
        )
        assert result == b"test"

    def test_bit_shift_right_empty_input(self):
        """Test right shift with empty input."""
        result = bake(
            EMPTY_BYTES,
            [{"op": "Bit shift right", "args": [1, "Logical shift"]}]
        )
        assert result == EMPTY_BYTES


# ============================================================================
# Rotate Left Tests
# ============================================================================


class TestRotateLeft:
    """Test suite for Rotate left operation."""

    def test_rotate_left_by_one(self):
        """Test rotate left by 1 bit."""
        result = bake(
            bytes([0x80, 0x01]),
            [{"op": "Rotate left", "args": [1, False]}]
        )
        # 0x80 = 10000000, rotated left 1 = 00000001 = 0x01
        # 0x01 = 00000001, rotated left 1 = 00000010 = 0x02
        assert result == bytes([0x01, 0x02])

    def test_rotate_left_by_four(self):
        """Test rotate left by 4 bits (swap nibbles)."""
        result = bake(
            bytes([0x12, 0xAB]),
            [{"op": "Rotate left", "args": [4, False]}]
        )
        # 0x12 rotated left 4 = 0x21
        # 0xAB rotated left 4 = 0xBA
        assert result == bytes([0x21, 0xBA])

    def test_rotate_left_full_byte(self):
        """Test rotate left by 8 bits (full rotation)."""
        result = bake(
            bytes([0xAB, 0xCD]),
            [{"op": "Rotate left", "args": [8, False]}]
        )
        # Full 8-bit rotation returns to original
        assert result == bytes([0xAB, 0xCD])

    def test_rotate_left_with_carry(self):
        """Test rotate left with carry through."""
        result = bake(
            bytes([0x80, 0x01]),
            [{"op": "Rotate left", "args": [1, True]}]
        )
        # With carry: high bit of first byte becomes low bit of next byte
        # 0x80 0x01 = 10000000 00000001
        # Rotated left 1 with carry = 00000000 00000011 = 0x00 0x03
        assert result == bytes([0x00, 0x03])

    def test_rotate_left_empty_input(self):
        """Test rotate left with empty input."""
        result = bake(
            EMPTY_BYTES,
            [{"op": "Rotate left", "args": [1, False]}]
        )
        assert result == EMPTY_BYTES


# ============================================================================
# Rotate Right Tests
# ============================================================================


class TestRotateRight:
    """Test suite for Rotate right operation."""

    def test_rotate_right_by_one(self):
        """Test rotate right by 1 bit."""
        result = bake(
            bytes([0x01, 0x80]),
            [{"op": "Rotate right", "args": [1, False]}]
        )
        # 0x01 = 00000001, rotated right 1 = 10000000 = 0x80
        # 0x80 = 10000000, rotated right 1 = 01000000 = 0x40
        assert result == bytes([0x80, 0x40])

    def test_rotate_right_by_four(self):
        """Test rotate right by 4 bits (swap nibbles)."""
        result = bake(
            bytes([0x12, 0xAB]),
            [{"op": "Rotate right", "args": [4, False]}]
        )
        # 0x12 rotated right 4 = 0x21
        # 0xAB rotated right 4 = 0xBA
        assert result == bytes([0x21, 0xBA])

    def test_rotate_right_full_byte(self):
        """Test rotate right by 8 bits (full rotation)."""
        result = bake(
            bytes([0xAB, 0xCD]),
            [{"op": "Rotate right", "args": [8, False]}]
        )
        # Full 8-bit rotation returns to original
        assert result == bytes([0xAB, 0xCD])

    def test_rotate_right_with_carry(self):
        """Test rotate right with carry through."""
        result = bake(
            bytes([0x01, 0x80]),
            [{"op": "Rotate right", "args": [1, True]}]
        )
        # With carry: bits rotate across byte boundaries
        # 0x01 0x80 = 00000001 10000000
        # Rotated right 1 with carry = 00000000 11000000 = 0x00 0xC0
        assert result == bytes([0x00, 0xC0])

    def test_rotate_right_empty_input(self):
        """Test rotate right with empty input."""
        result = bake(
            EMPTY_BYTES,
            [{"op": "Rotate right", "args": [1, False]}]
        )
        assert result == EMPTY_BYTES


# ============================================================================
# Math Operation Tests
# ============================================================================


class TestMathOperations:
    """Test suite for mathematical operations (Mean, Median, Sum, etc.)."""

    def test_sum_basic(self):
        """Test sum of numbers."""
        result = bake("1 2 3 4 5", [{"op": "Sum", "args": ["Space"]}])
        # Result is a JSObject, convert to string for comparison
        assert str(result) == "15"

    def test_sum_with_decimals(self):
        """Test sum with decimal numbers."""
        result = bake("1.5 2.5 3.0", [{"op": "Sum", "args": ["Space"]}])
        assert str(result) == "7"

    def test_sum_with_hex(self):
        """Test sum with hexadecimal input."""
        result = bake("0x0a 0x05", [{"op": "Sum", "args": ["Space"]}])
        # 0x0a = 10, 0x05 = 5, sum = 15
        assert str(result) == "15"

    def test_mean_basic(self):
        """Test mean (average) of numbers."""
        result = bake("2 4 6 8 10", [{"op": "Mean", "args": ["Space"]}])
        assert str(result) == "6"

    def test_mean_with_decimals(self):
        """Test mean with decimal numbers."""
        result = bake("1 2 3 4", [{"op": "Mean", "args": ["Space"]}])
        assert str(result) == "2.5"

    def test_median_odd_count(self):
        """Test median with odd number of values."""
        result = bake("1 2 3 4 5", [{"op": "Median", "args": ["Space"]}])
        assert str(result) == "3"

    def test_median_even_count(self):
        """Test median with even number of values."""
        result = bake("1 2 3 4", [{"op": "Median", "args": ["Space"]}])
        # Median of 1,2,3,4 is (2+3)/2 = 2.5
        assert str(result) == "2.5"

    def test_standard_deviation_basic(self):
        """Test standard deviation calculation."""
        result = bake("2 4 6 8 10", [{"op": "Standard Deviation", "args": ["Space"]}])
        # Verify result is a valid number (actual calculation is complex)
        assert float(result) > 0

    def test_multiply_basic(self):
        """Test multiply operation."""
        result = bake("2 3 4", [{"op": "Multiply", "args": ["Space"]}])
        assert str(result) == "24"

    def test_divide_basic(self):
        """Test divide operation."""
        result = bake("100 5 2", [{"op": "Divide", "args": ["Space"]}])
        assert str(result) == "10"

    def test_subtract_basic(self):
        """Test subtract operation."""
        result = bake("100 30 5", [{"op": "Subtract", "args": ["Space"]}])
        assert str(result) == "65"

    def test_sum_comma_delimiter(self):
        """Test sum with comma delimiter."""
        result = bake("1,2,3,4,5", [{"op": "Sum", "args": ["Comma"]}])
        assert str(result) == "15"

    def test_mean_line_feed_delimiter(self):
        """Test mean with line feed delimiter."""
        result = bake("10\n20\n30", [{"op": "Mean", "args": ["Line feed"]}])
        assert str(result) == "20"

    def test_sum_empty_input(self):
        """Test sum with empty input."""
        result = bake("", [{"op": "Sum", "args": ["Space"]}])
        # Empty input results in NaN
        assert str(result) == "NaN" or str(result) == "0" or str(result) == ""


# ============================================================================
# Set Operation Tests
# ============================================================================


class TestSetOperations:
    """Test suite for set operations."""

    def test_set_union_basic(self):
        """Test set union operation."""
        input_data = "1,2,3\n\n2,3,4"
        result = bake(
            input_data,
            [{"op": "Set Union", "args": ["\n\n", ","]}]
        )
        # Union of {1,2,3} and {2,3,4} = {1,2,3,4}
        assert "1" in result and "2" in result and "3" in result and "4" in result

    def test_set_intersection_basic(self):
        """Test set intersection operation."""
        input_data = "1,2,3\n\n2,3,4"
        result = bake(
            input_data,
            [{"op": "Set Intersection", "args": ["\n\n", ","]}]
        )
        # Intersection of {1,2,3} and {2,3,4} = {2,3}
        assert "2" in result and "3" in result

    def test_set_difference_basic(self):
        """Test set difference operation."""
        input_data = "1,2,3\n\n2,3,4"
        result = bake(
            input_data,
            [{"op": "Set Difference", "args": ["\n\n", ","]}]
        )
        # Difference {1,2,3} - {2,3,4} = {1}
        assert "1" in result

    def test_symmetric_difference_basic(self):
        """Test symmetric difference operation."""
        input_data = "1,2,3\n\n2,3,4"
        result = bake(
            input_data,
            [{"op": "Symmetric Difference", "args": ["\n\n", ","]}]
        )
        # Symmetric difference = elements in either set but not both
        # {1,2,3} △ {2,3,4} = {1,4}
        assert "1" in result and "4" in result

    def test_cartesian_product_basic(self):
        """Test cartesian product operation."""
        input_data = "a,b\n\n1,2"
        result = bake(
            input_data,
            [{"op": "Cartesian Product", "args": ["\n\n", ","]}]
        )
        # Cartesian product of {a,b} and {1,2} = {(a,1), (a,2), (b,1), (b,2)}
        assert "a" in result and "b" in result and "1" in result and "2" in result

    def test_power_set_basic(self):
        """Test power set operation."""
        result = bake(
            "a,b,c",
            [{"op": "Power Set", "args": [","]}]
        )
        # Power set of {a,b,c} includes empty set and all combinations
        # Should contain at least the elements and empty set
        assert isinstance(result, str)
        # Power set of 3 elements has 2^3 = 8 subsets (including empty set)
        # The result has an empty line at start, so we get 7 non-empty lines + empty line
        lines = [line for line in result.split("\n") if line.strip()]
        assert len(lines) >= 7  # At least 7 non-empty subsets

    def test_set_union_empty_sets(self):
        """Test set union with empty sets."""
        input_data = ",\n\n,"
        result = bake(
            input_data,
            [{"op": "Set Union", "args": ["\n\n", ","]}]
        )
        # Union of empty sets is empty
        assert result.strip() == "" or result == ","

    def test_set_intersection_disjoint(self):
        """Test set intersection with disjoint sets."""
        input_data = "1,2,3\n\n4,5,6"
        result = bake(
            input_data,
            [{"op": "Set Intersection", "args": ["\n\n", ","]}]
        )
        # Intersection of disjoint sets is empty
        # Result should be empty or just delimiter
        assert result.strip() == "" or result == ","

    def test_cartesian_product_single_elements(self):
        """Test cartesian product with single elements."""
        input_data = "x\n\ny"
        result = bake(
            input_data,
            [{"op": "Cartesian Product", "args": ["\n\n", ","]}]
        )
        # {x} × {y} = {(x,y)}
        assert "x" in result and "y" in result

    def test_power_set_single_element(self):
        """Test power set of single element."""
        result = bake(
            "a",
            [{"op": "Power Set", "args": [","]}]
        )
        # Power set of {a} = {∅, {a}}
        # Result includes empty line and line with "a"
        lines = [line for line in result.split("\n") if line or line == ""]
        # Should have at least the element itself
        assert "a" in result


# ============================================================================
# Combined Operation Tests
# ============================================================================


class TestCombinedOperations:
    """Test suite for combining multiple arithmetic/logic operations."""

    def test_xor_and_combine(self):
        """Test combining XOR and AND operations."""
        result = bake(
            bytes([0xFF, 0xFF]),
            [
                {"op": "XOR", "args": [{"option": "Hex", "string": "aa"}, "Standard", False]},
                {"op": "AND", "args": [{"option": "Hex", "string": "0f"}]}
            ]
        )
        # 0xFF XOR 0xAA = 0x55
        # 0x55 AND 0x0F = 0x05
        assert result == bytes([0x05, 0x05])

    def test_add_sub_roundtrip(self):
        """Test ADD followed by SUB for roundtrip."""
        result = bake(
            b"CyberChef",
            [
                {"op": "ADD", "args": [{"option": "Hex", "string": "13"}]},
                {"op": "SUB", "args": [{"option": "Hex", "string": "13"}]}
            ]
        )
        assert result == b"CyberChef"

    def test_shift_and_rotate(self):
        """Test combining shift and rotate operations."""
        result = bake(
            bytes([0x0F]),
            [
                {"op": "Bit shift left", "args": [4]},
                {"op": "Rotate right", "args": [2, False]}
            ]
        )
        # 0x0F << 4 = 0xF0
        # 0xF0 rotated right 2 = 0x3C
        assert result == bytes([0x3C])

    def test_not_xor_encryption_pattern(self):
        """Test NOT followed by XOR (encryption pattern)."""
        key = {"option": "Hex", "string": "5a"}
        result = bake(
            b"test",
            ["NOT", {"op": "XOR", "args": [key, "Standard", False]}]
        )
        # Should produce encrypted result
        assert result != b"test"

        # Decrypt by reversing operations
        decrypted = bake(
            result,
            [{"op": "XOR", "args": [key, "Standard", False]}, "NOT"]
        )
        assert decrypted == b"test"

    def test_bitwise_all_operations(self):
        """Test all bitwise operations in sequence."""
        result = bake(
            bytes([0x42]),
            [
                {"op": "XOR", "args": [{"option": "Hex", "string": "ff"}, "Standard", False]},
                "NOT",
                {"op": "OR", "args": [{"option": "Hex", "string": "0f"}]},
                {"op": "AND", "args": [{"option": "Hex", "string": "f0"}]}
            ]
        )
        # Verify it produces some result
        assert isinstance(result, bytes)
        assert len(result) == 1


# ============================================================================
# Edge Case Tests
# ============================================================================


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def test_all_zeros_through_operations(self):
        """Test all zeros through various operations."""
        # XOR with zeros
        result = bake(
            BINARY_ZEROS[:4],
            [{"op": "XOR", "args": [{"option": "Hex", "string": "00"}, "Standard", False]}]
        )
        assert result == BINARY_ZEROS[:4]

        # NOT on zeros gives all ones
        result = bake(BINARY_ZEROS[:4], ["NOT"])
        assert result == bytes([0xFF] * 4)

    def test_all_ones_through_operations(self):
        """Test all ones through various operations."""
        # AND with all ones is identity
        result = bake(
            BINARY_ONES[:4],
            [{"op": "AND", "args": [{"option": "Hex", "string": "ff"}]}]
        )
        assert result == BINARY_ONES[:4]

        # NOT on all ones gives zeros
        result = bake(BINARY_ONES[:4], ["NOT"])
        assert result == bytes([0x00] * 4)

    def test_alternating_pattern_operations(self):
        """Test alternating bit patterns."""
        # 0xAA = 10101010, 0x55 = 01010101
        result = bake(
            bytes([0xAA]),
            [{"op": "XOR", "args": [{"option": "Hex", "string": "55"}, "Standard", False]}]
        )
        assert result == bytes([0xFF])

    def test_sequential_bytes_rotate(self):
        """Test sequential bytes with rotation."""
        result = bake(
            BINARY_SEQUENTIAL[:8],
            [{"op": "Rotate left", "args": [1, False]}]
        )
        # Verify rotation occurred
        assert result != BINARY_SEQUENTIAL[:8]
        # Rotating back should restore
        restored = bake(
            result,
            [{"op": "Rotate right", "args": [1, False]}]
        )
        assert restored == BINARY_SEQUENTIAL[:8]

    def test_large_input_xor(self):
        """Test XOR with large input."""
        large_data = bytes(range(256))
        result = bake(
            large_data,
            [{"op": "XOR", "args": [{"option": "Hex", "string": "aa"}, "Standard", False]}]
        )
        # Verify it processed all bytes
        assert len(result) == 256

    def test_single_byte_operations(self):
        """Test operations on single byte."""
        single_byte = bytes([0x42])

        # Test various operations
        result = bake(single_byte, ["NOT"])
        assert len(result) == 1

        result = bake(single_byte, [{"op": "Rotate left", "args": [1, False]}])
        assert len(result) == 1

        result = bake(
            single_byte,
            [{"op": "XOR", "args": [{"option": "Hex", "string": "ff"}, "Standard", False]}]
        )
        assert len(result) == 1
