# Skipped Tests Audit

## Summary

There are **188 skipped tests** across the JSON-driven test suite. These tests are skipped due to issues in the STPyV8 JavaScript bridging layer that connects Python to the CyberChef JavaScript library.

## Categories by Skip Reason

| Category | Count | Skip Reason |
|----------|-------|-------------|
| 1 | 142 | "CyberChef string input handling broken - Invalid data type enum error" |
| 2 | 21 | "CyberChef operation broken - ArrayBuffer error" |
| 3 | 16 | "CyberChef string input handling broken or operation returns JS objects" |
| 4 | 5 | "BLAKE3 operation is broken in this CyberChef build" |
| 5 | 3 | "CyberChef operation returns JS objects instead of strings" |
| 6 | 1 | "Test expected value truncated or incorrect" |

---

## Category 1: Invalid Data Type Enum Error (142 tests)

### Description
These operations fail with an "Invalid data type enum" error. The CyberChef operations expect input data with a specific `Dish.type` enum value, but the bridging layer is passing the wrong type.

### Affected Files and Operations

| File | Operation | Test Count |
|------|-----------|------------|
| `datetime/unix_timestamp.json` | From UNIX Timestamp | 3 |
| `networking/ipv6.json` | Parse IPv6 address | 6 |
| `networking/url.json` | URL Decode/Encode | 6 |
| `networking/ip_defang.json` | Defang IP Addresses | 5 |
| `networking/ip_format.json` | Change IP Format | 6 |
| `encryption/affine.json` | Affine Cipher Encode/Decode | 3 |
| `encryption/a1z26.json` | A1Z26 Cipher Encode/Decode | 8 |
| `encryption/atbash.json` | Atbash Cipher | 4 |
| `encryption/vigenere.json` | Vigenère Encode/Decode | 3 |
| `encoding/base32.json` | From Base32 | 1 |
| `encoding/base45.json` | To Base45 | 1 |
| `encoding/base64.json` | From Base64 (string input variants) | 9 |
| `encoding/charcode.json` | From/To Charcode | 6 |
| `encoding/decimal.json` | From/To Decimal | 6+ |
| `data_format/json_minify.json` | JSON Minify | 7 |
| `data_format/json_beautify.json` | JSON Beautify | 11 |
| `data_format/json_to_yaml.json` | JSON to YAML | 5 |
| `data_format/json_to_csv.json` | JSON to CSV | 3 |
| `data_format/csv_to_json.json` | CSV to JSON | 4 |
| `data_format/cbor_encode.json` | CBOR Encode | 4 |

### Root Cause Analysis
The `bake()` function in `ida_cyberchef/cyberchef.py` creates a `Dish` object with a type based on the Python input type:
- Python `str` → `Dish.STRING`
- Python `bytes` → `Dish.ARRAY_BUFFER`

However, many CyberChef operations internally expect a specific input type regardless of what the user provides. For example, "From UNIX Timestamp" might expect `STRING` type even when bytes are passed, or vice versa.

### Proposed Fix
1. **Option A**: Create an operation-to-expected-input-type mapping and auto-convert input
2. **Option B**: Update test data to always use bytes input with proper Dish type handling
3. **Option C**: Modify the JavaScript `bake()` call to let CyberChef auto-detect/convert the input type

---

## Category 2: ArrayBuffer Error (21 tests)

### Description
Compression operations fail with ArrayBuffer-related errors when handling binary data.

### Affected Files and Operations

| File | Operation | Test Count |
|------|-----------|------------|
| `compression/lzma.json` | LZMA Compress/Decompress | 9 |
| `compression/bzip2.json` | Bzip2 Compress/Decompress | 10 |
| `compression/cross_compression.json` | Multi-operation compression chains | 2 |

### Root Cause Analysis
These compression operations use `ArrayBuffer` for internal binary data manipulation. The issue is in how STPyV8 bridges ArrayBuffer objects:
1. The `plate()` function attempts to extract bytes from ArrayBuffer using `Array.from(new Uint8Array(...))`
2. This may fail if the ArrayBuffer is not properly accessible across the Python/JS boundary
3. The operations might also return intermediate Dish objects that aren't being handled

### Proposed Fix
1. Investigate the exact error message when running these operations
2. Update `plate()` to handle ArrayBuffer edge cases
3. May need to convert ArrayBuffer to typed array before returning to Python

---

## Category 3: Operations Return JS Objects (16 tests)

### Description
These operations return JavaScript objects instead of strings, which the `plate()` function doesn't properly convert.

### Affected Files and Operations

| File | Operation | Test Count |
|------|-----------|------------|
| `data_format/xml_beautify.json` | XML Beautify | 4 |
| `data_format/xml_minify.json` | XML Minify | 4 |
| `data_format/cbor_decode.json` | CBOR Decode | 3 |
| `data_format/to_messagepack.json` | To MessagePack | 3 |
| `data_format/from_messagepack.json` | From MessagePack | 3 |

### Root Cause Analysis
The `plate()` function handles these Dish types:
- `BYTE_ARRAY` → converts to Python `bytes`
- `STRING` → converts to Python `str`
- `JSON` → returns value as-is

However, when an operation returns a complex JavaScript object (like a parsed XML document or CBOR structure), the `plate()` function may not properly serialize it.

### Proposed Fix
1. For `JSON` type outputs, serialize JS objects using `JSON.stringify()` in the JS context
2. For XML operations, ensure they return string representation
3. Add handling for `STPyV8.JSObject` instances to convert them to Python dicts/lists

---

## Category 4: BLAKE3 Broken (5 tests)

### Description
The BLAKE3 hash operation is completely broken in the current CyberChef build with error: "Data is not a valid string: {}"

### Affected Files

| File | Operation | Test Count |
|------|-----------|------------|
| `hashing/blake3.json` | BLAKE3 | 5 |

### Root Cause Analysis
This appears to be an issue with the CyberChef bundle itself, not the Python bridging. The operation fails even before data processing with a type validation error.

### Proposed Fix
1. Check if newer CyberChef versions fix this
2. If not fixable, document as a known limitation and remove these tests
3. Alternative: implement BLAKE3 natively in Python if needed

---

## Category 5: Test Data Issue (1 test)

### Description
One test has an incorrect expected value.

### Affected Files

| File | Test Name |
|------|-----------|
| `compression/lzstring.json` | lzstring_roundtrip_utf16_binary |

### Proposed Fix
Correct the expected value in the test file.

---

## Implementation Plan

### Phase 1: Fix Invalid Data Type Enum Error (HIGH PRIORITY)
**Impact**: 142 tests (75% of skipped tests)
**Status**: TODO

1. [ ] Add debug logging to capture actual error messages
2. [ ] Investigate which operations need STRING vs ARRAY_BUFFER input
3. [ ] Implement input type auto-conversion in `bake()`
4. [ ] Remove skip markers from fixed tests
5. [ ] Validate fixes in CI

### Phase 2: Fix ArrayBuffer Error (MEDIUM PRIORITY)
**Impact**: 21 tests (11% of skipped tests)
**Status**: TODO

1. [ ] Add ArrayBuffer handling to `plate()` function
2. [ ] Test LZMA and Bzip2 operations individually
3. [ ] Fix any edge cases in binary data handling
4. [ ] Remove skip markers from fixed tests

### Phase 3: Fix JS Object Returns (MEDIUM PRIORITY) ✅ COMPLETED
**Impact**: 10 tests (MessagePack, CBOR Decode)
**Status**: COMPLETED

Changes made:
1. [x] Added `_jsobj_to_python()` helper function to serialize JSObjects using `JSON.stringify()`
2. [x] Updated `plate()` to handle JSObject returns for STRING and JSON dish types
3. [x] Fixed `to_messagepack.json` - corrected `"type": "hex"` to `"type": "bytes"` with encoding
4. [x] Removed skip markers from `from_messagepack.json` (3 tests)
5. [x] Removed skip markers from `cbor_decode.json` (3 tests)
6. [x] Removed skip markers from `to_messagepack.json` (3 tests)

Note: XML Beautify/Minify tests remain skipped as they may have additional string input issues (Phase 1).

### Phase 4: Address BLAKE3 (LOW PRIORITY)
**Impact**: 5 tests (3% of skipped tests)
**Status**: TODO

1. [ ] Investigate if CyberChef bundle update fixes BLAKE3
2. [ ] If not fixable, remove tests or document limitation

### Phase 5: Fix Test Data (LOW PRIORITY) ✅ COMPLETED
**Impact**: 1 test
**Status**: COMPLETED

Changes made:
1. [x] Updated `decode_data_value()` in `tests/data/runner.py` to support `encoding: "latin-1"` for string types
2. [x] Removed skip marker from `lzstring_roundtrip_all_bytes_base64` test

---

## Files Modified

| File | Changes |
|------|---------|
| `ida_cyberchef/cyberchef.py` | Added `_jsobj_to_python()` helper; updated `plate()` for JSObject handling |
| `tests/data/runner.py` | Added latin-1 encoding support for string types in `decode_data_value()` |
| `tests/data/operations/data_format/from_messagepack.json` | Removed skip markers (3 tests) |
| `tests/data/operations/data_format/to_messagepack.json` | Fixed type from "hex" to "bytes", removed skip markers (3 tests) |
| `tests/data/operations/data_format/cbor_decode.json` | Removed skip markers (3 tests) |
| `tests/data/operations/compression/lzstring.json` | Removed skip marker (1 test) |
