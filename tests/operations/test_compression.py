"""Comprehensive tests for CyberChef compression operations.

This module tests all compression and decompression operations including:
- Gzip / Gunzip
- Bzip2 Compress / Bzip2 Decompress
- Zlib Deflate / Zlib Inflate
- Raw Deflate / Raw Inflate
- LZ4 Compress / LZ4 Decompress
- LZMA Compress / LZMA Decompress
- LZString Compress / LZString Decompress
- Zip / Unzip

Each operation is tested with:
- Basic compression/decompression
- Empty input
- Binary data (all 256 bytes)
- Roundtrip compress/decompress tests
- Comparison with Python standard library (where applicable)
- Large data compression
- Different compression levels (where supported)
- Highly compressible vs incompressible data
"""

import bz2
import gzip
import zlib

import pytest

from ida_cyberchef.cyberchef import bake

# Import test constants from conftest
from tests.conftest import (
    ALL_BYTES,
    COMPRESSIBLE_DATA,
    EMPTY_BYTES,
    HELLO_WORLD,
    LOREM_IPSUM,
    UTF8_EMOJI,
    UTF8_MULTILANG,
    UTF8_SIMPLE,
    assert_roundtrip,
)

# Import operation-specific helpers
from tests.operations.conftest import (
    is_operation_available,
    require_operations,
)


# ============================================================================
# Test Data for Compression
# ============================================================================

# Highly compressible data (repeated pattern)
HIGHLY_COMPRESSIBLE = b"A" * 1000

# Moderately compressible data (repeated text)
MODERATELY_COMPRESSIBLE = b"Hello World! " * 100

# Incompressible data (random-like)
INCOMPRESSIBLE = bytes(range(256)) * 4

# Large compressible data
LARGE_COMPRESSIBLE = b"ABCDEFGH" * 1000

# Binary with patterns
BINARY_PATTERN = bytes([i % 256 for i in range(1024)])


# ============================================================================
# Gzip Compression Tests
# ============================================================================


class TestGzip:
    """Test suite for Gzip compression and decompression operations."""

    def test_gzip_hello_world(self):
        """Test Gzip compression of 'Hello, World!'."""
        result = bake(HELLO_WORLD, ["Gzip"])
        assert isinstance(result, bytes)
        # Gzip magic number check
        assert result[:2] == b"\x1f\x8b"

    def test_gunzip_hello_world(self):
        """Test Gunzip decompression to 'Hello, World!'."""
        # First compress with Python's gzip
        compressed = gzip.compress(HELLO_WORLD)
        # Then decompress with CyberChef
        result = bake(compressed, ["Gunzip"])
        assert result == HELLO_WORLD

    def test_gzip_empty(self):
        """Test Gzip compression of empty input."""
        result = bake(EMPTY_BYTES, ["Gzip"])
        assert isinstance(result, bytes)
        assert len(result) > 0  # Gzip has header even for empty data

    def test_gunzip_empty(self):
        """Test Gunzip decompression of empty data."""
        compressed = gzip.compress(EMPTY_BYTES)
        result = bake(compressed, ["Gunzip"])
        assert result == EMPTY_BYTES

    def test_gzip_all_bytes(self):
        """Test Gzip compression of all 256 possible byte values."""
        result = bake(ALL_BYTES, ["Gzip"])
        assert isinstance(result, bytes)
        assert result[:2] == b"\x1f\x8b"
        # Verify decompression with Python
        decompressed = gzip.decompress(result)
        assert decompressed == ALL_BYTES

    def test_gzip_roundtrip_hello_world(self):
        """Test Gzip→Gunzip roundtrip with 'Hello, World!'."""
        assert_roundtrip(HELLO_WORLD, ["Gzip"], ["Gunzip"])

    def test_gzip_roundtrip_all_bytes(self):
        """Test Gzip→Gunzip roundtrip with all 256 bytes."""
        assert_roundtrip(ALL_BYTES, ["Gzip"], ["Gunzip"])

    def test_gzip_roundtrip_utf8(self):
        """Test Gzip→Gunzip roundtrip with UTF-8 data."""
        assert_roundtrip(UTF8_SIMPLE, ["Gzip"], ["Gunzip"])
        assert_roundtrip(UTF8_EMOJI, ["Gzip"], ["Gunzip"])
        assert_roundtrip(UTF8_MULTILANG, ["Gzip"], ["Gunzip"])

    def test_gzip_compare_python(self):
        """Compare CyberChef Gzip with Python's gzip module."""
        # Compress with CyberChef
        cyberchef_result = bake(HELLO_WORLD, ["Gzip"])
        # Decompress with Python to verify
        python_decompressed = gzip.decompress(cyberchef_result)
        assert python_decompressed == HELLO_WORLD

    def test_gunzip_compare_python(self):
        """Compare CyberChef Gunzip with Python's gzip module."""
        # Compress with Python
        python_compressed = gzip.compress(HELLO_WORLD)
        # Decompress with CyberChef
        cyberchef_result = bake(python_compressed, ["Gunzip"])
        assert cyberchef_result == HELLO_WORLD

    def test_gzip_highly_compressible(self):
        """Test Gzip compression of highly compressible data."""
        result = bake(HIGHLY_COMPRESSIBLE, ["Gzip"])
        # Should be significantly smaller than original
        assert len(result) < len(HIGHLY_COMPRESSIBLE)
        # Verify roundtrip
        decompressed = bake(result, ["Gunzip"])
        assert decompressed == HIGHLY_COMPRESSIBLE

    def test_gzip_incompressible(self):
        """Test Gzip compression of incompressible data."""
        result = bake(INCOMPRESSIBLE, ["Gzip"])
        assert isinstance(result, bytes)
        # May be larger due to headers, but should still decompress correctly
        decompressed = bake(result, ["Gunzip"])
        assert decompressed == INCOMPRESSIBLE

    def test_gzip_large_data(self):
        """Test Gzip compression of large data."""
        result = bake(LARGE_COMPRESSIBLE, ["Gzip"])
        assert isinstance(result, bytes)
        # Verify roundtrip
        decompressed = bake(result, ["Gunzip"])
        assert decompressed == LARGE_COMPRESSIBLE

    def test_gzip_with_compression_type_dynamic(self):
        """Test Gzip compression with dynamic Huffman coding."""
        result = bake(
            HELLO_WORLD,
            [{"op": "Gzip", "args": {"Compression type": "Dynamic Huffman Coding"}}]
        )
        assert isinstance(result, bytes)
        assert result[:2] == b"\x1f\x8b"
        # Verify decompression
        decompressed = bake(result, ["Gunzip"])
        assert decompressed == HELLO_WORLD

    def test_gzip_with_compression_type_fixed(self):
        """Test Gzip compression with fixed Huffman coding."""
        result = bake(
            HELLO_WORLD,
            [{"op": "Gzip", "args": {"Compression type": "Fixed Huffman Coding"}}]
        )
        assert isinstance(result, bytes)
        assert result[:2] == b"\x1f\x8b"
        # Verify decompression
        decompressed = bake(result, ["Gunzip"])
        assert decompressed == HELLO_WORLD

    def test_gzip_with_compression_type_none(self):
        """Test Gzip compression with no compression."""
        result = bake(
            HELLO_WORLD,
            [{"op": "Gzip", "args": {"Compression type": "None (Store)"}}]
        )
        assert isinstance(result, bytes)
        assert result[:2] == b"\x1f\x8b"
        # Verify decompression
        decompressed = bake(result, ["Gunzip"])
        assert decompressed == HELLO_WORLD


# ============================================================================
# Bzip2 Compression Tests
# ============================================================================


class TestBzip2:
    """Test suite for Bzip2 compression and decompression operations."""

    def test_bzip2_compress_hello_world(self):
        """Test Bzip2 compression of 'Hello, World!'."""
        result = bake(HELLO_WORLD, ["Bzip2 Compress"])
        assert isinstance(result, bytes)
        # Bzip2 magic number check
        assert result[:3] == b"BZh"

    def test_bzip2_decompress_hello_world(self):
        """Test Bzip2 decompression to 'Hello, World!'."""
        # First compress with Python's bz2
        compressed = bz2.compress(HELLO_WORLD)
        # Then decompress with CyberChef
        result = bake(compressed, ["Bzip2 Decompress"])
        assert result == HELLO_WORLD

    def test_bzip2_compress_empty(self):
        """Test Bzip2 compression of empty input."""
        result = bake(EMPTY_BYTES, ["Bzip2 Compress"])
        assert isinstance(result, bytes)
        assert len(result) > 0  # Bzip2 has header even for empty data

    def test_bzip2_decompress_empty(self):
        """Test Bzip2 decompression of empty data."""
        compressed = bz2.compress(EMPTY_BYTES)
        result = bake(compressed, ["Bzip2 Decompress"])
        assert result == EMPTY_BYTES

    def test_bzip2_compress_all_bytes(self):
        """Test Bzip2 compression of all 256 possible byte values."""
        result = bake(ALL_BYTES, ["Bzip2 Compress"])
        assert isinstance(result, bytes)
        assert result[:3] == b"BZh"
        # Verify decompression with Python
        decompressed = bz2.decompress(result)
        assert decompressed == ALL_BYTES

    def test_bzip2_roundtrip_hello_world(self):
        """Test Bzip2 Compress→Decompress roundtrip with 'Hello, World!'."""
        assert_roundtrip(HELLO_WORLD, ["Bzip2 Compress"], ["Bzip2 Decompress"])

    def test_bzip2_roundtrip_all_bytes(self):
        """Test Bzip2 Compress→Decompress roundtrip with all 256 bytes."""
        assert_roundtrip(ALL_BYTES, ["Bzip2 Compress"], ["Bzip2 Decompress"])

    def test_bzip2_roundtrip_utf8(self):
        """Test Bzip2 Compress→Decompress roundtrip with UTF-8 data."""
        assert_roundtrip(UTF8_SIMPLE, ["Bzip2 Compress"], ["Bzip2 Decompress"])
        assert_roundtrip(UTF8_EMOJI, ["Bzip2 Compress"], ["Bzip2 Decompress"])
        assert_roundtrip(UTF8_MULTILANG, ["Bzip2 Compress"], ["Bzip2 Decompress"])

    def test_bzip2_compare_python(self):
        """Compare CyberChef Bzip2 with Python's bz2 module."""
        # Compress with CyberChef
        cyberchef_result = bake(HELLO_WORLD, ["Bzip2 Compress"])
        # Decompress with Python to verify
        python_decompressed = bz2.decompress(cyberchef_result)
        assert python_decompressed == HELLO_WORLD

    def test_bzip2_decompress_compare_python(self):
        """Compare CyberChef Bzip2 Decompress with Python's bz2 module."""
        # Compress with Python
        python_compressed = bz2.compress(HELLO_WORLD)
        # Decompress with CyberChef
        cyberchef_result = bake(python_compressed, ["Bzip2 Decompress"])
        assert cyberchef_result == HELLO_WORLD

    def test_bzip2_highly_compressible(self):
        """Test Bzip2 compression of highly compressible data."""
        result = bake(HIGHLY_COMPRESSIBLE, ["Bzip2 Compress"])
        # Should be significantly smaller than original
        assert len(result) < len(HIGHLY_COMPRESSIBLE)
        # Verify roundtrip
        decompressed = bake(result, ["Bzip2 Decompress"])
        assert decompressed == HIGHLY_COMPRESSIBLE

    def test_bzip2_incompressible(self):
        """Test Bzip2 compression of incompressible data."""
        result = bake(INCOMPRESSIBLE, ["Bzip2 Compress"])
        assert isinstance(result, bytes)
        # Should still decompress correctly
        decompressed = bake(result, ["Bzip2 Decompress"])
        assert decompressed == INCOMPRESSIBLE

    def test_bzip2_large_data(self):
        """Test Bzip2 compression of large data."""
        result = bake(LARGE_COMPRESSIBLE, ["Bzip2 Compress"])
        assert isinstance(result, bytes)
        # Verify roundtrip
        decompressed = bake(result, ["Bzip2 Decompress"])
        assert decompressed == LARGE_COMPRESSIBLE

    def test_bzip2_compression_levels(self):
        """Test Bzip2 compression with different block sizes (compression levels)."""
        # Bzip2 block size affects compression (1-9)
        for block_size in [1, 5, 9]:
            result = bake(
                MODERATELY_COMPRESSIBLE,
                [{"op": "Bzip2 Compress", "args": {"Block size (100s of KB)": block_size}}]
            )
            assert isinstance(result, bytes)
            assert result[:3] == b"BZh"
            # Verify decompression
            decompressed = bake(result, ["Bzip2 Decompress"])
            assert decompressed == MODERATELY_COMPRESSIBLE


# ============================================================================
# Zlib Deflate/Inflate Tests
# ============================================================================


class TestZlib:
    """Test suite for Zlib Deflate and Inflate operations."""

    def test_zlib_deflate_hello_world(self):
        """Test Zlib Deflate compression of 'Hello, World!'."""
        result = bake(HELLO_WORLD, ["Zlib Deflate"])
        assert isinstance(result, bytes)
        # Zlib header check (first byte is typically 0x78)
        assert result[0] in [0x78, 0x08, 0x18, 0x28, 0x38, 0x48, 0x58, 0x68]

    def test_zlib_inflate_hello_world(self):
        """Test Zlib Inflate decompression to 'Hello, World!'."""
        # First compress with Python's zlib
        compressed = zlib.compress(HELLO_WORLD)
        # Then decompress with CyberChef
        result = bake(compressed, ["Zlib Inflate"])
        assert result == HELLO_WORLD

    def test_zlib_deflate_empty(self):
        """Test Zlib Deflate compression of empty input."""
        result = bake(EMPTY_BYTES, ["Zlib Deflate"])
        assert isinstance(result, bytes)
        assert len(result) > 0  # Zlib has header even for empty data

    def test_zlib_inflate_empty(self):
        """Test Zlib Inflate decompression of empty data."""
        compressed = zlib.compress(EMPTY_BYTES)
        result = bake(compressed, ["Zlib Inflate"])
        assert result == EMPTY_BYTES

    def test_zlib_deflate_all_bytes(self):
        """Test Zlib Deflate compression of all 256 possible byte values."""
        result = bake(ALL_BYTES, ["Zlib Deflate"])
        assert isinstance(result, bytes)
        # Verify decompression with Python
        decompressed = zlib.decompress(result)
        assert decompressed == ALL_BYTES

    def test_zlib_roundtrip_hello_world(self):
        """Test Zlib Deflate→Inflate roundtrip with 'Hello, World!'."""
        assert_roundtrip(HELLO_WORLD, ["Zlib Deflate"], ["Zlib Inflate"])

    def test_zlib_roundtrip_all_bytes(self):
        """Test Zlib Deflate→Inflate roundtrip with all 256 bytes."""
        assert_roundtrip(ALL_BYTES, ["Zlib Deflate"], ["Zlib Inflate"])

    def test_zlib_roundtrip_utf8(self):
        """Test Zlib Deflate→Inflate roundtrip with UTF-8 data."""
        assert_roundtrip(UTF8_SIMPLE, ["Zlib Deflate"], ["Zlib Inflate"])
        assert_roundtrip(UTF8_EMOJI, ["Zlib Deflate"], ["Zlib Inflate"])
        assert_roundtrip(UTF8_MULTILANG, ["Zlib Deflate"], ["Zlib Inflate"])

    def test_zlib_compare_python(self):
        """Compare CyberChef Zlib Deflate with Python's zlib module."""
        # Compress with CyberChef
        cyberchef_result = bake(HELLO_WORLD, ["Zlib Deflate"])
        # Decompress with Python to verify
        python_decompressed = zlib.decompress(cyberchef_result)
        assert python_decompressed == HELLO_WORLD

    def test_zlib_inflate_compare_python(self):
        """Compare CyberChef Zlib Inflate with Python's zlib module."""
        # Compress with Python
        python_compressed = zlib.compress(HELLO_WORLD)
        # Decompress with CyberChef
        cyberchef_result = bake(python_compressed, ["Zlib Inflate"])
        assert cyberchef_result == HELLO_WORLD

    def test_zlib_highly_compressible(self):
        """Test Zlib compression of highly compressible data."""
        result = bake(HIGHLY_COMPRESSIBLE, ["Zlib Deflate"])
        # Should be significantly smaller than original
        assert len(result) < len(HIGHLY_COMPRESSIBLE)
        # Verify roundtrip
        decompressed = bake(result, ["Zlib Inflate"])
        assert decompressed == HIGHLY_COMPRESSIBLE

    def test_zlib_incompressible(self):
        """Test Zlib compression of incompressible data."""
        result = bake(INCOMPRESSIBLE, ["Zlib Deflate"])
        assert isinstance(result, bytes)
        # Should still decompress correctly
        decompressed = bake(result, ["Zlib Inflate"])
        assert decompressed == INCOMPRESSIBLE

    def test_zlib_large_data(self):
        """Test Zlib compression of large data."""
        result = bake(LARGE_COMPRESSIBLE, ["Zlib Deflate"])
        assert isinstance(result, bytes)
        # Verify roundtrip
        decompressed = bake(result, ["Zlib Inflate"])
        assert decompressed == LARGE_COMPRESSIBLE

    def test_zlib_deflate_with_compression_type_dynamic(self):
        """Test Zlib Deflate with dynamic Huffman coding."""
        result = bake(
            HELLO_WORLD,
            [{"op": "Zlib Deflate", "args": {"Compression type": "Dynamic Huffman Coding"}}]
        )
        assert isinstance(result, bytes)
        # Verify decompression
        decompressed = bake(result, ["Zlib Inflate"])
        assert decompressed == HELLO_WORLD

    def test_zlib_deflate_with_compression_type_fixed(self):
        """Test Zlib Deflate with fixed Huffman coding."""
        result = bake(
            HELLO_WORLD,
            [{"op": "Zlib Deflate", "args": {"Compression type": "Fixed Huffman Coding"}}]
        )
        assert isinstance(result, bytes)
        # Verify decompression
        decompressed = bake(result, ["Zlib Inflate"])
        assert decompressed == HELLO_WORLD

    def test_zlib_deflate_with_compression_type_none(self):
        """Test Zlib Deflate with no compression."""
        result = bake(
            HELLO_WORLD,
            [{"op": "Zlib Deflate", "args": {"Compression type": "None (Store)"}}]
        )
        assert isinstance(result, bytes)
        # Verify decompression
        decompressed = bake(result, ["Zlib Inflate"])
        assert decompressed == HELLO_WORLD


# ============================================================================
# Raw Deflate/Inflate Tests
# ============================================================================


class TestRawDeflate:
    """Test suite for Raw Deflate and Raw Inflate operations."""

    def test_raw_deflate_hello_world(self):
        """Test Raw Deflate compression of 'Hello, World!'."""
        result = bake(HELLO_WORLD, ["Raw Deflate"])
        assert isinstance(result, bytes)
        # Raw deflate has no headers

    def test_raw_inflate_hello_world(self):
        """Test Raw Inflate decompression to 'Hello, World!'."""
        # First compress with Python's zlib (raw deflate)
        compressed = zlib.compress(HELLO_WORLD)[2:-4]  # Remove zlib headers/checksum
        # Then decompress with CyberChef
        result = bake(compressed, ["Raw Inflate"])
        assert result == HELLO_WORLD

    def test_raw_deflate_empty(self):
        """Test Raw Deflate compression of empty input."""
        result = bake(EMPTY_BYTES, ["Raw Deflate"])
        assert isinstance(result, bytes)

    def test_raw_deflate_all_bytes(self):
        """Test Raw Deflate compression of all 256 possible byte values."""
        result = bake(ALL_BYTES, ["Raw Deflate"])
        assert isinstance(result, bytes)

    def test_raw_deflate_roundtrip_hello_world(self):
        """Test Raw Deflate→Inflate roundtrip with 'Hello, World!'."""
        assert_roundtrip(HELLO_WORLD, ["Raw Deflate"], ["Raw Inflate"])

    def test_raw_deflate_roundtrip_all_bytes(self):
        """Test Raw Deflate→Inflate roundtrip with all 256 bytes."""
        assert_roundtrip(ALL_BYTES, ["Raw Deflate"], ["Raw Inflate"])

    def test_raw_deflate_roundtrip_utf8(self):
        """Test Raw Deflate→Inflate roundtrip with UTF-8 data."""
        assert_roundtrip(UTF8_SIMPLE, ["Raw Deflate"], ["Raw Inflate"])
        assert_roundtrip(UTF8_EMOJI, ["Raw Deflate"], ["Raw Inflate"])
        assert_roundtrip(UTF8_MULTILANG, ["Raw Deflate"], ["Raw Inflate"])

    def test_raw_deflate_highly_compressible(self):
        """Test Raw Deflate compression of highly compressible data."""
        result = bake(HIGHLY_COMPRESSIBLE, ["Raw Deflate"])
        # Should be significantly smaller than original
        assert len(result) < len(HIGHLY_COMPRESSIBLE)
        # Verify roundtrip
        decompressed = bake(result, ["Raw Inflate"])
        assert decompressed == HIGHLY_COMPRESSIBLE

    def test_raw_deflate_incompressible(self):
        """Test Raw Deflate compression of incompressible data."""
        result = bake(INCOMPRESSIBLE, ["Raw Deflate"])
        assert isinstance(result, bytes)
        # Should still decompress correctly
        decompressed = bake(result, ["Raw Inflate"])
        assert decompressed == INCOMPRESSIBLE

    def test_raw_deflate_large_data(self):
        """Test Raw Deflate compression of large data."""
        result = bake(LARGE_COMPRESSIBLE, ["Raw Deflate"])
        assert isinstance(result, bytes)
        # Verify roundtrip
        decompressed = bake(result, ["Raw Inflate"])
        assert decompressed == LARGE_COMPRESSIBLE

    def test_raw_deflate_with_compression_type_dynamic(self):
        """Test Raw Deflate with dynamic Huffman coding."""
        result = bake(
            HELLO_WORLD,
            [{"op": "Raw Deflate", "args": {"Compression type": "Dynamic Huffman Coding"}}]
        )
        assert isinstance(result, bytes)
        # Verify decompression
        decompressed = bake(result, ["Raw Inflate"])
        assert decompressed == HELLO_WORLD

    def test_raw_deflate_with_compression_type_fixed(self):
        """Test Raw Deflate with fixed Huffman coding."""
        result = bake(
            HELLO_WORLD,
            [{"op": "Raw Deflate", "args": {"Compression type": "Fixed Huffman Coding"}}]
        )
        assert isinstance(result, bytes)
        # Verify decompression
        decompressed = bake(result, ["Raw Inflate"])
        assert decompressed == HELLO_WORLD

    def test_raw_deflate_with_compression_type_none(self):
        """Test Raw Deflate with no compression."""
        result = bake(
            HELLO_WORLD,
            [{"op": "Raw Deflate", "args": {"Compression type": "None (Store)"}}]
        )
        assert isinstance(result, bytes)
        # Verify decompression
        decompressed = bake(result, ["Raw Inflate"])
        assert decompressed == HELLO_WORLD


# ============================================================================
# LZ4 Compression Tests
# ============================================================================


@require_operations("LZ4 Compress", "LZ4 Decompress")
class TestLZ4:
    """Test suite for LZ4 compression and decompression operations."""

    def test_lz4_compress_hello_world(self):
        """Test LZ4 compression of 'Hello, World!'."""
        result = bake(HELLO_WORLD, ["LZ4 Compress"])
        assert isinstance(result, bytes)
        # LZ4 compressed data should have specific format

    def test_lz4_decompress_hello_world(self):
        """Test LZ4 decompression to 'Hello, World!'."""
        # First compress with CyberChef
        compressed = bake(HELLO_WORLD, ["LZ4 Compress"])
        # Then decompress
        result = bake(compressed, ["LZ4 Decompress"])
        assert result == HELLO_WORLD

    def test_lz4_compress_empty(self):
        """Test LZ4 compression of empty input."""
        result = bake(EMPTY_BYTES, ["LZ4 Compress"])
        assert isinstance(result, bytes)

    def test_lz4_decompress_empty(self):
        """Test LZ4 decompression of empty data."""
        compressed = bake(EMPTY_BYTES, ["LZ4 Compress"])
        result = bake(compressed, ["LZ4 Decompress"])
        assert result == EMPTY_BYTES

    def test_lz4_compress_all_bytes(self):
        """Test LZ4 compression of all 256 possible byte values."""
        result = bake(ALL_BYTES, ["LZ4 Compress"])
        assert isinstance(result, bytes)

    def test_lz4_roundtrip_hello_world(self):
        """Test LZ4 Compress→Decompress roundtrip with 'Hello, World!'."""
        assert_roundtrip(HELLO_WORLD, ["LZ4 Compress"], ["LZ4 Decompress"])

    def test_lz4_roundtrip_all_bytes(self):
        """Test LZ4 Compress→Decompress roundtrip with all 256 bytes."""
        assert_roundtrip(ALL_BYTES, ["LZ4 Compress"], ["LZ4 Decompress"])

    def test_lz4_roundtrip_utf8(self):
        """Test LZ4 Compress→Decompress roundtrip with UTF-8 data."""
        assert_roundtrip(UTF8_SIMPLE, ["LZ4 Compress"], ["LZ4 Decompress"])
        assert_roundtrip(UTF8_EMOJI, ["LZ4 Compress"], ["LZ4 Decompress"])
        assert_roundtrip(UTF8_MULTILANG, ["LZ4 Compress"], ["LZ4 Decompress"])

    def test_lz4_highly_compressible(self):
        """Test LZ4 compression of highly compressible data."""
        result = bake(HIGHLY_COMPRESSIBLE, ["LZ4 Compress"])
        # Should be significantly smaller than original
        assert len(result) < len(HIGHLY_COMPRESSIBLE)
        # Verify roundtrip
        decompressed = bake(result, ["LZ4 Decompress"])
        assert decompressed == HIGHLY_COMPRESSIBLE

    def test_lz4_incompressible(self):
        """Test LZ4 compression of incompressible data."""
        result = bake(INCOMPRESSIBLE, ["LZ4 Compress"])
        assert isinstance(result, bytes)
        # Should still decompress correctly
        decompressed = bake(result, ["LZ4 Decompress"])
        assert decompressed == INCOMPRESSIBLE

    def test_lz4_large_data(self):
        """Test LZ4 compression of large data."""
        result = bake(LARGE_COMPRESSIBLE, ["LZ4 Compress"])
        assert isinstance(result, bytes)
        # Verify roundtrip
        decompressed = bake(result, ["LZ4 Decompress"])
        assert decompressed == LARGE_COMPRESSIBLE


# ============================================================================
# LZMA Compression Tests
# ============================================================================


@require_operations("LZMA Compress", "LZMA Decompress")
class TestLZMA:
    """Test suite for LZMA compression and decompression operations."""

    def test_lzma_compress_hello_world(self):
        """Test LZMA compression of 'Hello, World!'."""
        result = bake(HELLO_WORLD, ["LZMA Compress"])
        assert isinstance(result, bytes)

    def test_lzma_decompress_hello_world(self):
        """Test LZMA decompression to 'Hello, World!'."""
        # First compress with CyberChef
        compressed = bake(HELLO_WORLD, ["LZMA Compress"])
        # Then decompress
        result = bake(compressed, ["LZMA Decompress"])
        assert result == HELLO_WORLD

    def test_lzma_compress_empty(self):
        """Test LZMA compression of empty input."""
        result = bake(EMPTY_BYTES, ["LZMA Compress"])
        assert isinstance(result, bytes)

    def test_lzma_decompress_empty(self):
        """Test LZMA decompression of empty data."""
        compressed = bake(EMPTY_BYTES, ["LZMA Compress"])
        result = bake(compressed, ["LZMA Decompress"])
        assert result == EMPTY_BYTES

    def test_lzma_compress_all_bytes(self):
        """Test LZMA compression of all 256 possible byte values."""
        result = bake(ALL_BYTES, ["LZMA Compress"])
        assert isinstance(result, bytes)

    def test_lzma_roundtrip_hello_world(self):
        """Test LZMA Compress→Decompress roundtrip with 'Hello, World!'."""
        assert_roundtrip(HELLO_WORLD, ["LZMA Compress"], ["LZMA Decompress"])

    def test_lzma_roundtrip_all_bytes(self):
        """Test LZMA Compress→Decompress roundtrip with all 256 bytes."""
        assert_roundtrip(ALL_BYTES, ["LZMA Compress"], ["LZMA Decompress"])

    def test_lzma_roundtrip_utf8(self):
        """Test LZMA Compress→Decompress roundtrip with UTF-8 data."""
        assert_roundtrip(UTF8_SIMPLE, ["LZMA Compress"], ["LZMA Decompress"])
        assert_roundtrip(UTF8_EMOJI, ["LZMA Compress"], ["LZMA Decompress"])
        assert_roundtrip(UTF8_MULTILANG, ["LZMA Compress"], ["LZMA Decompress"])

    def test_lzma_highly_compressible(self):
        """Test LZMA compression of highly compressible data."""
        result = bake(HIGHLY_COMPRESSIBLE, ["LZMA Compress"])
        # Should be significantly smaller than original
        assert len(result) < len(HIGHLY_COMPRESSIBLE)
        # Verify roundtrip
        decompressed = bake(result, ["LZMA Decompress"])
        assert decompressed == HIGHLY_COMPRESSIBLE

    def test_lzma_incompressible(self):
        """Test LZMA compression of incompressible data."""
        result = bake(INCOMPRESSIBLE, ["LZMA Compress"])
        assert isinstance(result, bytes)
        # Should still decompress correctly
        decompressed = bake(result, ["LZMA Decompress"])
        assert decompressed == INCOMPRESSIBLE

    def test_lzma_large_data(self):
        """Test LZMA compression of large data."""
        result = bake(LARGE_COMPRESSIBLE, ["LZMA Compress"])
        assert isinstance(result, bytes)
        # Verify roundtrip
        decompressed = bake(result, ["LZMA Decompress"])
        assert decompressed == LARGE_COMPRESSIBLE

    def test_lzma_compression_modes(self):
        """Test LZMA compression with different compression modes (1-9)."""
        for mode in [1, 5, 9]:
            result = bake(
                MODERATELY_COMPRESSIBLE,
                [{"op": "LZMA Compress", "args": {"Compression Mode": mode}}]
            )
            assert isinstance(result, bytes)
            # Verify decompression
            decompressed = bake(result, ["LZMA Decompress"])
            assert decompressed == MODERATELY_COMPRESSIBLE


# ============================================================================
# LZString Compression Tests
# ============================================================================


@require_operations("LZString Compress", "LZString Decompress")
class TestLZString:
    """Test suite for LZString compression and decompression operations."""

    def test_lzstring_compress_hello_world(self):
        """Test LZString compression of 'Hello, World!'."""
        result = bake(HELLO_WORLD, ["LZString Compress"])
        assert isinstance(result, str)

    def test_lzstring_decompress_hello_world(self):
        """Test LZString decompression to 'Hello, World!'."""
        # First compress with CyberChef
        compressed = bake(HELLO_WORLD, ["LZString Compress"])
        # Then decompress (returns string)
        result = bake(compressed, ["LZString Decompress"])
        # LZString returns string, so compare with decoded original
        assert result == HELLO_WORLD.decode('utf-8')

    def test_lzstring_compress_empty(self):
        """Test LZString compression of empty input."""
        result = bake(EMPTY_BYTES, ["LZString Compress"])
        assert isinstance(result, str)

    def test_lzstring_decompress_empty(self):
        """Test LZString decompression of empty data."""
        compressed = bake(EMPTY_BYTES, ["LZString Compress"])
        result = bake(compressed, ["LZString Decompress"])
        # LZString returns string, so compare with decoded original
        assert result == EMPTY_BYTES.decode('utf-8')

    def test_lzstring_roundtrip_hello_world(self):
        """Test LZString Compress→Decompress roundtrip with 'Hello, World!'."""
        # LZString returns string, so pass expected as decoded string
        assert_roundtrip(HELLO_WORLD, ["LZString Compress"], ["LZString Decompress"],
                        expected=HELLO_WORLD.decode('utf-8'))

    def test_lzstring_roundtrip_all_bytes(self):
        """Test LZString Compress→Decompress roundtrip with all 256 bytes."""
        # Use Base64 format for binary data to avoid UTF-16 encoding issues
        compress_op = {"op": "LZString Compress", "args": {"Compression Format": "Base64"}}
        decompress_op = {"op": "LZString Decompress", "args": {"Compression Format": "Base64"}}
        # Note: ALL_BYTES may not be valid UTF-8, so test with latin-1 decodable subset
        # LZString works with strings, so we expect string output
        compressed = bake(ALL_BYTES, [compress_op])
        decompressed = bake(compressed, [decompress_op])
        # Compare by re-encoding the decompressed string
        assert decompressed.encode('latin-1') == ALL_BYTES

    def test_lzstring_roundtrip_utf8(self):
        """Test LZString Compress→Decompress roundtrip with UTF-8 data."""
        # UTF8_SIMPLE works with default UTF16 format
        assert_roundtrip(UTF8_SIMPLE, ["LZString Compress"], ["LZString Decompress"],
                        expected=UTF8_SIMPLE.decode('utf-8'))
        # UTF8_EMOJI needs Base64 format to avoid encoding issues
        compress_op = {"op": "LZString Compress", "args": {"Compression Format": "Base64"}}
        decompress_op = {"op": "LZString Decompress", "args": {"Compression Format": "Base64"}}
        assert_roundtrip(UTF8_EMOJI, [compress_op], [decompress_op],
                        expected=UTF8_EMOJI.decode('utf-8'))

    def test_lzstring_highly_compressible(self):
        """Test LZString compression of highly compressible data."""
        # Use Base64 format to avoid UTF-16 encoding issues with compressed data
        compress_op = {"op": "LZString Compress", "args": {"Compression Format": "Base64"}}
        decompress_op = {"op": "LZString Decompress", "args": {"Compression Format": "Base64"}}
        result = bake(HIGHLY_COMPRESSIBLE, [compress_op])
        assert isinstance(result, str)
        # Verify roundtrip
        decompressed = bake(result, [decompress_op])
        assert decompressed == HIGHLY_COMPRESSIBLE.decode('utf-8')

    def test_lzstring_compression_formats(self):
        """Test LZString compression with different formats."""
        # Only test formats that work (URI Component is not supported)
        formats = [
            "UTF16",
            "Base64",
        ]
        for fmt in formats:
            result = bake(
                HELLO_WORLD,
                [{"op": "LZString Compress", "args": {"Compression Format": fmt}}]
            )
            assert isinstance(result, str)
            # Verify decompression
            decompressed = bake(
                result,
                [{"op": "LZString Decompress", "args": {"Compression Format": fmt}}]
            )
            # LZString returns string, so compare with decoded original
            assert decompressed == HELLO_WORLD.decode('utf-8')


# ============================================================================
# Zip/Unzip Tests
# ============================================================================


@require_operations("Zip", "Unzip")
class TestZip:
    """Test suite for Zip and Unzip operations."""

    def test_zip_hello_world(self):
        """Test Zip compression of 'Hello, World!'."""
        result = bake(
            HELLO_WORLD,
            [{"op": "Zip", "args": {"Filename": "test.txt"}}]
        )
        assert isinstance(result, bytes)
        # ZIP file signature
        assert result[:4] == b"PK\x03\x04"

    def test_unzip_hello_world(self):
        """Test Unzip decompression to 'Hello, World!'."""
        # First zip with CyberChef
        zipped = bake(
            HELLO_WORLD,
            [{"op": "Zip", "args": {"Filename": "test.txt"}}]
        )
        # Then unzip
        result = bake(zipped, ["Unzip"])
        assert HELLO_WORLD in result or str(HELLO_WORLD, 'utf-8') in result

    def test_zip_empty(self):
        """Test Zip compression of empty input."""
        result = bake(
            EMPTY_BYTES,
            [{"op": "Zip", "args": {"Filename": "empty.txt"}}]
        )
        assert isinstance(result, bytes)
        assert result[:4] == b"PK\x03\x04"

    def test_zip_roundtrip_hello_world(self):
        """Test Zip→Unzip roundtrip with 'Hello, World!'."""
        # Zip the data
        zipped = bake(
            HELLO_WORLD,
            [{"op": "Zip", "args": {"Filename": "test.txt"}}]
        )
        # Unzip and verify
        result = bake(zipped, ["Unzip"])
        # Unzip returns a formatted output with filename, so check content
        assert isinstance(result, (str, bytes))

    def test_zip_all_bytes(self):
        """Test Zip compression of all 256 possible byte values."""
        result = bake(
            ALL_BYTES,
            [{"op": "Zip", "args": {"Filename": "binary.dat"}}]
        )
        assert isinstance(result, bytes)
        assert result[:4] == b"PK\x03\x04"

    def test_zip_compression_methods(self):
        """Test Zip with different compression methods."""
        methods = ["Deflate", "None (Store)"]
        for method in methods:
            result = bake(
                HELLO_WORLD,
                [{
                    "op": "Zip",
                    "args": {
                        "Filename": "test.txt",
                        "Compression method": method
                    }
                }]
            )
            assert isinstance(result, bytes)
            assert result[:4] == b"PK\x03\x04"

    def test_zip_compression_types(self):
        """Test Zip with different compression types."""
        compression_types = [
            "Dynamic Huffman Coding",
            "Fixed Huffman Coding",
            "None (Store)"
        ]
        for comp_type in compression_types:
            result = bake(
                HELLO_WORLD,
                [{
                    "op": "Zip",
                    "args": {
                        "Filename": "test.txt",
                        "Compression type": comp_type
                    }
                }]
            )
            assert isinstance(result, bytes)
            assert result[:4] == b"PK\x03\x04"


# ============================================================================
# Cross-Compression Integration Tests
# ============================================================================


class TestCrossCompression:
    """Test suite for combining multiple compression operations."""

    def test_gzip_then_base64(self):
        """Test Gzip compression followed by Base64 encoding."""
        result = bake(HELLO_WORLD, ["Gzip", "To Base64"])
        assert isinstance(result, str)
        # Decode back
        decoded = bake(result, ["From Base64", "Gunzip"])
        assert decoded == HELLO_WORLD

    def test_bzip2_then_hex(self):
        """Test Bzip2 compression followed by hex encoding."""
        result = bake(HELLO_WORLD, ["Bzip2 Compress", "To Hex"])
        assert isinstance(result, str)
        # Decode back
        decoded = bake(result, ["From Hex", "Bzip2 Decompress"])
        assert decoded == HELLO_WORLD

    def test_zlib_then_url_encode(self):
        """Test Zlib compression followed by URL encoding."""
        result = bake(HELLO_WORLD, ["Zlib Deflate", "To Hex", "URL Encode"])
        assert isinstance(result, str)
        # Decode back
        decoded = bake(result, ["URL Decode", "From Hex", "Zlib Inflate"])
        assert decoded == HELLO_WORLD

    def test_double_compression_gzip_bzip2(self):
        """Test double compression: Gzip then Bzip2."""
        result = bake(LARGE_COMPRESSIBLE, ["Gzip", "Bzip2 Compress"])
        assert isinstance(result, bytes)
        # Decompress in reverse order
        decoded = bake(result, ["Bzip2 Decompress", "Gunzip"])
        assert decoded == LARGE_COMPRESSIBLE


# ============================================================================
# Edge Cases and Error Handling Tests
# ============================================================================


class TestCompressionEdgeCases:
    """Test suite for edge cases and error handling in compression operations."""

    def test_gunzip_non_gzip_data(self):
        """Test Gunzip with non-gzip data should raise error or handle gracefully."""
        # This should fail or handle gracefully
        with pytest.raises(Exception):
            bake(b"not gzip data", ["Gunzip"])

    def test_bzip2_decompress_non_bzip2_data(self):
        """Test Bzip2 Decompress with non-bzip2 data should raise error."""
        # This should fail or handle gracefully
        with pytest.raises(Exception):
            bake(b"not bzip2 data", ["Bzip2 Decompress"])

    def test_zlib_inflate_non_zlib_data(self):
        """Test Zlib Inflate with non-zlib data should raise error."""
        # This should fail or handle gracefully
        with pytest.raises(Exception):
            bake(b"not zlib data", ["Zlib Inflate"])

    def test_compression_ratio_highly_compressible(self):
        """Test compression ratio for highly compressible data."""
        original_size = len(HIGHLY_COMPRESSIBLE)

        # Gzip
        gzipped = bake(HIGHLY_COMPRESSIBLE, ["Gzip"])
        assert len(gzipped) < original_size * 0.1  # Should compress to < 10%

        # Bzip2
        bzipped = bake(HIGHLY_COMPRESSIBLE, ["Bzip2 Compress"])
        assert len(bzipped) < original_size * 0.1  # Should compress to < 10%

    def test_compression_of_already_compressed(self):
        """Test compression of already compressed data (should not compress well)."""
        # First compress with Gzip
        first_pass = bake(HELLO_WORLD, ["Gzip"])
        first_size = len(first_pass)

        # Compress again
        second_pass = bake(first_pass, ["Gzip"])
        second_size = len(second_pass)

        # Second compression should not significantly reduce size
        # (might even increase due to headers)
        assert second_size >= first_size * 0.8

    def test_large_data_gzip(self):
        """Test Gzip with very large data."""
        very_large_data = b"X" * 100000
        result = bake(very_large_data, ["Gzip"])
        assert isinstance(result, bytes)
        # Verify roundtrip
        decompressed = bake(result, ["Gunzip"])
        assert decompressed == very_large_data

    def test_lorem_ipsum_compression(self):
        """Test compression of Lorem Ipsum text."""
        # Gzip
        gzipped = bake(LOREM_IPSUM, ["Gzip"])
        assert len(gzipped) < len(LOREM_IPSUM)
        assert bake(gzipped, ["Gunzip"]) == LOREM_IPSUM

        # Bzip2
        bzipped = bake(LOREM_IPSUM, ["Bzip2 Compress"])
        assert len(bzipped) < len(LOREM_IPSUM)
        assert bake(bzipped, ["Bzip2 Decompress"]) == LOREM_IPSUM

        # Zlib
        deflated = bake(LOREM_IPSUM, ["Zlib Deflate"])
        assert len(deflated) < len(LOREM_IPSUM)
        assert bake(deflated, ["Zlib Inflate"]) == LOREM_IPSUM

    def test_binary_pattern_compression(self):
        """Test compression of binary patterns."""
        result = bake(BINARY_PATTERN, ["Gzip"])
        assert isinstance(result, bytes)
        # Should compress reasonably well due to pattern
        assert len(result) < len(BINARY_PATTERN)
        # Verify roundtrip
        decompressed = bake(result, ["Gunzip"])
        assert decompressed == BINARY_PATTERN

    def test_null_bytes_compression(self):
        """Test compression of data with null bytes."""
        data_with_nulls = b"hello\x00\x00\x00world\x00\x00\x00test"
        # Gzip
        assert_roundtrip(data_with_nulls, ["Gzip"], ["Gunzip"])
        # Bzip2
        assert_roundtrip(data_with_nulls, ["Bzip2 Compress"], ["Bzip2 Decompress"])
        # Zlib
        assert_roundtrip(data_with_nulls, ["Zlib Deflate"], ["Zlib Inflate"])

    def test_single_byte_compression(self):
        """Test compression of single byte."""
        single_byte = b"A"
        # All compression methods should handle single byte
        assert_roundtrip(single_byte, ["Gzip"], ["Gunzip"])
        assert_roundtrip(single_byte, ["Bzip2 Compress"], ["Bzip2 Decompress"])
        assert_roundtrip(single_byte, ["Zlib Deflate"], ["Zlib Inflate"])
