# IDA CyberChef Test Infrastructure

This directory contains the comprehensive testing infrastructure for the IDA CyberChef plugin, designed to test all 443 unique CyberChef operations across 16 categories.

## Structure

```
tests/
├── conftest.py                    # Main pytest configuration and fixtures
├── operations/                     # Operation-specific tests
│   ├── __init__.py                # Package initialization
│   └── conftest.py                # Operation-specific fixtures
├── test_cyberchef.py              # Core CyberChef API tests
└── ...                            # Other test files
```

## Main Test Infrastructure (`conftest.py`)

The main `conftest.py` file provides:

### Standard Test Constants

- **ALL_BYTES**: All 256 possible byte values (0x00-0xFF)
- **HELLO_WORLD**: Standard "Hello, World!" test string
- **UTF8_SIMPLE, UTF8_EMOJI, UTF8_MULTILANG**: Various UTF-8 test strings
- **BINARY_ZEROS, BINARY_ONES, BINARY_ALTERNATING**: Binary test patterns
- **BASE64_TEST_VECTORS**: Standard RFC 4648 Base64 test vectors
- **HASH_TEST_VECTORS**: Standard hash test vectors for MD5, SHA1, SHA256, SHA512
- **URL_ENCODE_TEST_VECTORS**: URL encoding test cases
- **LOREM_IPSUM**: Standard Lorem Ipsum text for compression testing

### Pytest Fixtures

#### Core Fixtures

- **`chef`**: Session-scoped fixture providing cached CyberChef instance
- **`bake_fn`**: Fixture providing the main `bake()` function
- **`plate_fn`**: Fixture providing the `plate()` conversion function

#### Test Data Fixtures

- **`all_bytes`**: All 256 byte values
- **`hello_world`**: Standard test string
- **`utf8_test_strings`**: Dictionary of UTF-8 test strings
- **`binary_test_data`**: Dictionary of binary test patterns
- **`base64_vectors`**: RFC 4648 Base64 test vectors
- **`hash_vectors`**: Hash algorithm test vectors

### Helper Functions

#### `roundtrip_test(input_data, encode_recipe, decode_recipe, expected=None)`

Test that encode→decode returns the original input.

```python
# Test that To Hex → From Hex returns original
assert roundtrip_test(b"hello", ["To Hex"], ["From Hex"])

# Test Base64 encoding/decoding
assert roundtrip_test(b"test data", ["To Base64"], ["From Base64"])
```

#### `verify_hash(input_data, operation, expected_hash)`

Verify that a CyberChef hash operation produces the expected hash.

```python
assert verify_hash(
    b"hello",
    {"op": "SHA2", "args": {"size": "256"}},
    "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
)
```

#### `get_python_hash(input_data, algorithm)`

Get hash using Python's hashlib for comparison.

```python
expected = get_python_hash(b"hello", "sha256")
result = bake(b"hello", [{"op": "SHA2", "args": {"size": "256"}}])
assert result == expected
```

#### `assert_roundtrip(input_data, encode_recipe, decode_recipe, expected=None)`

Like `roundtrip_test` but raises AssertionError with detailed information on failure.

```python
assert_roundtrip(b"hello", ["To Hex"], ["From Hex"])
```

#### `compare_with_python(input_data, cyberchef_recipe, python_func)`

Compare CyberChef result with Python standard library implementation.

```python
import base64
assert compare_with_python(
    b"hello",
    ["To Base64"],
    lambda data: base64.b64encode(data).decode()
)
```

## Operations Test Infrastructure (`operations/conftest.py`)

The operations-specific configuration provides:

### Operation Availability Checking

#### `is_operation_available(operation_name)`

Check if a CyberChef operation is available.

```python
if is_operation_available("AES Encrypt"):
    # Run AES tests
    pass
```

#### `skip_if_unavailable(operation_name)`

Pytest marker to skip test if operation is not available.

```python
@skip_if_unavailable("AES Encrypt")
def test_aes_encryption():
    result = bake(b"data", ["AES Encrypt"])
    assert result
```

#### `require_operations(*operation_names)`

Pytest marker to skip test if any required operations are unavailable.

```python
@require_operations("To Base64", "From Base64")
def test_base64_roundtrip():
    assert roundtrip_test(b"data", ["To Base64"], ["From Base64"])
```

### Operation Test Data Fixtures

- **`encoding_test_data`**: Test data for encoding operations
- **`compression_test_data`**: Test data for compression operations
- **`encryption_test_data`**: Test data and keys for encryption operations
- **`hash_test_data`**: Test inputs for hash operations
- **`parsing_test_data`**: Test data for parsing operations (IP, URL, JSON, etc.)
- **`datetime_test_data`**: Test datetime strings in various formats

### Operation Category Fixtures

- **`operation_categories`**: Mapping of operations by category
- **`reversible_operations`**: Pairs of reversible encode/decode operations

### Operation Testing Helpers

#### `test_operation_with_args(operation_name, input_data, args, expected_type=None)`

Test an operation with specific arguments.

```python
success, result = test_operation_with_args(
    "SHA2",
    b"hello",
    {"size": "256"},
    expected_type=str
)
assert success
assert len(result) == 64  # SHA256 hex digest length
```

#### `get_operation_output_type(operation_name, input_data=b"test")`

Determine the output type of an operation.

```python
output_type = get_operation_output_type("To Base64")
assert output_type == str

output_type = get_operation_output_type("From Base64")
assert output_type == bytes
```

#### `assert_operation_succeeds(operation_name, input_data, args=None)`

Assert that an operation executes without error.

```python
assert_operation_succeeds("MD5", b"hello")
assert_operation_succeeds("SHA2", b"hello", {"size": "256"})
```

#### `operation_smoke_test` (fixture)

Fixture for smoke testing operations.

```python
def test_all_encoding_ops(operation_smoke_test):
    for op in ["To Base64", "To Hex", "URL Encode"]:
        operation_smoke_test(op)
```

## Usage Examples

### Basic Operation Test

```python
def test_base64_encoding():
    """Test Base64 encoding with standard test vectors."""
    result = bake(b"hello", ["To Base64"])
    assert result == "aGVsbG8="
```

### Using Fixtures

```python
def test_with_fixtures(bake_fn, base64_vectors):
    """Test Base64 using fixtures."""
    for input_data, expected in base64_vectors:
        result = bake_fn(input_data, ["To Base64"])
        assert result == expected
```

### Roundtrip Testing

```python
def test_hex_roundtrip(all_bytes):
    """Test that hex encoding/decoding preserves all bytes."""
    assert_roundtrip(all_bytes, ["To Hex"], ["From Hex"])
```

### Hash Verification

```python
def test_hash_with_vectors(hash_vectors):
    """Test hash operations with standard test vectors."""
    for input_data, expected_hash in hash_vectors["sha256"]:
        assert verify_hash(
            input_data,
            {"op": "SHA2", "args": {"size": "256"}},
            expected_hash
        )
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input_data,expected", BASE64_TEST_VECTORS)
def test_base64_parametrized(input_data, expected):
    """Test Base64 encoding with parametrized inputs."""
    result = bake(input_data, ["To Base64"])
    assert result == expected
```

### Testing with Operation Arguments

```python
def test_sha2_sizes():
    """Test SHA2 with different sizes."""
    test_cases = [
        ("224", 56),  # SHA2-224 produces 56 hex chars
        ("256", 64),  # SHA2-256 produces 64 hex chars
        ("384", 96),  # SHA2-384 produces 96 hex chars
        ("512", 128), # SHA2-512 produces 128 hex chars
    ]

    for size, expected_length in test_cases:
        result = bake(b"hello", [{"op": "SHA2", "args": {"size": size}}])
        assert len(result) == expected_length
```

### Skipping Unavailable Operations

```python
@skip_if_unavailable("AES Encrypt")
def test_aes():
    """Test AES encryption (skipped if not available)."""
    result = bake(
        b"secret",
        [{"op": "AES Encrypt", "args": {"key": "0123456789ABCDEF"}}]
    )
    assert result
```

### Testing Operation Chains

```python
def test_operation_chain():
    """Test chaining multiple operations."""
    # Convert to hex, then hash the hex string
    result = bake(
        b"hello",
        [
            "To Hex",
            {"op": "SHA2", "args": {"size": "256"}}
        ]
    )

    # Verify against Python
    import hashlib
    hex_str = "68 65 6c 6c 6f"
    expected = hashlib.sha256(hex_str.encode()).hexdigest()
    assert result == expected
```

## Test Vector Sources

The test vectors are derived from:

1. **RFC 4648**: Base64, Base32 encoding standards
2. **NIST FIPS**: Hash function test vectors (MD5, SHA family)
3. **CyberChef upstream**: Original CyberChef test suite
4. **Python standard library**: For verification and comparison

## Running Tests

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_cyberchef.py

# Run tests matching pattern
pytest -k "base64"

# Run with coverage
pytest --cov=ida_cyberchef --cov-report=html
```

## Writing New Tests

When adding tests for new operations:

1. Use the appropriate fixtures from `conftest.py`
2. Use standard test vectors when available
3. Test roundtrip where applicable (encode→decode)
4. Test edge cases (empty input, all bytes, UTF-8)
5. Use `skip_if_unavailable` for optional operations
6. Compare with Python stdlib when possible

Example template:

```python
from tests.conftest import roundtrip_test, verify_hash

@skip_if_unavailable("New Operation")
def test_new_operation(bake_fn):
    """Test description."""
    # Basic test
    result = bake_fn(b"test", ["New Operation"])
    assert result

    # Roundtrip if applicable
    if has_inverse_operation:
        assert_roundtrip(b"test", ["New Operation"], ["Inverse Operation"])

    # Edge cases
    assert bake_fn(b"", ["New Operation"])
    assert bake_fn(ALL_BYTES, ["New Operation"])
```

## Contributing

When adding new test infrastructure:

1. Add constants to the appropriate section
2. Document new fixtures with clear docstrings
3. Provide usage examples in docstrings
4. Add test vectors with source attribution
5. Update this README with new features
