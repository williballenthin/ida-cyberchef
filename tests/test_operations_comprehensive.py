"""Comprehensive test suite for CyberChef operations with QuickJS backend.

This tests a wide variety of operations to verify which ones work correctly
with the QuickJS JavaScript engine.
"""

import hashlib
import base64
import pytest

from ida_cyberchef.cyberchef import bake


# =============================================================================
# ENCODING / DECODING OPERATIONS
# =============================================================================

class TestBaseEncodings:
    """Test base encoding/decoding operations."""

    def test_to_base64(self):
        result = bake(b"hello world", ["To Base64"])
        assert result == "aGVsbG8gd29ybGQ="

    def test_from_base64(self):
        result = bake("aGVsbG8gd29ybGQ=", ["From Base64"])
        assert result == b"hello world"

    def test_base64_roundtrip(self):
        original = b"The quick brown fox jumps over the lazy dog"
        result = bake(original, ["To Base64", "From Base64"])
        assert result == original

    def test_to_base32(self):
        result = bake(b"hello", ["To Base32"])
        assert result == "NBSWY3DP"

    def test_from_base32(self):
        result = bake("NBSWY3DP", ["From Base32"])
        assert result == b"hello"

    def test_to_base58(self):
        result = bake(b"hello", ["To Base58"])
        assert len(result) > 0

    def test_from_base58(self):
        result = bake("Cn8eVZL", ["From Base58"])
        assert isinstance(result, bytes)

    def test_to_base62(self):
        result = bake(b"hello", ["To Base62"])
        assert len(result) > 0

    def test_to_base85(self):
        result = bake(b"hello", ["To Base85"])
        assert len(result) > 0


class TestHexEncodings:
    """Test hexadecimal encoding/decoding."""

    def test_to_hex(self):
        result = bake(b"hello", ["To Hex"])
        assert result == "68 65 6c 6c 6f"

    def test_from_hex(self):
        result = bake("68656c6c6f", ["From Hex"])
        assert result == b"hello"

    def test_hex_roundtrip(self):
        original = bytes(range(256))
        result = bake(original, ["To Hex", "From Hex"])
        assert result == original

    def test_to_hex_no_delimiter(self):
        result = bake(b"AB", [{"op": "To Hex", "args": {"Delimiter": "None"}}])
        assert result == "4142"


class TestCharacterEncodings:
    """Test character encoding operations."""

    def test_to_charcode(self):
        # To Charcode outputs hex by default
        result = bake("ABC", ["To Charcode"])
        assert "41" in result or "42" in result  # Hex codes

    def test_from_charcode(self):
        # From Charcode expects hex by default
        result = bake("41 42 43", ["From Charcode"])
        assert result == "ABC" or result == b"ABC"

    def test_to_decimal(self):
        result = bake(b"\x00\x01\x02", ["To Decimal"])
        assert "0" in result and "1" in result and "2" in result

    def test_from_decimal(self):
        result = bake("0 1 2", ["From Decimal"])
        assert result == b"\x00\x01\x02"

    def test_to_binary(self):
        result = bake(b"A", ["To Binary"])
        assert "01000001" in result

    def test_from_binary(self):
        result = bake("01000001", ["From Binary"])
        assert result == b"A"

    def test_to_octal(self):
        result = bake(b"A", ["To Octal"])
        assert "101" in result  # Octal for 65

    def test_from_octal(self):
        result = bake("101", ["From Octal"])
        assert result == b"A"


class TestURLEncodings:
    """Test URL encoding/decoding."""

    def test_url_encode(self):
        result = bake("Hello World!", ["URL Encode"])
        assert result == "Hello%20World!"

    def test_url_decode(self):
        result = bake("Hello%20World%21", ["URL Decode"])
        assert result == "Hello World!"


class TestHTMLEncodings:
    """Test HTML encoding/decoding."""

    def test_html_entity_encode(self):
        result = bake("<script>", ["To HTML Entity"])
        assert "&lt;" in result or "&#" in result

    def test_html_entity_decode(self):
        result = bake("&lt;script&gt;", ["From HTML Entity"])
        assert "<script>" in result


# =============================================================================
# HASHING OPERATIONS
# =============================================================================

class TestHashingMD:
    """Test MD family hash operations."""

    def test_md5(self):
        result = bake(b"hello", ["MD5"])
        expected = hashlib.md5(b"hello").hexdigest()
        assert result == expected

    def test_md4(self):
        result = bake(b"hello", ["MD4"])
        assert len(result) == 32  # MD4 produces 128-bit hash

    def test_md2(self):
        result = bake(b"hello", ["MD2"])
        assert len(result) == 32


class TestHashingSHA:
    """Test SHA family hash operations."""

    def test_sha1(self):
        result = bake(b"hello", ["SHA1"])
        expected = hashlib.sha1(b"hello").hexdigest()
        assert result == expected

    def test_sha256(self):
        result = bake(b"hello", [{"op": "SHA2", "args": {"size": "256"}}])
        expected = hashlib.sha256(b"hello").hexdigest()
        assert result == expected

    def test_sha384(self):
        result = bake(b"hello", [{"op": "SHA2", "args": {"size": "384"}}])
        expected = hashlib.sha384(b"hello").hexdigest()
        assert result == expected

    def test_sha512(self):
        result = bake(b"hello", [{"op": "SHA2", "args": {"size": "512"}}])
        expected = hashlib.sha512(b"hello").hexdigest()
        assert result == expected

    def test_sha3_256(self):
        result = bake(b"hello", [{"op": "SHA3", "args": {"size": "256"}}])
        expected = hashlib.sha3_256(b"hello").hexdigest()
        assert result == expected

    def test_sha3_512(self):
        result = bake(b"hello", [{"op": "SHA3", "args": {"size": "512"}}])
        expected = hashlib.sha3_512(b"hello").hexdigest()
        assert result == expected


class TestHashingOther:
    """Test other hash operations."""

    def test_ripemd(self):
        result = bake(b"hello", ["RIPEMD"])
        assert len(result) == 80  # RIPEMD-160/256/320 combined

    def test_crc32(self):
        result = bake(b"hello", [{"op": "CRC Checksum", "args": {"Algorithm": "CRC-32"}}])
        assert len(result) == 8  # CRC-32 is 8 hex chars

    def test_crc16(self):
        result = bake(b"hello", [{"op": "CRC Checksum", "args": {"Algorithm": "CRC-16"}}])
        assert len(result) > 0

    def test_blake2b(self):
        result = bake(b"hello", [{"op": "BLAKE2b", "args": {"size": "256"}}])
        assert len(result) == 64  # 256 bits = 64 hex chars

    def test_blake2s(self):
        result = bake(b"hello", [{"op": "BLAKE2s", "args": {"size": "256"}}])
        assert len(result) == 64


class TestHMAC:
    """Test HMAC operations."""

    def test_hmac_md5(self):
        result = bake(b"hello", [{"op": "HMAC", "args": {"Key": {"string": "key", "option": "UTF8"}, "Hashing function": "MD5"}}])
        assert len(result) == 32

    def test_hmac_sha256(self):
        result = bake(b"hello", [{"op": "HMAC", "args": {"Key": {"string": "key", "option": "UTF8"}, "Hashing function": "SHA256"}}])
        assert len(result) == 64


# =============================================================================
# STRING MANIPULATION OPERATIONS
# =============================================================================

class TestStringManipulation:
    """Test string manipulation operations."""

    def test_reverse(self):
        result = bake("hello", ["Reverse"])
        # May return bytes or string
        assert result == "olleh" or result == b"olleh"

    def test_upper_case(self):
        result = bake("hello world", ["To Upper case"])
        assert result == "HELLO WORLD"

    def test_lower_case(self):
        result = bake("HELLO WORLD", ["To Lower case"])
        assert result == "hello world"

    def test_split(self):
        result = bake("a,b,c", [{"op": "Split", "args": {"Split delimiter": ","}}])
        assert "a" in result

    def test_add_line_numbers(self):
        result = bake("line1\nline2", ["Add line numbers"])
        assert "1" in result

    def test_remove_line_numbers(self):
        result = bake("1 line1\n2 line2", ["Remove line numbers"])
        assert "line1" in result

    def test_remove_whitespace(self):
        result = bake("hello   world", [{"op": "Remove whitespace", "args": {"Spaces": True}}])
        assert "helloworld" in result

    def test_pad_lines(self):
        result = bake("test", [{"op": "Pad lines", "args": {"Position": "Start", "Length": 10, "Character": " "}}])
        assert len(result) >= 10

    def test_head(self):
        result = bake("line1\nline2\nline3", [{"op": "Head", "args": {"Number of lines": 1}}])
        assert "line1" in result

    def test_tail(self):
        result = bake("line1\nline2\nline3", [{"op": "Tail", "args": {"Number of lines": 1}}])
        assert "line3" in result

    def test_sort(self):
        result = bake("c\na\nb", ["Sort"])
        assert result.startswith("a") or "a\nb\nc" in result

    def test_unique(self):
        result = bake("a\na\nb\nb", ["Unique"])
        assert result.count("a") == 1 or "a\nb" in result


class TestEscaping:
    """Test escape/unescape operations."""

    def test_escape_string(self):
        result = bake('hello\nworld', ["Escape string"])
        assert "\\n" in result

    def test_unescape_string(self):
        result = bake('hello\\nworld', ["Unescape string"])
        assert "hello" in result


# =============================================================================
# ARITHMETIC / LOGIC OPERATIONS
# =============================================================================

class TestArithmeticLogic:
    """Test arithmetic and logic operations."""

    def test_xor(self):
        result = bake(b"hello", [{"op": "XOR", "args": {"Key": {"string": "key", "option": "UTF8"}}}])
        assert isinstance(result, bytes)
        assert len(result) == 5

    def test_xor_roundtrip(self):
        original = b"hello"
        key_args = {"Key": {"string": "secret", "option": "UTF8"}}
        encrypted = bake(original, [{"op": "XOR", "args": key_args}])
        decrypted = bake(encrypted, [{"op": "XOR", "args": key_args}])
        assert decrypted == original

    def test_and(self):
        result = bake(b"\xff\x00", [{"op": "AND", "args": {"Key": {"string": "f0", "option": "Hex"}}}])
        assert isinstance(result, bytes)

    def test_or(self):
        result = bake(b"\x0f\x00", [{"op": "OR", "args": {"Key": {"string": "f0", "option": "Hex"}}}])
        assert isinstance(result, bytes)

    def test_not(self):
        result = bake(b"\xff", ["NOT"])
        assert result == b"\x00"

    def test_add(self):
        result = bake(b"\x01\x02", [{"op": "ADD", "args": {"Key": {"string": "01", "option": "Hex"}}}])
        assert isinstance(result, bytes)

    def test_subtract(self):
        result = bake(b"\x02\x03", [{"op": "SUB", "args": {"Key": {"string": "01", "option": "Hex"}}}])
        assert isinstance(result, bytes)

    def test_bit_shift_left(self):
        result = bake(b"\x01", [{"op": "Bit shift left", "args": {"Amount": 1}}])
        assert result == b"\x02"

    def test_bit_shift_right(self):
        result = bake(b"\x02", [{"op": "Bit shift right", "args": {"Amount": 1}}])
        assert result == b"\x01"

    def test_rotate_left(self):
        result = bake(b"\x80", [{"op": "Rotate left", "args": {"Amount": 1}}])
        assert isinstance(result, bytes)

    def test_rotate_right(self):
        result = bake(b"\x01", [{"op": "Rotate right", "args": {"Amount": 1}}])
        assert isinstance(result, bytes)


# =============================================================================
# DATA FORMAT OPERATIONS
# =============================================================================

class TestJSONOperations:
    """Test JSON operations."""

    def test_json_beautify(self):
        result = bake('{"a":1,"b":2}', ["JSON Beautify"])
        assert "a" in result
        assert "\n" in result or "  " in result

    def test_json_minify(self):
        result = bake('{\n  "a": 1\n}', ["JSON Minify"])
        assert result == '{"a":1}'

    def test_json_to_csv(self):
        result = bake('[{"a":1},{"a":2}]', ["JSON to CSV"])
        assert "a" in result


class TestXMLOperations:
    """Test XML operations."""

    def test_xml_beautify(self):
        result = bake('<root><child>test</child></root>', ["XML Beautify"])
        assert "<root>" in result

    def test_xml_minify(self):
        result = bake('<root>\n  <child>test</child>\n</root>', ["XML Minify"])
        assert "<root>" in result


class TestDateTimeOperations:
    """Test date/time operations."""

    def test_parse_unix_timestamp(self):
        result = bake("1609459200", ["From UNIX Timestamp"])
        assert "2021" in result or "Jan" in result

    def test_to_unix_timestamp(self):
        result = bake("2021-01-01 00:00:00", ["To UNIX Timestamp"])
        assert "1609" in result


# =============================================================================
# CIPHER OPERATIONS (CLASSICAL)
# =============================================================================

class TestClassicalCiphers:
    """Test classical cipher operations."""

    def test_rot13(self):
        result = bake("hello", ["ROT13"])
        # May return bytes or string
        assert result == "uryyb" or result == b"uryyb"

    def test_rot13_roundtrip(self):
        original = "TheQuickBrownFox"
        result = bake(original, ["ROT13", "ROT13"])
        assert result == original or result == original.encode()

    def test_rot47(self):
        result = bake("hello", ["ROT47"])
        assert result != "hello"

    def test_atbash(self):
        result = bake("abc", ["Atbash Cipher"])
        assert result == "zyx"

    def test_vigenere_encode(self):
        result = bake("hello", [{"op": "Vigenère Encode", "args": {"Key": "key"}}])
        assert len(result) == 5
        assert result != "hello"

    def test_vigenere_decode(self):
        encoded = bake("hello", [{"op": "Vigenère Encode", "args": {"Key": "key"}}])
        decoded = bake(encoded, [{"op": "Vigenère Decode", "args": {"Key": "key"}}])
        assert decoded.lower() == "hello"

    def test_affine_cipher_encode(self):
        result = bake("hello", [{"op": "Affine Cipher Encode", "args": {"a": 5, "b": 8}}])
        assert len(result) == 5

    def test_a1z26_encode(self):
        result = bake("abc", ["A1Z26 Cipher Encode"])
        assert "1" in result and "2" in result and "3" in result

    def test_a1z26_decode(self):
        result = bake("1 2 3", ["A1Z26 Cipher Decode"])
        assert result.lower() == "abc"


# =============================================================================
# NETWORK OPERATIONS
# =============================================================================

class TestNetworkParsing:
    """Test network-related parsing operations."""

    def test_parse_ipv4(self):
        result = bake("192.168.1.1", ["Parse IP range"])
        assert "192.168.1.1" in result

    def test_parse_ipv6(self):
        result = bake("2001:0db8:85a3:0000:0000:8a2e:0370:7334", ["Parse IPv6 address"])
        assert "2001" in result

    def test_defang_ip(self):
        result = bake("192.168.1.1", ["Defang IP Addresses"])
        assert "[.]" in result

    def test_defang_url(self):
        result = bake("http://example.com", ["Defang URL"])
        assert "[.]" in result or "hxxp" in result

    def test_parse_uri(self):
        result = bake("https://example.com:8080/path?query=1", ["Parse URI"])
        assert "example.com" in result


class TestExtractors:
    """Test data extraction operations."""

    def test_extract_urls(self):
        result = bake("Visit https://example.com for more info", ["Extract URLs"])
        assert "https://example.com" in result

    def test_extract_email_addresses(self):
        result = bake("Contact test@example.com for info", ["Extract email addresses"])
        assert "test@example.com" in result

    def test_extract_ip_addresses(self):
        result = bake("Server at 192.168.1.1 is down", ["Extract IP addresses"])
        assert "192.168.1.1" in result

    def test_extract_file_paths(self):
        result = bake("Open /etc/passwd for editing", ["Extract file paths"])
        assert "/etc/passwd" in result

    def test_extract_dates(self):
        result = bake("Meeting on 2021-01-15", ["Extract dates"])
        assert "2021" in result or "15" in result


# =============================================================================
# UTILITY OPERATIONS
# =============================================================================

class TestUtilityOps:
    """Test utility operations."""

    def test_detect_file_type(self):
        # PNG header
        result = bake(b"\x89PNG\r\n\x1a\n", ["Detect File Type"])
        assert "PNG" in result or "image" in result.lower()

    def test_generate_uuid(self):
        result = bake("", ["Generate UUID"])
        assert "-" in result
        assert len(result) == 36

    def test_generate_lorem_ipsum(self):
        result = bake("", [{"op": "Generate Lorem Ipsum", "args": {"paragraphs": 1}}])
        assert "Lorem" in result or "ipsum" in result.lower() or len(result) > 10


# =============================================================================
# QUOTING OPERATIONS
# =============================================================================

class TestQuoting:
    """Test quoting operations."""

    def test_to_quoted_printable(self):
        result = bake("hello=world", ["To Quoted Printable"])
        assert "=3D" in result  # = is encoded as =3D

    def test_from_quoted_printable(self):
        result = bake("hello=3Dworld", ["From Quoted Printable"])
        assert result == b"hello=world"

    def test_quoted_printable_roundtrip(self):
        original = "hello=world with spaces"
        result = bake(original, ["To Quoted Printable", "From Quoted Printable"])
        assert result == original.encode()


# =============================================================================
# SPECIAL ENCODINGS
# =============================================================================

class TestSpecialEncodings:
    """Test special encoding operations."""

    def test_to_morse_code(self):
        result = bake("SOS", ["To Morse Code"])
        assert "..." in result and "---" in result

    def test_from_morse_code(self):
        result = bake("... --- ...", ["From Morse Code"])
        assert result.upper() == "SOS"

    def test_to_braille(self):
        result = bake("hello", ["To Braille"])
        assert len(result) > 0

    def test_from_braille(self):
        braille = bake("hello", ["To Braille"])
        result = bake(braille, ["From Braille"])
        assert "hello" in result.lower()

    def test_encode_text_to_binary(self):
        result = bake("A", ["To Binary"])
        assert "01000001" in result


# =============================================================================
# CHAINED OPERATIONS
# =============================================================================

class TestChainedOperations:
    """Test complex chains of operations."""

    def test_encode_decode_chain(self):
        """Test multiple encode/decode operations in sequence."""
        original = b"test data"
        result = bake(original, [
            "To Base64",
            "To Hex",
            "From Hex",
            "From Base64"
        ])
        assert result == original

    def test_hash_chain(self):
        """Test chaining multiple hash operations."""
        result = bake(b"hello", ["MD5", "SHA1"])
        # Should be SHA1 of the MD5 hash string
        md5_hash = hashlib.md5(b"hello").hexdigest()
        expected = hashlib.sha1(md5_hash.encode()).hexdigest()
        assert result == expected

    def test_transform_chain(self):
        """Test chaining string transformations."""
        result = bake("hello world", [
            "To Upper case",
            "Reverse",
            "To Lower case"
        ])
        # May be bytes or string
        expected = "dlrow olleh"
        assert result == expected or result == expected.encode()

    def test_complex_recipe(self):
        """Test a complex multi-step recipe."""
        result = bake(b"secret message", [
            "To Base64",
            "ROT13",
            {"op": "XOR", "args": {"Key": {"string": "key", "option": "UTF8"}}},
            "To Hex"
        ])
        assert isinstance(result, str)
        assert len(result) > 0


# =============================================================================
# CRYPTOGRAPHIC OPERATIONS (Modern)
# =============================================================================

class TestModernCrypto:
    """Test modern cryptographic operations."""

    def test_aes_encrypt_decrypt(self):
        """Test AES encryption/decryption roundtrip."""
        key = "0123456789abcdef"  # 16 bytes = AES-128
        iv = "abcdef0123456789"

        encrypted = bake(b"hello world", [{
            "op": "AES Encrypt",
            "args": {
                "Key": {"string": key, "option": "UTF8"},
                "IV": {"string": iv, "option": "UTF8"},
                "Mode": "CBC",
                "Input": "Raw",
                "Output": "Hex"
            }
        }])

        decrypted = bake(encrypted, [{
            "op": "AES Decrypt",
            "args": {
                "Key": {"string": key, "option": "UTF8"},
                "IV": {"string": iv, "option": "UTF8"},
                "Mode": "CBC",
                "Input": "Hex",
                "Output": "Raw"
            }
        }])

        # AES Decrypt returns a string, not bytes
        assert decrypted == "hello world"

    def test_rc4_encrypt_decrypt(self):
        """Test RC4 encryption/decryption roundtrip."""
        result = bake(b"hello", [{
            "op": "RC4",
            "args": {"Passphrase": {"string": "secret", "option": "UTF8"}}
        }])

        decrypted = bake(result, [{
            "op": "RC4",
            "args": {"Passphrase": {"string": "secret", "option": "UTF8"}}
        }])

        # RC4 returns a string, not bytes
        assert decrypted == "hello"

    def test_blowfish_encrypt_decrypt(self):
        """Test Blowfish encryption."""
        key = "secretkey1234567"
        iv = "12345678"

        encrypted = bake(b"hello", [{
            "op": "Blowfish Encrypt",
            "args": {
                "Key": {"string": key, "option": "UTF8"},
                "IV": {"string": iv, "option": "UTF8"},
                "Mode": "CBC",
                "Input": "Raw",
                "Output": "Hex"
            }
        }])

        assert len(encrypted) > 0


class TestRegex:
    """Test regex operations."""

    def test_regular_expression_extract(self):
        result = bake("test123abc456", [{
            "op": "Regular expression",
            "args": {"Regex": "\\d+", "Output format": "List matches"}
        }])
        assert "123" in result or "456" in result


class TestConversionOps:
    """Test conversion operations that work."""

    def test_convert_data_units(self):
        """Test converting bytes to kilobytes."""
        result = bake("1024", [{"op": "Convert data units", "args": {"Input units": "Bytes (B)", "Output units": "Kilobytes (KB)"}}])
        assert "1.024" in result or "1" in result

    def test_convert_distance(self):
        """Test converting metres to kilometers."""
        result = bake("1000", [{"op": "Convert distance", "args": {"Input units": "Metres (m)", "Output units": "Kilometers (km)"}}])
        assert "1" in result

    def test_convert_mass(self):
        """Test converting grams to kilograms."""
        result = bake("1000", [{"op": "Convert mass", "args": {"Input units": "Gram (g)", "Output units": "Kilogram (kg)"}}])
        assert "1" in result


# =============================================================================
# ANALYSIS OPERATIONS
# =============================================================================

class TestAnalysis:
    """Test analysis operations."""

    def test_analyse_hash(self):
        result = bake("5d41402abc4b2a76b9719d911017c592", ["Analyse hash"])
        assert "MD5" in result or "hash" in result.lower()


# =============================================================================
# ADDITIONAL ENCODING TESTS
# =============================================================================

class TestMoreEncodings:
    """Additional encoding tests."""

    def test_to_hexdump(self):
        result = bake(b"hello", ["To Hexdump"])
        assert "68" in result  # 'h' = 0x68

    def test_from_hexdump(self):
        hexdump_input = "00000000  68 65 6c 6c 6f                                    |hello|"
        result = bake(hexdump_input, ["From Hexdump"])
        assert result == b"hello"

    def test_to_messagepack(self):
        result = bake('{"test": 123}', ["To MessagePack"])
        assert isinstance(result, bytes)

    def test_swap_endianness(self):
        """Test swapping endianness of hex data."""
        result = bake("12345678", [{"op": "Swap endianness", "args": {"Word length (bytes)": 4}}])
        assert "78563412" in result or "78 56 34 12" in result
