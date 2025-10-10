from ida_cyberchef.core.hex_formatter import HexFormatter


def test_format_simple_bytes():
    formatter = HexFormatter()
    result = formatter.format_hex_dump(b"Hello")

    assert "48 65 6c 6c 6f" in result
    assert "Hello" in result


def test_format_multiple_lines():
    formatter = HexFormatter()
    data = b"A" * 32
    result = formatter.format_hex_dump(data)

    lines = result.strip().split("\n")
    assert len(lines) == 2  # 16 bytes per line


def test_format_with_non_printable():
    formatter = HexFormatter()
    result = formatter.format_hex_dump(b"\x00\x01\x02")

    assert "00 01 02" in result
    assert "." in result  # Non-printable shown as dots


class TestHexStringUnspaced:
    """Tests for format_hex_string_unspaced method."""

    def test_basic_functionality(self):
        formatter = HexFormatter()
        result = formatter.format_hex_string_unspaced(b"Hello")
        assert result == "48656c6c6f"

    def test_empty_data(self):
        formatter = HexFormatter()
        result = formatter.format_hex_string_unspaced(b"")
        assert result == ""

    def test_single_byte(self):
        formatter = HexFormatter()
        result = formatter.format_hex_string_unspaced(b"\x00")
        assert result == "00"

    def test_non_printable_bytes(self):
        formatter = HexFormatter()
        result = formatter.format_hex_string_unspaced(b"\x00\x01\xff")
        assert result == "0001ff"


class TestHexStringSpaced:
    """Tests for format_hex_string_spaced method."""

    def test_basic_functionality(self):
        formatter = HexFormatter()
        result = formatter.format_hex_string_spaced(b"Hello")
        assert result == "48 65 6c 6c 6f"

    def test_empty_data(self):
        formatter = HexFormatter()
        result = formatter.format_hex_string_spaced(b"")
        assert result == ""

    def test_single_byte(self):
        formatter = HexFormatter()
        result = formatter.format_hex_string_spaced(b"\x00")
        assert result == "00"

    def test_non_printable_bytes(self):
        formatter = HexFormatter()
        result = formatter.format_hex_string_spaced(b"\x00\x01\xff")
        assert result == "00 01 ff"


class TestStringLiteral:
    """Tests for format_string_literal method."""

    def test_basic_printable_ascii(self):
        formatter = HexFormatter()
        result = formatter.format_string_literal(b"Hello")
        assert result == '"Hello"'

    def test_empty_data(self):
        formatter = HexFormatter()
        result = formatter.format_string_literal(b"")
        assert result == '""'

    def test_double_quote_escaped(self):
        formatter = HexFormatter()
        result = formatter.format_string_literal(b'Say "Hi"')
        assert result == '"Say \\"Hi\\""'

    def test_backslash_escaped(self):
        formatter = HexFormatter()
        result = formatter.format_string_literal(b"C:\\Path")
        assert result == '"C:\\\\Path"'

    def test_tab_escaped(self):
        formatter = HexFormatter()
        result = formatter.format_string_literal(b"A\tB")
        assert result == '"A\\tB"'

    def test_newline_escaped(self):
        formatter = HexFormatter()
        result = formatter.format_string_literal(b"Line1\nLine2")
        assert result == '"Line1\\nLine2"'

    def test_carriage_return_escaped(self):
        formatter = HexFormatter()
        result = formatter.format_string_literal(b"A\rB")
        assert result == '"A\\rB"'

    def test_non_printable_hex_escaped(self):
        formatter = HexFormatter()
        result = formatter.format_string_literal(b"\x00\x01\xff")
        assert result == '"\\x00\\x01\\xff"'

    def test_mixed_content(self):
        formatter = HexFormatter()
        result = formatter.format_string_literal(b'Hello\n"World"\t\x00')
        assert result == '"Hello\\n\\"World\\"\\t\\x00"'


class TestCUcharArrayHex:
    """Tests for format_c_uchar_array_hex method."""

    def test_basic_functionality(self):
        formatter = HexFormatter()
        result = formatter.format_c_uchar_array_hex(b"Hello")
        assert result == "0x48, 0x65, 0x6c, 0x6c, 0x6f"

    def test_empty_data(self):
        formatter = HexFormatter()
        result = formatter.format_c_uchar_array_hex(b"")
        assert result == ""

    def test_single_byte(self):
        formatter = HexFormatter()
        result = formatter.format_c_uchar_array_hex(b"\x00")
        assert result == "0x00"

    def test_non_printable_bytes(self):
        formatter = HexFormatter()
        result = formatter.format_c_uchar_array_hex(b"\x00\x01\xff")
        assert result == "0x00, 0x01, 0xff"

    def test_hex_formatting_lowercase(self):
        formatter = HexFormatter()
        result = formatter.format_c_uchar_array_hex(b"\xab\xcd\xef")
        assert result == "0xab, 0xcd, 0xef"


class TestCUcharArrayDecimal:
    """Tests for format_c_uchar_array_decimal method."""

    def test_basic_functionality(self):
        formatter = HexFormatter()
        result = formatter.format_c_uchar_array_decimal(b"Hello")
        assert result == "72, 101, 108, 108, 111"

    def test_empty_data(self):
        formatter = HexFormatter()
        result = formatter.format_c_uchar_array_decimal(b"")
        assert result == ""

    def test_single_byte(self):
        formatter = HexFormatter()
        result = formatter.format_c_uchar_array_decimal(b"\x00")
        assert result == "0"

    def test_non_printable_bytes(self):
        formatter = HexFormatter()
        result = formatter.format_c_uchar_array_decimal(b"\x00\x01\xff")
        assert result == "0, 1, 255"

    def test_max_byte_value(self):
        formatter = HexFormatter()
        result = formatter.format_c_uchar_array_decimal(b"\xff")
        assert result == "255"


class TestCInitializedVariable:
    """Tests for format_c_initialized_variable method."""

    def test_basic_functionality(self):
        formatter = HexFormatter()
        result = formatter.format_c_initialized_variable(b"Hello")
        assert "unsigned char data[5] = {" in result
        assert "0x48, 0x65, 0x6c, 0x6c, 0x6f" in result
        assert result.endswith("};")

    def test_empty_data(self):
        formatter = HexFormatter()
        result = formatter.format_c_initialized_variable(b"")
        assert result == "unsigned char data[] = {};"

    def test_single_byte(self):
        formatter = HexFormatter()
        result = formatter.format_c_initialized_variable(b"\x00")
        expected = "unsigned char data[1] = {\n    0x00\n};"
        assert result == expected

    def test_multiline_12_per_line(self):
        formatter = HexFormatter()
        data = bytes(range(25))
        result = formatter.format_c_initialized_variable(data)

        lines = result.split("\n")
        assert lines[0] == "unsigned char data[25] = {"
        assert lines[-1] == "};"

        first_data_line = lines[1]
        assert first_data_line.startswith("    ")
        assert first_data_line.count("0x") == 12
        assert first_data_line.endswith(",")

        second_data_line = lines[2]
        assert second_data_line.startswith("    ")
        assert second_data_line.count("0x") == 12
        assert second_data_line.endswith(",")

        third_data_line = lines[3]
        assert third_data_line.startswith("    ")
        assert third_data_line.count("0x") == 1
        assert not third_data_line.endswith(",")

    def test_exactly_12_bytes(self):
        formatter = HexFormatter()
        data = b"A" * 12
        result = formatter.format_c_initialized_variable(data)

        lines = result.split("\n")
        assert len(lines) == 3
        assert lines[0] == "unsigned char data[12] = {"
        assert not lines[1].endswith(",")
        assert lines[2] == "};"

    def test_13_bytes_creates_two_lines(self):
        formatter = HexFormatter()
        data = b"A" * 13
        result = formatter.format_c_initialized_variable(data)

        lines = result.split("\n")
        assert len(lines) == 4
        assert lines[0] == "unsigned char data[13] = {"
        assert lines[1].endswith(",")
        assert not lines[2].endswith(",")
        assert lines[3] == "};"

    def test_indentation(self):
        formatter = HexFormatter()
        result = formatter.format_c_initialized_variable(b"Hello")

        lines = result.split("\n")
        for line in lines[1:-1]:
            assert line.startswith("    ")

    def test_hex_formatting_lowercase(self):
        formatter = HexFormatter()
        result = formatter.format_c_initialized_variable(b"\xab\xcd\xef")
        assert "0xab" in result
        assert "0xcd" in result
        assert "0xef" in result
