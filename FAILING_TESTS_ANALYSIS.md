# Failing Tests Analysis

## Summary
- **Total Tests**: 978 (operations + integration)
- **Passed**: 883 (90.3%)
- **Failed**: 81 (8.3%)
- **Skipped**: 14 (1.4%)

---

## Failure Categories

### Category 1: ArrayBuffer Input Type Mismatch (46 tests)

**Root Cause**: Operations expect `ArrayBuffer` input type, but the `bake()` function doesn't properly convert Python bytes to JavaScript ArrayBuffer for these operations.

**Error**: `JSError: Error: Data is not a valid ArrayBuffer: {}`

| Test File | Tests | Operations Affected |
|-----------|-------|---------------------|
| `test_compression.py` | 14 | Bzip2 Compress/Decompress |
| `test_compression.py` | 12 | LZMA Compress/Decompress |
| `test_compression.py` | 7 | Zip/Unzip |
| `test_compression.py` | 4 | Cross-compression (using Bzip2) |
| `test_compression.py` | 4 | Edge cases (using Bzip2) |
| `test_encoding.py` | 2 | To/From Base62 |
| `test_hashing.py` | 1 | CRC Checksum |

**Specific Tests**:
```
test_compression.py::TestBzip2::test_bzip2_compress_hello_world
test_compression.py::TestBzip2::test_bzip2_decompress_hello_world
test_compression.py::TestBzip2::test_bzip2_compress_empty
test_compression.py::TestBzip2::test_bzip2_decompress_empty
test_compression.py::TestBzip2::test_bzip2_compress_all_bytes
test_compression.py::TestBzip2::test_bzip2_roundtrip_hello_world
test_compression.py::TestBzip2::test_bzip2_roundtrip_all_bytes
test_compression.py::TestBzip2::test_bzip2_roundtrip_utf8
test_compression.py::TestBzip2::test_bzip2_compare_python
test_compression.py::TestBzip2::test_bzip2_decompress_compare_python
test_compression.py::TestBzip2::test_bzip2_highly_compressible
test_compression.py::TestBzip2::test_bzip2_incompressible
test_compression.py::TestBzip2::test_bzip2_large_data
test_compression.py::TestBzip2::test_bzip2_compression_levels
test_compression.py::TestLZMA::test_lzma_compress_hello_world
test_compression.py::TestLZMA::test_lzma_decompress_hello_world
test_compression.py::TestLZMA::test_lzma_compress_empty
test_compression.py::TestLZMA::test_lzma_decompress_empty
test_compression.py::TestLZMA::test_lzma_compress_all_bytes
test_compression.py::TestLZMA::test_lzma_roundtrip_hello_world
test_compression.py::TestLZMA::test_lzma_roundtrip_all_bytes
test_compression.py::TestLZMA::test_lzma_roundtrip_utf8
test_compression.py::TestLZMA::test_lzma_highly_compressible
test_compression.py::TestLZMA::test_lzma_incompressible
test_compression.py::TestLZMA::test_lzma_large_data
test_compression.py::TestLZMA::test_lzma_compression_modes
test_compression.py::TestZip::test_zip_hello_world
test_compression.py::TestZip::test_unzip_hello_world
test_compression.py::TestZip::test_zip_empty
test_compression.py::TestZip::test_zip_roundtrip_hello_world
test_compression.py::TestZip::test_zip_all_bytes
test_compression.py::TestZip::test_zip_compression_methods
test_compression.py::TestZip::test_zip_compression_types
test_compression.py::TestCrossCompression::test_bzip2_then_hex
test_compression.py::TestCrossCompression::test_double_compression_gzip_bzip2
test_compression.py::TestCompressionEdgeCases::test_compression_ratio_highly_compressible
test_compression.py::TestCompressionEdgeCases::test_lorem_ipsum_compression
test_compression.py::TestCompressionEdgeCases::test_null_bytes_compression
test_compression.py::TestCompressionEdgeCases::test_single_byte_compression
test_encoding.py::TestBase62::test_to_base62_empty
test_encoding.py::TestBase62::test_base62_roundtrip_all_bytes
test_hashing.py::TestCRC::test_crc32_python_comparison
```

**Fix Required**: Modify `bake()` or `plate()` in `cyberchef.py` to properly convert Python bytes to JavaScript ArrayBuffer for operations that expect `inputType: ArrayBuffer`.

---

### Category 2: URL Encoding Behavioral Difference (6 tests)

**Root Cause**: CyberChef's URL encoding doesn't encode "unreserved" characters like `=`, `&`, `@`, `+`, `,` by default, while Python's `urllib.parse.quote()` does encode them.

**Error**: `AssertionError: assert 'foo=bar&baz=qux' == 'foo%3Dbar%26baz%3Dqux'`

| Expected (Python) | Actual (CyberChef) |
|-------------------|---------------------|
| `foo%3Dbar%26baz%3Dqux` | `foo=bar&baz=qux` |
| `user%40example.com` | `user@example.com` |
| `a%2Bb%3Dc` | `a+b=c` |
| `Hello%2C%20World!` | `Hello,%20World!` |

**Specific Tests**:
```
test_encoding.py::TestURLEncoding::test_url_encode_vectors[foo=bar&baz=qux-foo%3Dbar%26baz%3Dqux]
test_encoding.py::TestURLEncoding::test_url_encode_vectors[user@example.com-user%40example.com]
test_encoding.py::TestURLEncoding::test_url_encode_vectors[a+b=c-a%2Bb%3Dc]
test_encoding.py::TestURLEncoding::test_url_encode_hello_world
test_encoding.py::TestURLEncoding::test_url_encode_compare_python
test_encoding.py::TestEncodingEdgeCases::test_unicode_emoji_url_encode
```

**Fix Required**: Update test expectations to match CyberChef's URL encoding behavior, or use the "Encode all special chars" option if available.

---

### Category 3: LZString Decompression Returns Null (7 tests)

**Root Cause**: LZString decompress operations return `null` when decompressing data that wasn't compressed with LZString compress.

**Error**: `JSError: Error: Data is not a valid string: null`

**Specific Tests**:
```
test_compression.py::TestLZString::test_lzstring_decompress_hello_world
test_compression.py::TestLZString::test_lzstring_decompress_empty
test_compression.py::TestLZString::test_lzstring_roundtrip_hello_world
test_compression.py::TestLZString::test_lzstring_roundtrip_all_bytes
test_compression.py::TestLZString::test_lzstring_roundtrip_utf8
test_compression.py::TestLZString::test_lzstring_highly_compressible
test_compression.py::TestLZString::test_lzstring_compression_formats
```

**Fix Required**: First compress with LZString, then decompress. The tests were trying to decompress uncompressed data.

---

### Category 4: BLAKE3 Operation Requires Empty String Default (6 tests)

**Root Cause**: BLAKE3 operation has a required "Size (bytes)" argument that defaults to empty string `''`, but the operation fails when size is not properly specified.

**Error**: `STPyV8.JSError` (various)

**Specific Tests**:
```
test_hashing.py::TestBLAKE3::test_blake3_default_size
test_hashing.py::TestBLAKE3::test_blake3_various_sizes[BLAKE3-128bit]
test_hashing.py::TestBLAKE3::test_blake3_various_sizes[BLAKE3-256bit]
test_hashing.py::TestBLAKE3::test_blake3_various_sizes[BLAKE3-512bit]
test_hashing.py::TestBLAKE3::test_blake3_empty_input
test_hashing.py::TestBLAKE3::test_blake3_with_key
```

**Fix Required**: Specify the correct "Size (bytes)" argument format (e.g., `32` for 256-bit output).

---

### Category 5: BLAKE2 Size/Key Argument Mismatch (7 tests)

**Root Cause**: BLAKE2b/BLAKE2s size options don't match all Python hashlib sizes, and keyed hashing argument format differs.

**Error**: Output hash doesn't match Python hashlib

**Specific Tests**:
```
test_hashing.py::TestBLAKE2b::test_blake2b_various_sizes_vs_python[BLAKE2b-256]
test_hashing.py::TestBLAKE2b::test_blake2b_various_sizes_vs_python[BLAKE2b-384]
test_hashing.py::TestBLAKE2b::test_blake2b_with_key
test_hashing.py::TestBLAKE2s::test_blake2s_various_sizes_vs_python[BLAKE2s-128]
test_hashing.py::TestBLAKE2s::test_blake2s_various_sizes_vs_python[BLAKE2s-160]
test_hashing.py::TestBLAKE2s::test_blake2s_various_sizes_vs_python[BLAKE2s-224]
test_hashing.py::TestBLAKE2s::test_blake2s_with_key
```

**Fix Required**:
- BLAKE2b only supports: 512, 384, 256, 160, 128 bits
- BLAKE2s only supports: 256, 160, 128 bits
- Update tests to use available sizes only

---

### Category 6: Charcode Operation Has Window.app Dependency (6 tests)

**Root Cause**: The "From Charcode" operation tries to access `window.app.options` which doesn't exist in the Node.js/STPyV8 environment.

**Error**: `TypeError: Cannot read properties of undefined (reading 'options')`

**Specific Tests**:
```
test_encoding.py::TestCharcode::test_to_charcode_hello
test_encoding.py::TestCharcode::test_from_charcode_hello
test_encoding.py::TestCharcode::test_from_charcode_empty
test_encoding.py::TestCharcode::test_charcode_roundtrip_hello
test_encoding.py::TestCharcode::test_charcode_roundtrip_utf8
test_encoding.py::TestCharcode::test_from_charcode_base_hex
```

**Fix Required**: Add `window.app = { options: { attemptHighlight: false } }` to the JS polyfills in `cyberchef.py`.

---

### Category 7: Hex Delimiter/Format Issues (2 tests)

**Root Cause**:
1. "To Hex" with 0x prefix doesn't add spaces between bytes
2. "From Hex" with "None" delimiter interprets hex differently

**Errors**:
- `assert '0x680x650x6c0x6c0x6f' == '0x68 0x65 0x6c 0x6c 0x6f'`
- `assert b'Hello' == b'hello'`

**Specific Tests**:
```
test_encoding.py::TestHex::test_to_hex_0x_prefix
test_encoding.py::TestHex::test_from_hex_no_delimiter
```

**Fix Required**: Update test expectations to match CyberChef behavior.

---

### Category 8: Decimal Encoding Base Difference (1 test)

**Root Cause**: "To Charcode" outputs hex by default (base 16), test expected decimal.

**Error**: `assert '68 65 6c 6c 6f' == '104 101 108 108 111'`

**Specific Test**:
```
test_encoding.py::TestDecimal::test_from_decimal_delimiter_comma
```

**Fix Required**: Specify base argument correctly.

---

### Category 9: AES/Encryption Argument Format (3 tests)

**Root Cause**: Complex encryption operations require specific argument formats for keys, IVs, and modes.

**Specific Tests**:
```
test_encryption.py::TestAES::test_aes_binary_data
test_encryption.py::TestBlowfish::test_blowfish_ecb_mode
test_encryption.py::TestEncryptionEdgeCases::test_des_triple_des_different_results
test_encryption.py::TestEncryptionEdgeCases::test_vigenere_with_numeric_key
```

**Fix Required**: Verify correct argument format for toggleString and argSelector types.

---

## Recommended Fixes (Priority Order)

### High Priority (Core Infrastructure)

1. **Fix ArrayBuffer conversion** in `cyberchef.py`:
   - Detect when operation expects `inputType: ArrayBuffer`
   - Properly convert Python bytes to JS ArrayBuffer
   - This fixes 46 tests

2. **Add window.app polyfill** in `cyberchef.py`:
   ```javascript
   window.app = { options: { attemptHighlight: false } };
   ```
   - This fixes 6 Charcode tests

### Medium Priority (Test Adjustments)

3. **Update URL encoding tests** to match CyberChef's RFC 3986 behavior
   - Don't expect `=`, `&`, `@`, `+`, `,` to be encoded
   - This fixes 6 tests

4. **Fix BLAKE2/BLAKE3 tests**:
   - Use only supported size options
   - Correct key argument format
   - This fixes 13 tests

5. **Fix LZString tests**:
   - Compress before decompress in roundtrip tests
   - This fixes 7 tests

### Low Priority (Minor Fixes)

6. **Fix Hex delimiter tests** - update expectations
7. **Fix Decimal/Charcode base** - specify correct base argument
8. **Fix encryption argument formats** - verify toggleString format

---

## Test Pass Rate After Fixes

| Category | Tests | After Fix |
|----------|-------|-----------|
| ArrayBuffer | 46 | Passing |
| URL Encoding | 6 | Passing |
| LZString | 7 | Passing |
| BLAKE3 | 6 | Passing |
| BLAKE2 | 7 | Passing |
| Charcode | 6 | Passing |
| Hex | 2 | Passing |
| Decimal | 1 | Passing |
| Encryption | 4 | Passing |

**Expected after fixes**: 964/978 = **98.6% pass rate**
