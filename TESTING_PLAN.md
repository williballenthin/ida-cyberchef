# Comprehensive CyberChef Operations Testing Suite Plan

## Executive Summary

This plan outlines a strategy to develop a comprehensive unit testing suite that validates every supported CyberChef operation in the IDA CyberChef plugin. The goal is to ensure reliable operation execution across all 443 unique operations spanning 16 categories.

## Current State Analysis

### Existing Test Coverage
- **15 test files** with approximately 100 test cases
- Focus on: core engine (`test_cyberchef.py`), recipe execution, Qt models, UI widgets
- **Limited operation coverage**: Only ~15 operations tested (Base64, Hex, MD5, SHA, URL encode)
- No systematic coverage of the 443 available operations

### Upstream CyberChef Reference
- CyberChef maintains **161 operation test files**
- Test format: Input → Recipe → Expected Output with named test cases
- Covers edge cases: empty input, UTF-8, binary data (all 256 bytes), error conditions

## Testing Architecture

### Directory Structure
```
tests/
├── conftest.py                     # Shared fixtures
├── operations/                     # Operation-specific tests
│   ├── __init__.py
│   ├── test_encoding.py            # Base64, Hex, URL encode/decode, etc.
│   ├── test_hashing.py             # MD5, SHA, BLAKE, CRC, etc.
│   ├── test_encryption.py          # AES, DES, XOR, ciphers
│   ├── test_compression.py         # Gzip, Bzip2, Deflate, etc.
│   ├── test_data_format.py         # JSON, CSV, XML conversions
│   ├── test_networking.py          # IP parsing, URL operations
│   ├── test_arithmetic_logic.py    # ADD, XOR, AND, OR, shifts
│   ├── test_datetime.py            # Date/time operations
│   ├── test_extractors.py          # Regex, IP extraction, etc.
│   ├── test_utils.py               # String manipulation, etc.
│   ├── test_multimedia.py          # Image operations
│   ├── test_public_key.py          # RSA, ECDSA, PGP
│   └── test_forensics.py           # ELF, file detection
├── integration/                    # End-to-end tests
│   ├── test_recipe_chains.py       # Multi-operation recipes
│   └── test_binary_roundtrip.py    # Binary data preservation
└── edge_cases/                     # Error handling tests
    ├── test_invalid_input.py
    └── test_error_recovery.py
```

### Test Case Format
```python
@pytest.mark.parametrize("name,input_data,recipe,expected", [
    ("simple", b"hello", ["To Base64"], "aGVsbG8="),
    ("empty", b"", ["To Base64"], ""),
    ("binary", bytes(range(256)), ["To Base64"], ALL_BYTES_B64),
    ("utf8", "ნუ პანიკას".encode(), ["To Base64"], "4YOc4YOjIOGDnuGDkOGDnOGDmOGDmeGDkOGDow=="),
])
def test_to_base64(name, input_data, recipe, expected):
    result = bake(input_data, recipe)
    assert result == expected, f"Test '{name}' failed"
```

## Operation Categories & Test Strategy

### 1. Encoding/Decoding (Priority: HIGH)
**Operations**: 72 in Data format + encoding-related
**Test Categories**:
- Base16/32/45/58/62/64/85/92 encode/decode
- Hex conversions
- URL encode/decode
- ASCII/UTF-8/Latin1 conversions
- Binary representations

**Test Vectors**:
- Empty string
- "Hello, World!" (standard)
- All 256 bytes (binary completeness)
- UTF-8 characters
- Roundtrip: encode → decode = original

### 2. Hashing (Priority: HIGH)
**Operations**: 38 operations
**Algorithms**: MD5, SHA1, SHA2, SHA3, BLAKE2/3, CRC, HMAC, etc.

**Test Strategy**:
- Compare against Python's `hashlib` for standard algorithms
- Use known test vectors from RFCs
- Test different output formats (hex, base64)
- Test keyed hashes (HMAC, keyed BLAKE)

### 3. Encryption/Encoding (Priority: HIGH)
**Operations**: 77 operations
**Categories**:
- Symmetric: AES, DES, 3DES, Blowfish, ChaCha20
- Classical: ROT13, Vigenère, Caesar, Affine
- Key derivation: PBKDF2, scrypt, Argon2

**Test Strategy**:
- Encrypt → Decrypt = original
- Known test vectors for standard algorithms
- Mode variations (CBC, ECB, CTR, GCM)
- Different key sizes (AES-128/192/256)

### 4. Compression (Priority: MEDIUM)
**Operations**: 19 operations
**Algorithms**: Gzip, Bzip2, Zlib, Deflate, LZMA, LZ4

**Test Strategy**:
- Compress → Decompress = original
- Compare against Python standard library
- Various compression levels
- Large and small inputs

### 5. Arithmetic/Logic (Priority: MEDIUM)
**Operations**: 22 operations
**Operations**: XOR, AND, OR, ADD, SUB, bit shifts, rotations

**Test Strategy**:
- Known key/data combinations
- Edge cases: all zeros, all ones
- Key wrapping behavior

### 6. Networking (Priority: MEDIUM)
**Operations**: 33 operations
**Categories**: IP parsing, URL operations, MAC addresses, checksums

**Test Strategy**:
- Valid/invalid IP addresses
- IPv4/IPv6 formats
- URL parsing and manipulation

### 7. Date/Time (Priority: LOW)
**Operations**: 9 operations

**Test Strategy**:
- Standard date formats
- Timezone conversions
- Unix timestamps

### 8. Extractors (Priority: LOW)
**Operations**: 17 operations
**Categories**: Regex, IP extraction, email extraction

**Test Strategy**:
- Documents with embedded data
- Edge cases with no matches

### 9. Multimedia (Priority: LOW)
**Operations**: 24 operations

**Test Strategy**:
- Skip network-dependent operations
- Test with small test images
- Format conversions

### 10. Public Key (Priority: LOW)
**Operations**: 23 operations

**Test Strategy**:
- Use pre-generated test keys
- Sign/verify roundtrips
- Key parsing

## Implementation Phases

### Phase 1: Test Infrastructure (Day 1)
- [ ] Create `tests/conftest.py` with shared fixtures
- [ ] Create `tests/operations/__init__.py`
- [ ] Define test constants (ALL_BYTES, test vectors)
- [ ] Create helper functions for test generation

### Phase 2: Core Operations (Day 1-2)
- [ ] Encoding tests (Base64, Hex, URL)
- [ ] Hashing tests (MD5, SHA family)
- [ ] Basic encryption tests (XOR, AES, DES)

### Phase 3: Extended Operations (Day 2-3)
- [ ] Compression tests
- [ ] Arithmetic/Logic tests
- [ ] Networking tests
- [ ] Date/Time tests

### Phase 4: Edge Cases & Integration (Day 3)
- [ ] Error handling tests
- [ ] Recipe chain tests
- [ ] Binary data preservation tests
- [ ] Performance tests for large inputs

## Test Vectors Repository

### Standard Test Inputs
```python
# All 256 byte values
ALL_BYTES = bytes(range(256))

# Standard ASCII test
HELLO_WORLD = b"Hello, World!"

# UTF-8 test (Georgian)
UTF8_TEST = "ნუ პანიკას".encode('utf-8')

# Empty input
EMPTY = b""

# Large input (1MB)
LARGE_INPUT = b"A" * (1024 * 1024)
```

### Operation-Specific Vectors
Leverage upstream CyberChef test vectors where applicable, adapting their JavaScript format to Python.

## Success Criteria

1. **Coverage**: At least 90% of operations have at least one test
2. **Reliability**: All tests pass consistently
3. **Documentation**: Each test file has clear docstrings
4. **Maintainability**: Easy to add new operation tests
5. **Performance**: Full test suite runs in < 5 minutes

## Risk Mitigation

1. **Network-dependent operations**: Mock or skip (e.g., DNS over HTTPS)
2. **Multimedia operations**: Use small test fixtures
3. **Slow operations**: Add timeout annotations
4. **V8 limitations**: Document known issues

## Estimated Operation Test Count

| Category | Operations | Tests (min) |
|----------|------------|-------------|
| Data format | 72 | 150 |
| Encryption | 77 | 200 |
| Hashing | 38 | 100 |
| Networking | 33 | 80 |
| Utils | 46 | 100 |
| Arithmetic | 22 | 50 |
| Multimedia | 24 | 30 |
| Code tidy | 24 | 50 |
| Compression | 19 | 50 |
| Extractors | 17 | 40 |
| Public Key | 23 | 60 |
| Other | 17 | 40 |
| Forensics | 9 | 20 |
| Date/Time | 9 | 25 |
| Flow control | 9 | 20 |
| Language | 4 | 10 |
| **Total** | **443** | **~1025** |

## Next Steps

1. Review and approve this plan
2. Begin Phase 1: Test Infrastructure
3. Implement tests category by category
4. Continuous integration for all tests
