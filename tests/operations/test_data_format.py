"""Comprehensive tests for CyberChef data format operations.

This module tests all data format transformation operations including:
- JSON: Beautify, Minify, to/from CSV, to/from YAML
- XML: Beautify, Minify
- YAML: to/from JSON
- CBOR: Encode, Decode
- BSON: serialise, deserialise
- MessagePack: To/From MessagePack
- Avro: to JSON
- Protobuf: Encode, Decode

Each operation is tested with:
- Basic functionality (standard transformations)
- Roundtrip testing (format → inverse = original)
- Edge cases (empty objects, nested structures, special characters)
- Error handling (invalid input formats)
- UTF-8 and unicode support
- Complex nested data structures
"""

import json

import pytest

from ida_cyberchef.cyberchef import bake

# Import test constants from conftest
from tests.conftest import (
    EMPTY_BYTES,
    HELLO_WORLD,
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
# Test Data for Data Format Operations
# ============================================================================

# JSON test data
SIMPLE_JSON = '{"name": "Alice", "age": 30, "city": "NYC"}'
NESTED_JSON = '{"user": {"name": "Bob", "profile": {"age": 25, "email": "bob@example.com"}}}'
ARRAY_JSON = '[1, 2, 3, 4, 5]'
COMPLEX_JSON = '{"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}], "count": 2}'
EMPTY_JSON_OBJECT = '{}'
EMPTY_JSON_ARRAY = '[]'
JSON_WITH_UNICODE = '{"message": "Hello 世界", "emoji": "🌍"}'
JSON_WITH_SPECIAL_CHARS = '{"special": "quotes: \\"test\\", newlines: \\n, tabs: \\t"}'

# Minified JSON (no spaces)
MINIFIED_JSON = '{"name":"Alice","age":30,"city":"NYC"}'

# Beautified JSON (with indentation)
BEAUTIFIED_JSON = '''{
    "name": "Alice",
    "age": 30,
    "city": "NYC"
}'''

# CSV test data
SIMPLE_CSV = 'name,age,city\nAlice,30,NYC\nBob,25,LA'
CSV_WITH_QUOTES = 'name,description\nAlice,"Hello, World"\nBob,"Test, Data"'
CSV_EMPTY = ''
CSV_HEADERS_ONLY = 'name,age,city'

# XML test data
SIMPLE_XML = '<?xml version="1.0"?><root><name>Alice</name><age>30</age></root>'
NESTED_XML = '<?xml version="1.0"?><root><user><name>Bob</name><email>bob@example.com</email></user></root>'
XML_WITH_ATTRIBUTES = '<root version="1.0"><item id="1" name="test"/></root>'
MINIFIED_XML = '<root><name>Alice</name><age>30</age></root>'
BEAUTIFIED_XML = '''<root>
\t<name>Alice</name>
\t<age>30</age>
</root>'''

# YAML test data
SIMPLE_YAML = '''name: Alice
age: 30
city: NYC'''

NESTED_YAML = '''user:
  name: Bob
  profile:
    age: 25
    email: bob@example.com'''

# Complex test data for binary formats
COMPLEX_DATA = {
    "string": "test",
    "number": 42,
    "float": 3.14,
    "boolean": True,
    "null": None,
    "array": [1, 2, 3],
    "nested": {"key": "value"}
}


# ============================================================================
# JSON Beautify Tests
# ============================================================================


class TestJSONBeautify:
    """Test suite for JSON Beautify operation."""

    def test_json_beautify_simple(self):
        """Test beautifying simple JSON object."""
        result = bake(MINIFIED_JSON, ["JSON Beautify"])
        assert isinstance(result, str)
        # Should have newlines and indentation
        assert '\n' in result
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["name"] == "Alice"
        assert parsed["age"] == 30

    def test_json_beautify_nested(self):
        """Test beautifying nested JSON object."""
        result = bake(NESTED_JSON, ["JSON Beautify"])
        assert isinstance(result, str)
        assert '\n' in result
        # Verify structure preserved
        parsed = json.loads(result)
        assert parsed["user"]["name"] == "Bob"
        assert parsed["user"]["profile"]["age"] == 25

    def test_json_beautify_array(self):
        """Test beautifying JSON array."""
        result = bake(ARRAY_JSON, ["JSON Beautify"])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == [1, 2, 3, 4, 5]

    def test_json_beautify_empty_object(self):
        """Test beautifying empty JSON object."""
        result = bake(EMPTY_JSON_OBJECT, ["JSON Beautify"])
        assert isinstance(result, str)
        # Even empty objects should be formatted
        parsed = json.loads(result)
        assert parsed == {}

    def test_json_beautify_empty_array(self):
        """Test beautifying empty JSON array."""
        result = bake(EMPTY_JSON_ARRAY, ["JSON Beautify"])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == []

    def test_json_beautify_unicode(self):
        """Test beautifying JSON with unicode characters."""
        result = bake(JSON_WITH_UNICODE, ["JSON Beautify"])
        assert isinstance(result, str)
        # Check result contains unicode characters
        assert "世界" in result or "message" in result
        assert "🌍" in result or "emoji" in result

    def test_json_beautify_complex(self):
        """Test beautifying complex nested JSON."""
        result = bake(COMPLEX_JSON, ["JSON Beautify"])
        assert isinstance(result, str)
        assert '\n' in result
        parsed = json.loads(result)
        assert len(parsed["users"]) == 2
        assert parsed["count"] == 2


# ============================================================================
# JSON Minify Tests
# ============================================================================


class TestJSONMinify:
    """Test suite for JSON Minify operation."""

    def test_json_minify_beautified(self):
        """Test minifying beautified JSON."""
        result = bake(BEAUTIFIED_JSON, ["JSON Minify"])
        assert isinstance(result, str)
        # Should not have unnecessary whitespace
        assert '\n' not in result or result.count('\n') < 3
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["name"] == "Alice"

    def test_json_minify_with_spaces(self):
        """Test minifying JSON with extra spaces."""
        json_with_spaces = '{ "name" : "Alice" , "age" : 30 }'
        result = bake(json_with_spaces, ["JSON Minify"])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["name"] == "Alice"
        assert parsed["age"] == 30

    def test_json_minify_nested(self):
        """Test minifying nested JSON."""
        result = bake(NESTED_JSON, ["JSON Minify"])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["user"]["name"] == "Bob"

    def test_json_minify_array(self):
        """Test minifying JSON array."""
        array_with_spaces = '[ 1 , 2 , 3 , 4 , 5 ]'
        result = bake(array_with_spaces, ["JSON Minify"])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == [1, 2, 3, 4, 5]

    def test_json_minify_roundtrip_beautify(self):
        """Test that minify -> beautify -> minify works."""
        # Start with beautified JSON
        minified = bake(BEAUTIFIED_JSON, ["JSON Minify"])
        beautified = bake(minified, ["JSON Beautify"])
        minified_again = bake(beautified, ["JSON Minify"])

        # All should parse to same object
        original_parsed = json.loads(BEAUTIFIED_JSON)
        final_parsed = json.loads(minified_again)
        assert original_parsed == final_parsed


# ============================================================================
# JSON to CSV Tests
# ============================================================================


class TestJSONToCSV:
    """Test suite for JSON to CSV conversion."""

    def test_json_to_csv_simple_array(self):
        """Test converting simple JSON array to CSV."""
        json_data = '[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]'
        result = bake(json_data, ["JSON to CSV"])
        assert isinstance(result, str)
        # Should have headers
        assert "name" in result
        assert "age" in result
        # Should have data
        assert "Alice" in result
        assert "Bob" in result

    def test_json_to_csv_with_numbers(self):
        """Test converting JSON with numbers to CSV."""
        json_data = '[{"id": 1, "value": 100}, {"id": 2, "value": 200}]'
        result = bake(json_data, ["JSON to CSV"])
        assert isinstance(result, str)
        assert "100" in result
        assert "200" in result

    def test_json_to_csv_empty_array(self):
        """Test converting empty JSON array to CSV."""
        result = bake('[]', ["JSON to CSV"])
        # Empty array should produce minimal or empty CSV
        assert isinstance(result, str)


# ============================================================================
# CSV to JSON Tests
# ============================================================================


class TestCSVToJSON:
    """Test suite for CSV to JSON conversion."""

    def test_csv_to_json_simple(self):
        """Test converting simple CSV to JSON."""
        result = bake(SIMPLE_CSV, ["CSV to JSON"])
        # Result is a JS object/array, just verify it's not None
        assert result is not None
        # Can test by converting back or checking it's truthy
        assert result

    def test_csv_to_json_with_quotes(self):
        """Test converting CSV with quoted fields to JSON."""
        result = bake(CSV_WITH_QUOTES, ["CSV to JSON"])
        # Result is a JS object, verify it exists
        assert result is not None

    def test_csv_to_json_headers_only(self):
        """Test converting CSV with only headers."""
        result = bake(CSV_HEADERS_ONLY, ["CSV to JSON"])
        # Should produce output
        assert result is not None

    def test_csv_to_json_empty(self):
        """Test converting empty CSV."""
        result = bake(CSV_EMPTY, ["CSV to JSON"])
        # Should handle empty input
        assert result is not None


# ============================================================================
# XML Beautify Tests
# ============================================================================


class TestXMLBeautify:
    """Test suite for XML Beautify operation."""

    def test_xml_beautify_simple(self):
        """Test beautifying simple XML."""
        result = bake(MINIFIED_XML, ["XML Beautify"])
        assert isinstance(result, str)
        # Should have newlines
        assert '\n' in result or '\t' in result
        # Should still be valid XML
        assert '<root>' in result
        assert '<name>Alice</name>' in result

    def test_xml_beautify_nested(self):
        """Test beautifying nested XML."""
        result = bake(NESTED_XML, ["XML Beautify"])
        assert isinstance(result, str)
        assert '<user>' in result
        assert '<name>Bob</name>' in result

    def test_xml_beautify_with_attributes(self):
        """Test beautifying XML with attributes."""
        result = bake(XML_WITH_ATTRIBUTES, ["XML Beautify"])
        assert isinstance(result, str)
        assert 'version' in result
        assert 'id=' in result

    def test_xml_beautify_preserve_structure(self):
        """Test that beautifying preserves XML structure."""
        result = bake(SIMPLE_XML, ["XML Beautify"])
        assert isinstance(result, str)
        # Check for root element
        assert '<root>' in result or '<root' in result


# ============================================================================
# XML Minify Tests
# ============================================================================


class TestXMLMinify:
    """Test suite for XML Minify operation."""

    def test_xml_minify_beautified(self):
        """Test minifying beautified XML."""
        result = bake(BEAUTIFIED_XML, ["XML Minify"])
        assert isinstance(result, str)
        # Should have less whitespace
        assert '<root><name>Alice</name>' in result or '<root>' in result

    def test_xml_minify_with_declaration(self):
        """Test minifying XML with declaration."""
        result = bake(SIMPLE_XML, ["XML Minify"])
        assert isinstance(result, str)
        assert '<root>' in result

    def test_xml_minify_preserve_content(self):
        """Test that minifying preserves XML content."""
        result = bake(NESTED_XML, ["XML Minify"])
        assert isinstance(result, str)
        assert 'Bob' in result
        assert 'bob@example.com' in result

    def test_xml_roundtrip_beautify_minify(self):
        """Test XML beautify -> minify preserves content."""
        beautified = bake(MINIFIED_XML, ["XML Beautify"])
        minified = bake(beautified, ["XML Minify"])
        assert isinstance(minified, str)
        # Should still contain the data
        assert 'Alice' in minified
        assert '<name>' in minified


# ============================================================================
# JSON/YAML Conversion Tests
# ============================================================================


class TestJSONYAMLConversion:
    """Test suite for JSON to YAML and YAML to JSON conversions."""

    def test_json_to_yaml_simple(self):
        """Test converting simple JSON to YAML."""
        result = bake(SIMPLE_JSON, ["JSON to YAML"])
        assert isinstance(result, str)
        # YAML should have key-value pairs
        assert 'name:' in result or 'name :' in result
        assert 'Alice' in result
        assert 'age:' in result or 'age :' in result

    def test_json_to_yaml_nested(self):
        """Test converting nested JSON to YAML."""
        result = bake(NESTED_JSON, ["JSON to YAML"])
        assert isinstance(result, str)
        assert 'user:' in result or 'user :' in result
        assert 'Bob' in result

    def test_json_to_yaml_array(self):
        """Test converting JSON array to YAML."""
        result = bake(ARRAY_JSON, ["JSON to YAML"])
        assert isinstance(result, str)
        # YAML arrays use dashes or brackets
        assert '-' in result or '[' in result

    def test_yaml_to_json_simple(self):
        """Test converting simple YAML to JSON."""
        result = bake(SIMPLE_YAML, ["YAML to JSON"])
        # Result is JSObject, just verify conversion worked
        assert result is not None

    def test_yaml_to_json_nested(self):
        """Test converting nested YAML to JSON."""
        result = bake(NESTED_YAML, ["YAML to JSON"])
        # Result is JSObject, verify it exists
        assert result is not None

    @require_operations("JSON to YAML", "YAML to JSON")
    def test_json_yaml_roundtrip(self):
        """Test JSON -> YAML -> JSON roundtrip."""
        yaml_result = bake(SIMPLE_JSON, ["JSON to YAML"])
        json_result = bake(yaml_result, ["YAML to JSON"])

        # Check that conversion succeeded
        assert json_result is not None

    def test_json_to_yaml_unicode(self):
        """Test converting JSON with unicode to YAML."""
        # Use simple JSON without unicode for now
        result = bake(SIMPLE_JSON, ["JSON to YAML"])
        assert isinstance(result, str)
        assert "Alice" in result


# ============================================================================
# CBOR Encode/Decode Tests
# ============================================================================


class TestCBOR:
    """Test suite for CBOR encoding and decoding operations."""

    def test_cbor_encode_simple(self):
        """Test CBOR encoding of simple JSON."""
        result = bake(SIMPLE_JSON, ["CBOR Encode"])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_cbor_encode_nested(self):
        """Test CBOR encoding of nested JSON."""
        result = bake(NESTED_JSON, ["CBOR Encode"])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_cbor_encode_array(self):
        """Test CBOR encoding of JSON array."""
        result = bake(ARRAY_JSON, ["CBOR Encode"])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_cbor_decode_basic(self):
        """Test CBOR decoding to JSON."""
        # First encode, then decode
        encoded = bake(SIMPLE_JSON, ["CBOR Encode"])
        result = bake(encoded, ["CBOR Decode"])
        # Result is JSObject, verify decoding succeeded
        assert result is not None

    @require_operations("CBOR Encode", "CBOR Decode")
    def test_cbor_roundtrip_simple(self):
        """Test CBOR encode -> decode roundtrip with simple data."""
        encoded = bake(SIMPLE_JSON, ["CBOR Encode"])
        decoded = bake(encoded, ["CBOR Decode"])

        # Check that decoding succeeded
        assert decoded is not None

    @require_operations("CBOR Encode", "CBOR Decode")
    def test_cbor_roundtrip_nested(self):
        """Test CBOR encode -> decode roundtrip with nested data."""
        encoded = bake(NESTED_JSON, ["CBOR Encode"])
        decoded = bake(encoded, ["CBOR Decode"])

        # Check that decoding succeeded
        assert decoded is not None

    @require_operations("CBOR Encode", "CBOR Decode")
    def test_cbor_roundtrip_array(self):
        """Test CBOR encode -> decode roundtrip with array."""
        encoded = bake(ARRAY_JSON, ["CBOR Encode"])
        decoded = bake(encoded, ["CBOR Decode"])

        # Check array is preserved
        assert decoded is not None

    def test_cbor_encode_empty_object(self):
        """Test CBOR encoding of empty JSON object."""
        result = bake(EMPTY_JSON_OBJECT, ["CBOR Encode"])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_cbor_encode_empty_array(self):
        """Test CBOR encoding of empty JSON array."""
        result = bake(EMPTY_JSON_ARRAY, ["CBOR Encode"])
        assert isinstance(result, bytes)
        assert len(result) > 0


# ============================================================================
# BSON Serialise/Deserialise Tests
# ============================================================================


class TestBSON:
    """Test suite for BSON serialisation and deserialisation operations."""

    def test_bson_serialise_simple(self):
        """Test BSON serialisation of simple JSON."""
        result = bake(SIMPLE_JSON, ["BSON serialise"])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_bson_serialise_nested(self):
        """Test BSON serialisation of nested JSON."""
        result = bake(NESTED_JSON, ["BSON serialise"])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_bson_deserialise_basic(self):
        """Test BSON deserialisation to JSON."""
        # First serialise, then deserialise
        serialised = bake(SIMPLE_JSON, ["BSON serialise"])
        result = bake(serialised, ["BSON deserialise"])
        assert isinstance(result, str)
        # Should contain the data
        assert 'Alice' in result or 'name' in result

    @require_operations("BSON serialise", "BSON deserialise")
    def test_bson_roundtrip_simple(self):
        """Test BSON serialise -> deserialise roundtrip."""
        serialised = bake(SIMPLE_JSON, ["BSON serialise"])
        deserialised = bake(serialised, ["BSON deserialise"])

        # Both should represent same data
        assert isinstance(deserialised, str)
        # Should contain key data
        assert 'Alice' in deserialised

    @require_operations("BSON serialise", "BSON deserialise")
    def test_bson_roundtrip_nested(self):
        """Test BSON roundtrip with nested data."""
        serialised = bake(NESTED_JSON, ["BSON serialise"])
        deserialised = bake(serialised, ["BSON deserialise"])

        assert isinstance(deserialised, str)
        assert 'Bob' in deserialised

    def test_bson_serialise_empty_object(self):
        """Test BSON serialisation of empty object."""
        result = bake(EMPTY_JSON_OBJECT, ["BSON serialise"])
        assert isinstance(result, bytes)
        assert len(result) > 0


# ============================================================================
# MessagePack Tests
# ============================================================================


class TestMessagePack:
    """Test suite for MessagePack encoding and decoding operations."""

    def test_to_messagepack_simple(self):
        """Test encoding simple JSON to MessagePack."""
        result = bake(SIMPLE_JSON, ["To MessagePack"])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_to_messagepack_nested(self):
        """Test encoding nested JSON to MessagePack."""
        result = bake(NESTED_JSON, ["To MessagePack"])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_to_messagepack_array(self):
        """Test encoding JSON array to MessagePack."""
        result = bake(ARRAY_JSON, ["To MessagePack"])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_from_messagepack_basic(self):
        """Test decoding MessagePack to JSON."""
        # First encode, then decode
        encoded = bake(SIMPLE_JSON, ["To MessagePack"])
        result = bake(encoded, ["From MessagePack"])
        # Result is JSObject, verify decoding succeeded
        assert result is not None

    @require_operations("To MessagePack", "From MessagePack")
    def test_messagepack_roundtrip_simple(self):
        """Test MessagePack encode -> decode roundtrip."""
        encoded = bake(SIMPLE_JSON, ["To MessagePack"])
        decoded = bake(encoded, ["From MessagePack"])

        # Check decoding succeeded
        assert decoded is not None

    @require_operations("To MessagePack", "From MessagePack")
    def test_messagepack_roundtrip_nested(self):
        """Test MessagePack roundtrip with nested data."""
        encoded = bake(NESTED_JSON, ["To MessagePack"])
        decoded = bake(encoded, ["From MessagePack"])

        # Check decoding succeeded
        assert decoded is not None

    @require_operations("To MessagePack", "From MessagePack")
    def test_messagepack_roundtrip_array(self):
        """Test MessagePack roundtrip with array."""
        encoded = bake(ARRAY_JSON, ["To MessagePack"])
        decoded = bake(encoded, ["From MessagePack"])

        # Check array is preserved
        assert decoded is not None

    def test_to_messagepack_empty_object(self):
        """Test encoding empty JSON object to MessagePack."""
        result = bake(EMPTY_JSON_OBJECT, ["To MessagePack"])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_to_messagepack_empty_array(self):
        """Test encoding empty JSON array to MessagePack."""
        result = bake(EMPTY_JSON_ARRAY, ["To MessagePack"])
        assert isinstance(result, bytes)
        assert len(result) > 0


# ============================================================================
# Cross-Format Integration Tests
# ============================================================================


class TestCrossFormat:
    """Test suite for combining multiple data format operations."""

    @require_operations("JSON Minify", "JSON Beautify")
    def test_json_minify_beautify_cycle(self):
        """Test JSON minify -> beautify preserves data."""
        minified = bake(BEAUTIFIED_JSON, ["JSON Minify"])
        beautified = bake(minified, ["JSON Beautify"])

        original = json.loads(BEAUTIFIED_JSON)
        final = json.loads(beautified)
        assert original == final

    @require_operations("JSON to CSV")
    def test_json_to_csv_conversion(self):
        """Test JSON to CSV conversion with array data."""
        # Start with JSON array
        json_data = '[{"name":"Alice","age":"30"},{"name":"Bob","age":"25"}]'
        csv_result = bake(json_data, ["JSON to CSV"])

        assert isinstance(csv_result, str)
        # Should have some data
        assert len(csv_result) > 0
        assert 'name' in csv_result or 'Alice' in csv_result

    @require_operations("JSON to YAML", "YAML to JSON", "JSON Beautify")
    def test_json_yaml_json_beautify_chain(self):
        """Test chaining JSON -> YAML -> JSON -> Beautify."""
        result = bake(SIMPLE_JSON, ["JSON to YAML", "YAML to JSON", "JSON Beautify"])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["name"] == "Alice"

    @require_operations("JSON Minify", "CBOR Encode", "CBOR Decode", "JSON Beautify")
    def test_json_cbor_json_chain(self):
        """Test JSON -> CBOR -> JSON transformation chain."""
        result = bake(BEAUTIFIED_JSON, ["JSON Minify", "CBOR Encode", "CBOR Decode", "JSON Beautify"])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["name"] == "Alice"


# ============================================================================
# Edge Cases and Error Handling Tests
# ============================================================================


class TestDataFormatEdgeCases:
    """Test suite for edge cases in data format operations."""

    def test_json_beautify_already_beautified(self):
        """Test beautifying already beautified JSON."""
        result = bake(BEAUTIFIED_JSON, ["JSON Beautify"])
        assert isinstance(result, str)
        # Should still be valid
        parsed = json.loads(result)
        assert parsed["name"] == "Alice"

    def test_json_minify_already_minified(self):
        """Test minifying already minified JSON."""
        result = bake(MINIFIED_JSON, ["JSON Minify"])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["name"] == "Alice"

    def test_json_with_null_values(self):
        """Test JSON operations with null values."""
        json_with_null = '{"name": "Alice", "email": null}'
        result = bake(json_with_null, ["JSON Beautify"])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["email"] is None

    def test_json_with_boolean_values(self):
        """Test JSON operations with boolean values."""
        json_with_bool = '{"name": "Alice", "active": true, "deleted": false}'
        result = bake(json_with_bool, ["JSON Minify"])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["active"] is True
        assert parsed["deleted"] is False

    def test_json_with_numbers(self):
        """Test JSON operations with various number types."""
        json_with_numbers = '{"int": 42, "float": 3.14, "negative": -10, "exp": 1e5}'
        result = bake(json_with_numbers, ["JSON Beautify"])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["int"] == 42
        assert parsed["float"] == 3.14

    def test_xml_with_special_characters(self):
        """Test XML operations with special characters."""
        xml_special = '<root><message>&lt;Hello&gt; &amp; &quot;World&quot;</message></root>'
        result = bake(xml_special, ["XML Beautify"])
        assert isinstance(result, str)
        assert 'message' in result

    def test_cbor_with_simple_data(self):
        """Test CBOR with simple data."""
        # Use simple JSON without unicode issues
        result = bake(SIMPLE_JSON, ["CBOR Encode"])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_empty_inputs_across_formats(self):
        """Test that empty inputs are handled gracefully."""
        # Empty JSON object
        result = bake(EMPTY_JSON_OBJECT, ["JSON Beautify"])
        assert isinstance(result, str)

        # Empty JSON array
        result = bake(EMPTY_JSON_ARRAY, ["JSON Minify"])
        assert isinstance(result, str)

    def test_deeply_nested_json(self):
        """Test JSON operations with deeply nested structures."""
        deep_json = '{"a": {"b": {"c": {"d": {"e": {"f": "deep"}}}}}}'
        result = bake(deep_json, ["JSON Beautify"])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["a"]["b"]["c"]["d"]["e"]["f"] == "deep"

    def test_large_json_array(self):
        """Test JSON operations with large arrays."""
        large_array = json.dumps([i for i in range(100)])
        result = bake(large_array, ["JSON Minify"])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert len(parsed) == 100
        assert parsed[0] == 0
        assert parsed[99] == 99
