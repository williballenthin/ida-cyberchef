"""Tests for operation documentation formatting."""

from ida_cyberchef.core.operation_doc_formatter import (
    format_operation_docs,
    strip_html_tags,
)


def test_format_operation_docs_full():
    """Test formatting operation with all fields."""
    operation = {
        "name": "AES Decrypt",
        "category": "Encryption / Encoding",
        "description": "Advanced Encryption Standard (AES) decryption.",
        "args": [
            {"name": "Key", "type": "string", "value": ""},
            {"name": "IV", "type": "string", "value": ""},
            {
                "name": "Mode",
                "type": "option",
                "value": ["CBC", "ECB"],
                "toggleValues": ["CBC", "ECB"],
            },
        ],
    }

    result = format_operation_docs(operation)

    assert "AES Decrypt" in result
    assert "Category: Encryption / Encoding" in result
    assert "Advanced Encryption Standard" in result
    assert "Parameters:" in result
    assert "Key (string)" in result
    assert "Mode (option)" in result
    assert "CBC, ECB" in result


def test_format_operation_docs_minimal():
    """Test formatting operation with minimal fields."""
    operation = {
        "name": "XOR",
        "category": "Encryption / Encoding",
        "description": "XOR operation.",
        "args": [],
    }

    result = format_operation_docs(operation)

    assert "XOR" in result
    assert "Category: Encryption / Encoding" in result
    assert "XOR operation." in result
    assert "Parameters: None" in result


def test_strip_html_tags_basic():
    """Test stripping basic HTML tags."""
    assert strip_html_tags("<b>bold</b> text") == "bold text"
    assert strip_html_tags("<code>code</code>") == "code"
    assert strip_html_tags("<strong>strong</strong>") == "strong"
    assert strip_html_tags("<i>italic</i>") == "italic"
    assert strip_html_tags("<u>underline</u>") == "underline"


def test_strip_html_tags_br_conversion():
    """Test <br> tag conversion to newlines."""
    assert strip_html_tags("line1<br>line2") == "line1\nline2"
    assert strip_html_tags("line1<BR>line2") == "line1\nline2"
    assert strip_html_tags("line1<br/>line2") == "line1\nline2"
    assert strip_html_tags("line1<br />line2") == "line1\nline2"
    assert strip_html_tags("line1<br><br>line2") == "line1\n\nline2"


def test_strip_html_tags_complex():
    """Test stripping complex HTML with nested tags."""
    text = "<b>Key:</b> The <code>key</code> parameter<br><br>More info"
    expected = "Key: The key parameter\n\nMore info"
    assert strip_html_tags(text) == expected


def test_strip_html_tags_lists():
    """Test stripping list HTML tags."""
    text = "<ul><li>item1</li><li>item2</li></ul>"
    assert strip_html_tags(text) == "item1item2"


def test_strip_html_tags_links():
    """Test stripping anchor tags but keeping text."""
    text = "<a href='http://example.com'>link text</a>"
    assert strip_html_tags(text) == "link text"


def test_format_operation_docs_with_html():
    """Test formatting operation with HTML in description."""
    operation = {
        "name": "A1Z26 Cipher Decode",
        "category": "Encryption / Encoding",
        "description": "Converts alphabet order numbers into their corresponding  alphabet character.<br><br>e.g. <code>1</code> becomes <code>a</code> and <code>2</code> becomes <code>b</code>.",
        "args": [],
    }

    result = format_operation_docs(operation)

    assert "A1Z26 Cipher Decode" in result
    assert "Category: Encryption / Encoding" in result
    assert "<br>" not in result
    assert "<code>" not in result
    assert "</code>" not in result
    assert "1 becomes a" in result
    assert "2 becomes b" in result
    assert result.count("\n\n") >= 2


def test_format_operation_docs_with_complex_html():
    """Test formatting operation with complex HTML description."""
    operation = {
        "name": "AES Decrypt",
        "category": "Encryption / Encoding",
        "description": "<b>Key:</b> The following algorithms will be used based on the size of the key:<ul><li>16 bytes = AES-128</li><li>24 bytes = AES-192</li></ul><br><br><b>IV:</b> The Initialization Vector should be 16 bytes long.",
        "args": [],
    }

    result = format_operation_docs(operation)

    assert "AES Decrypt" in result
    assert "<b>" not in result
    assert "</b>" not in result
    assert "<ul>" not in result
    assert "<li>" not in result
    assert "</li>" not in result
    assert "</ul>" not in result
    assert "Key:" in result
    assert "16 bytes = AES-128" in result
    assert "24 bytes = AES-192" in result
    assert "IV:" in result
    assert "Initialization Vector" in result
