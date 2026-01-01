import hashlib

from ida_cyberchef.cyberchef import bake, get_chef, plate


def test_from_base64():
    """Test From Base64 operation."""
    test_input = "U28gbG9uZyBhbmQgdGhhbmtzIGZvciBhbGwgdGhlIGZpc2gu"
    result = bake(test_input, ["From Base64"])
    assert result == b"So long and thanks for all the fish."


def test_to_hex():
    """Test To Hex operation."""
    result = bake(b"hello", ["To Hex"])
    assert result == "68 65 6c 6c 6f"


def test_md5():
    """Test MD5 operation."""
    result = bake(b"hello", ["MD5"])
    assert result == "5d41402abc4b2a76b9719d911017c592"


def test_chained_operations():
    """Test chaining operations."""
    result = bake(b"hello", ["To Hex", "From Hex", "MD5"])
    expected = "5d41402abc4b2a76b9719d911017c592"
    assert result == expected


def test_translate_datetime():
    """Test Translate DateTime Format operation."""
    result = bake(
        "15/06/2015 20:45:00",
        [{"op": "Translate DateTime Format", "args": {"outputTimezone": "Australia/Queensland"}}],
    )
    assert "2015" in result


def test_parse_ipv6():
    """Test Parse IPv6 address operation."""
    result = bake(
        "2001:0000:4136:e378:8000:63bf:3fff:fdd2",
        ["Parse IPv6 address"],
    )
    assert "2001:0:4136:e378:8000:63bf:3fff:fdd2" in result


def test_sha256():
    """Test SHA2-256 produces correct standard hash.

    Note: size must be a string "256", not integer 256.
    """
    result = bake(b"hello", [{"op": "SHA2", "args": {"size": "256"}}])
    expected = hashlib.sha256(b"hello").hexdigest()
    assert result == expected


def test_url_encode():
    """Test URL Encode operation."""
    result = bake("Hello World!", ["URL Encode"])
    assert result == "Hello%20World!"


def test_bake_simple():
    """Test bake with simple operations."""
    result = bake(b"hello", ["To Base64"])
    assert result == "aGVsbG8="


def test_bake_chain():
    """Test bake with multiple operations."""
    result = bake(b"hello", ["To Base64", "MD5"])
    assert isinstance(result, str)
    assert len(result) == 32


def test_bake_binary():
    """Test bake with binary data that needs to survive encoding."""
    binary_data = bytes(range(256))
    result = bake(binary_data, ["To Hex", "From Hex"])
    assert result == binary_data


def test_bake_with_args():
    """Test bake with operations that have arguments.

    Note: SHA2 size must be string "256", not integer 256.
    """
    result = bake(b"hello", [{"op": "SHA2", "args": {"size": "256"}}])

    # CyberChef's SHA2 should match standard hashlib
    expected = hashlib.sha256(b"hello").hexdigest()
    assert result == expected


def test_bake_sha2_composition():
    """Test SHA2 composition - double hashing works correctly."""
    # Chain two SHA2 operations
    result = bake(
        b"hello",
        [
            {"op": "SHA2", "args": {"size": "256"}},
            {"op": "SHA2", "args": {"size": "256"}},
        ],
    )

    # Expected: SHA256(SHA256("hello"))
    first_hash = hashlib.sha256(b"hello").hexdigest()
    expected = hashlib.sha256(first_hash.encode()).hexdigest()

    assert result == expected
    assert len(result) == 64  # SHA256 produces 64 hex characters


def test_bake_complex_chain():
    """Test bake with a complex chain of operations."""
    result = bake(b"hello", ["To Hex"])
    assert result == "68 65 6c 6c 6f"

    result = bake(result, ["From Hex"])
    assert result == b"hello"

    result = bake(result, ["MD5"])
    expected = "5d41402abc4b2a76b9719d911017c592"
    assert result == expected


def test_bake_hex_to_sha2_chain():
    """Test chaining To Hex followed by SHA2."""
    result = bake(b"hello", [{"op": "To Hex"}, {"op": "SHA2", "args": {"size": "256"}}])

    # Expected: SHA256 of "68 65 6c 6c 6f"
    hex_str = "68 65 6c 6c 6f"
    expected = hashlib.sha256(hex_str.encode()).hexdigest()

    assert result == expected


def test_bake_md5_chain():
    """Test chaining MD5 operations."""
    result = bake(b"hello", [{"op": "MD5"}, {"op": "MD5"}])

    # Expected: MD5(MD5("hello"))
    first_hash = hashlib.md5(b"hello").hexdigest()
    expected = hashlib.md5(first_hash.encode()).hexdigest()

    assert result == expected


def test_bake_url_operations():
    """Test bake with URL encoding operations."""
    result = bake("Hello World!", ["URL Encode"])
    assert result == "Hello%20World!"


def test_bake_empty_recipe():
    """Test bake with empty recipe returns input unchanged."""
    result = bake(b"hello", [])
    assert result == b"hello" or result == "hello"


def test_plate_bytes():
    """Test plate converts bytes to Dish format."""
    dish = plate(b"hello")
    assert isinstance(dish, dict)
    assert "value" in dish
    assert "type" in dish


def test_plate_string():
    """Test plate converts string to Dish format."""
    dish = plate("hello")
    assert isinstance(dish, dict)
    assert dish["value"] == "hello"


def test_get_chef():
    """Test get_chef returns a valid context."""
    chef = get_chef()
    assert chef is not None
    # Should return same instance on second call
    chef2 = get_chef()
    assert chef is chef2
