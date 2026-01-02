"""Comprehensive tests for compression operations.

These operations use Python's stdlib (zlib, gzip, bz2) as fallbacks because
QuickJS has stricter typed array bounds checking that causes CyberChef's
embedded zlib.js to fail.
"""

import gzip
import zlib
import bz2
import pytest

from ida_cyberchef.cyberchef import bake


# =============================================================================
# ZLIB DEFLATE / INFLATE
# =============================================================================

class TestZlibDeflate:
    """Test Zlib Deflate compression."""

    def test_basic_compression(self):
        """Test basic zlib compression."""
        result = bake(b"hello world", ["Zlib Deflate"])
        assert isinstance(result, bytes)
        assert len(result) > 0
        # Zlib header starts with 0x78
        assert result[0] == 0x78

    def test_empty_input(self):
        """Test compression of empty data."""
        result = bake(b"", ["Zlib Deflate"])
        assert isinstance(result, bytes)
        # Empty zlib compressed data is still valid
        assert result[0] == 0x78

    def test_short_input(self):
        """Test compression of very short data."""
        result = bake(b"a", ["Zlib Deflate"])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_repetitive_data_compression_ratio(self):
        """Test that repetitive data compresses well."""
        original = b"AAAAAAAAAA" * 100  # 1000 bytes of A's
        result = bake(original, ["Zlib Deflate"])
        # Should compress to much smaller size
        assert len(result) < len(original) / 5

    def test_binary_data(self):
        """Test compression of binary data."""
        original = bytes(range(256)) * 4
        result = bake(original, ["Zlib Deflate"])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_compression_type_dynamic(self):
        """Test with Dynamic Huffman Coding (default)."""
        result = bake(b"test data", [{"op": "Zlib Deflate", "args": {"Compression type": "Dynamic Huffman Coding"}}])
        assert isinstance(result, bytes)

    def test_compression_type_fixed(self):
        """Test with Fixed Huffman Coding."""
        result = bake(b"test data", [{"op": "Zlib Deflate", "args": {"Compression type": "Fixed Huffman Coding"}}])
        assert isinstance(result, bytes)

    def test_compression_type_store(self):
        """Test with None (Store) - no compression."""
        original = b"test data"
        result = bake(original, [{"op": "Zlib Deflate", "args": {"Compression type": "None (Store)"}}])
        assert isinstance(result, bytes)
        # Store mode should be larger or equal (header overhead)
        assert len(result) >= len(original)

    def test_large_data(self):
        """Test compression of larger data."""
        original = b"The quick brown fox jumps over the lazy dog. " * 1000
        result = bake(original, ["Zlib Deflate"])
        assert isinstance(result, bytes)
        assert len(result) < len(original)

    def test_string_input(self):
        """Test that string input is handled correctly."""
        result = bake("hello world", ["Zlib Deflate"])
        assert isinstance(result, bytes)


class TestZlibInflate:
    """Test Zlib Inflate decompression."""

    def test_basic_decompression(self):
        """Test basic zlib decompression."""
        compressed = zlib.compress(b"hello world")
        result = bake(compressed, ["Zlib Inflate"])
        assert result == b"hello world"

    def test_empty_decompression(self):
        """Test decompression of empty compressed data."""
        compressed = zlib.compress(b"")
        result = bake(compressed, ["Zlib Inflate"])
        assert result == b""

    def test_large_decompression(self):
        """Test decompression of larger data."""
        original = b"test data " * 10000
        compressed = zlib.compress(original)
        result = bake(compressed, ["Zlib Inflate"])
        assert result == original

    def test_start_index(self):
        """Test decompression with start index."""
        # Prepend some garbage bytes
        garbage = b"GARBAGE"
        compressed = zlib.compress(b"hello")
        data = garbage + compressed
        result = bake(data, [{"op": "Zlib Inflate", "args": {"Start index": len(garbage)}}])
        assert result == b"hello"


class TestZlibRoundtrip:
    """Test Zlib compression/decompression roundtrip."""

    def test_simple_roundtrip(self):
        """Test simple compress/decompress cycle."""
        original = b"hello world"
        result = bake(original, ["Zlib Deflate", "Zlib Inflate"])
        assert result == original

    def test_binary_roundtrip(self):
        """Test binary data roundtrip."""
        original = bytes(range(256))
        result = bake(original, ["Zlib Deflate", "Zlib Inflate"])
        assert result == original

    def test_large_roundtrip(self):
        """Test large data roundtrip."""
        original = b"Lorem ipsum dolor sit amet. " * 5000
        result = bake(original, ["Zlib Deflate", "Zlib Inflate"])
        assert result == original

    def test_empty_roundtrip(self):
        """Test empty data roundtrip."""
        result = bake(b"", ["Zlib Deflate", "Zlib Inflate"])
        assert result == b""

    def test_unicode_roundtrip(self):
        """Test UTF-8 encoded unicode roundtrip."""
        original = "Hello 世界 🌍".encode("utf-8")
        result = bake(original, ["Zlib Deflate", "Zlib Inflate"])
        assert result == original


# =============================================================================
# RAW DEFLATE / INFLATE
# =============================================================================

class TestRawDeflate:
    """Test Raw Deflate compression (no zlib header)."""

    def test_basic_compression(self):
        """Test basic raw deflate compression."""
        result = bake(b"hello world", ["Raw Deflate"])
        assert isinstance(result, bytes)
        assert len(result) > 0
        # Raw deflate does NOT start with 0x78 (no zlib header)
        assert result[0] != 0x78 or len(result) < 3

    def test_empty_input(self):
        """Test compression of empty data."""
        result = bake(b"", ["Raw Deflate"])
        assert isinstance(result, bytes)

    def test_compression_types(self):
        """Test different compression types."""
        data = b"test data for compression"

        dynamic = bake(data, [{"op": "Raw Deflate", "args": {"Compression type": "Dynamic Huffman Coding"}}])
        fixed = bake(data, [{"op": "Raw Deflate", "args": {"Compression type": "Fixed Huffman Coding"}}])
        store = bake(data, [{"op": "Raw Deflate", "args": {"Compression type": "None (Store)"}}])

        assert isinstance(dynamic, bytes)
        assert isinstance(fixed, bytes)
        assert isinstance(store, bytes)


class TestRawInflate:
    """Test Raw Inflate decompression."""

    def test_basic_decompression(self):
        """Test basic raw inflate decompression."""
        # Create raw deflate data using Python
        compressor = zlib.compressobj(level=6, wbits=-15)
        compressed = compressor.compress(b"hello world") + compressor.flush()

        result = bake(compressed, ["Raw Inflate"])
        assert result == b"hello world"

    def test_start_index(self):
        """Test decompression with start index."""
        compressor = zlib.compressobj(level=6, wbits=-15)
        compressed = compressor.compress(b"hello") + compressor.flush()

        garbage = b"XX"
        data = garbage + compressed
        result = bake(data, [{"op": "Raw Inflate", "args": {"Start index": 2}}])
        assert result == b"hello"


class TestRawDeflateRoundtrip:
    """Test Raw Deflate roundtrip."""

    def test_simple_roundtrip(self):
        """Test simple compress/decompress cycle."""
        original = b"hello world"
        result = bake(original, ["Raw Deflate", "Raw Inflate"])
        assert result == original

    def test_binary_roundtrip(self):
        """Test binary data roundtrip."""
        original = bytes(range(256))
        result = bake(original, ["Raw Deflate", "Raw Inflate"])
        assert result == original

    def test_large_roundtrip(self):
        """Test large data roundtrip."""
        original = b"Test pattern. " * 10000
        result = bake(original, ["Raw Deflate", "Raw Inflate"])
        assert result == original


# =============================================================================
# GZIP / GUNZIP
# =============================================================================

class TestGzip:
    """Test Gzip compression."""

    def test_basic_compression(self):
        """Test basic gzip compression."""
        result = bake(b"hello world", ["Gzip"])
        assert isinstance(result, bytes)
        # Gzip magic number
        assert result[:2] == b"\x1f\x8b"

    def test_empty_input(self):
        """Test compression of empty data."""
        result = bake(b"", ["Gzip"])
        assert isinstance(result, bytes)
        assert result[:2] == b"\x1f\x8b"

    def test_compression_ratio(self):
        """Test that repetitive data compresses."""
        original = b"AAAAAAAAAA" * 100
        result = bake(original, ["Gzip"])
        assert len(result) < len(original) / 5

    def test_compression_types(self):
        """Test different compression types."""
        data = b"test data for gzip"

        dynamic = bake(data, [{"op": "Gzip", "args": {"Compression type": "Dynamic Huffman Coding"}}])
        fixed = bake(data, [{"op": "Gzip", "args": {"Compression type": "Fixed Huffman Coding"}}])

        assert dynamic[:2] == b"\x1f\x8b"
        assert fixed[:2] == b"\x1f\x8b"

    def test_stdlib_compatibility(self):
        """Test that output is compatible with Python's gzip."""
        original = b"hello world"
        compressed = bake(original, ["Gzip"])

        # Should be decompressible by Python's gzip
        decompressed = gzip.decompress(compressed)
        assert decompressed == original


class TestGunzip:
    """Test Gunzip decompression."""

    def test_basic_decompression(self):
        """Test basic gunzip decompression."""
        compressed = gzip.compress(b"hello world")
        result = bake(compressed, ["Gunzip"])
        assert result == b"hello world"

    def test_empty_decompression(self):
        """Test decompression of empty gzipped data."""
        compressed = gzip.compress(b"")
        result = bake(compressed, ["Gunzip"])
        assert result == b""

    def test_large_decompression(self):
        """Test decompression of larger data."""
        original = b"decompression test " * 10000
        compressed = gzip.compress(original)
        result = bake(compressed, ["Gunzip"])
        assert result == original

    def test_multi_member(self):
        """Test decompression of data compressed externally."""
        # Create gzip data that might come from external tools
        original = b"data from external source"
        compressed = gzip.compress(original)
        result = bake(compressed, ["Gunzip"])
        assert result == original


class TestGzipRoundtrip:
    """Test Gzip roundtrip."""

    def test_simple_roundtrip(self):
        """Test simple compress/decompress cycle."""
        original = b"hello world"
        result = bake(original, ["Gzip", "Gunzip"])
        assert result == original

    def test_binary_roundtrip(self):
        """Test binary data roundtrip."""
        original = bytes(range(256))
        result = bake(original, ["Gzip", "Gunzip"])
        assert result == original

    def test_large_roundtrip(self):
        """Test large data roundtrip."""
        original = b"Gzip test pattern! " * 10000
        result = bake(original, ["Gzip", "Gunzip"])
        assert result == original

    def test_unicode_roundtrip(self):
        """Test UTF-8 unicode roundtrip."""
        original = "Привет мир! 你好世界!".encode("utf-8")
        result = bake(original, ["Gzip", "Gunzip"])
        assert result == original


# =============================================================================
# BZIP2 COMPRESS / DECOMPRESS
# =============================================================================

class TestBzip2Compress:
    """Test Bzip2 compression."""

    def test_basic_compression(self):
        """Test basic bzip2 compression."""
        result = bake(b"hello world", ["Bzip2 Compress"])
        assert isinstance(result, bytes)
        # Bzip2 magic number
        assert result[:2] == b"BZ"

    def test_empty_input(self):
        """Test compression of empty data."""
        result = bake(b"", ["Bzip2 Compress"])
        assert isinstance(result, bytes)

    def test_compression_ratio(self):
        """Test compression of repetitive data."""
        original = b"BZIP2TEST" * 100
        result = bake(original, ["Bzip2 Compress"])
        assert len(result) < len(original) / 3

    def test_block_size(self):
        """Test different block sizes."""
        data = b"test data " * 100

        small_block = bake(data, [{"op": "Bzip2 Compress", "args": {"Block size (100s of kb)": 1}}])
        large_block = bake(data, [{"op": "Bzip2 Compress", "args": {"Block size (100s of kb)": 9}}])

        assert small_block[:2] == b"BZ"
        assert large_block[:2] == b"BZ"

    def test_stdlib_compatibility(self):
        """Test that output is compatible with Python's bz2."""
        original = b"hello world"
        compressed = bake(original, ["Bzip2 Compress"])

        # Should be decompressible by Python's bz2
        decompressed = bz2.decompress(compressed)
        assert decompressed == original


class TestBzip2Decompress:
    """Test Bzip2 decompression."""

    def test_basic_decompression(self):
        """Test basic bzip2 decompression."""
        compressed = bz2.compress(b"hello world")
        result = bake(compressed, ["Bzip2 Decompress"])
        assert result == b"hello world"

    def test_empty_decompression(self):
        """Test decompression of empty bzip2 data."""
        compressed = bz2.compress(b"")
        result = bake(compressed, ["Bzip2 Decompress"])
        assert result == b""

    def test_large_decompression(self):
        """Test decompression of larger data."""
        original = b"bzip2 decompression test " * 5000
        compressed = bz2.compress(original)
        result = bake(compressed, ["Bzip2 Decompress"])
        assert result == original


class TestBzip2Roundtrip:
    """Test Bzip2 roundtrip."""

    def test_simple_roundtrip(self):
        """Test simple compress/decompress cycle."""
        original = b"hello world"
        result = bake(original, ["Bzip2 Compress", "Bzip2 Decompress"])
        assert result == original

    def test_binary_roundtrip(self):
        """Test binary data roundtrip."""
        original = bytes(range(256))
        result = bake(original, ["Bzip2 Compress", "Bzip2 Decompress"])
        assert result == original

    def test_large_roundtrip(self):
        """Test large data roundtrip."""
        original = b"Bzip2 pattern! " * 10000
        result = bake(original, ["Bzip2 Compress", "Bzip2 Decompress"])
        assert result == original


# =============================================================================
# MIXED OPERATIONS (Compression + Other Operations)
# =============================================================================

class TestMixedOperations:
    """Test compression operations mixed with other CyberChef operations."""

    def test_base64_then_compress(self):
        """Test Base64 encoding followed by compression."""
        original = b"hello world"
        result = bake(original, ["To Base64", "Gzip"])
        assert result[:2] == b"\x1f\x8b"

    def test_compress_then_hex(self):
        """Test compression followed by hex encoding."""
        original = b"test"
        result = bake(original, ["Gzip", "To Hex"])
        assert "1f 8b" in result  # Gzip magic in hex

    def test_hex_decompress_chain(self):
        """Test hex decode then decompress."""
        compressed = gzip.compress(b"hello")
        hex_data = compressed.hex()
        result = bake(hex_data, ["From Hex", "Gunzip"])
        assert result == b"hello"

    def test_compress_hash(self):
        """Test compression followed by hashing."""
        original = b"test data"
        result = bake(original, ["Zlib Deflate", "MD5"])
        assert len(result) == 32  # MD5 hash length

    def test_complex_chain(self):
        """Test complex chain with compression in the middle."""
        original = b"The quick brown fox"
        result = bake(original, [
            "To Base64",       # QuickJS
            "Gzip",            # Python
            "To Hex",          # QuickJS
            "From Hex",        # QuickJS
            "Gunzip",          # Python
            "From Base64"      # QuickJS
        ])
        assert result == original

    def test_multiple_compressions(self):
        """Test chaining different compression algorithms."""
        original = b"multi-compression test"

        # Compress with one, decompress, compress with another
        result = bake(original, [
            "Gzip",
            "Gunzip",
            "Zlib Deflate",
            "Zlib Inflate",
            "Bzip2 Compress",
            "Bzip2 Decompress"
        ])
        assert result == original

    def test_compress_between_transforms(self):
        """Test compression between string transformations."""
        original = "hello world"
        result = bake(original, [
            "To Upper case",
            "Gzip",
            "Gunzip",
            "To Lower case"
        ])
        # After upper -> compress -> decompress -> lower
        assert result == "hello world"


# =============================================================================
# EDGE CASES AND ERROR HANDLING
# =============================================================================

class TestEdgeCases:
    """Test edge cases and potential error conditions."""

    def test_very_small_data(self):
        """Test compression of 1-byte data."""
        for algo in ["Zlib Deflate", "Raw Deflate", "Gzip", "Bzip2 Compress"]:
            result = bake(b"X", [algo])
            assert isinstance(result, bytes)

    def test_null_bytes(self):
        """Test compression of data with null bytes."""
        original = b"\x00\x00\x00\x00"
        for algo_pair in [
            ("Zlib Deflate", "Zlib Inflate"),
            ("Raw Deflate", "Raw Inflate"),
            ("Gzip", "Gunzip"),
            ("Bzip2 Compress", "Bzip2 Decompress"),
        ]:
            result = bake(original, list(algo_pair))
            assert result == original

    def test_high_entropy_data(self):
        """Test compression of high-entropy (random-like) data."""
        # High entropy data doesn't compress well
        import os
        original = os.urandom(1000)

        compressed = bake(original, ["Zlib Deflate"])
        # Should still work, even if not much smaller
        assert isinstance(compressed, bytes)

        # Roundtrip should work
        result = bake(compressed, ["Zlib Inflate"])
        assert result == original

    def test_repeated_compression(self):
        """Test compressing already-compressed data."""
        original = b"test data"

        # Double compress
        double_compressed = bake(original, ["Gzip", "Gzip"])
        assert double_compressed[:2] == b"\x1f\x8b"

        # Double decompress
        result = bake(double_compressed, ["Gunzip", "Gunzip"])
        assert result == original

    def test_all_byte_values(self):
        """Test compression with all possible byte values."""
        original = bytes(range(256))

        for algo_pair in [
            ("Zlib Deflate", "Zlib Inflate"),
            ("Raw Deflate", "Raw Inflate"),
            ("Gzip", "Gunzip"),
            ("Bzip2 Compress", "Bzip2 Decompress"),
        ]:
            result = bake(original, list(algo_pair))
            assert result == original, f"Failed for {algo_pair}"
