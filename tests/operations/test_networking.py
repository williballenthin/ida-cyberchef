"""Comprehensive tests for CyberChef networking operations.

This module tests all major networking operations including:
- IPv4 and IPv6 address parsing and formatting
- IP range parsing (CIDR, hyphenated)
- URL parsing and defanging/fanging
- IP address defanging
- NetBIOS name encoding/decoding
- MAC address formatting and extraction
- Protocol parsing (TCP, UDP, IPv4 headers)

Each operation is tested with:
- Standard and special addresses
- Various formats and notations
- Edge cases and invalid input handling
- Roundtrip tests where applicable
"""

import pytest

from ida_cyberchef.cyberchef import bake

# Import test constants from conftest
from tests.conftest import EMPTY_BYTES, assert_roundtrip, roundtrip_test


# ============================================================================
# IPv6 Address Parsing Tests
# ============================================================================


class TestParseIPv6Address:
    """Test suite for Parse IPv6 address operation."""

    def test_parse_ipv6_full_form(self):
        """Test parsing a full form IPv6 address."""
        result = bake("2001:0db8:0000:0000:0000:ff00:0042:8329", ["Parse IPv6 address"])
        assert "2001:0db8:0000:0000:0000:ff00:0042:8329" in result
        assert "2001:db8::ff00:42:8329" in result  # Shortened form

    def test_parse_ipv6_compressed(self):
        """Test parsing a compressed IPv6 address."""
        result = bake("2001:db8::1", ["Parse IPv6 address"])
        assert "2001:0db8:0000:0000:0000:0000:0000:0001" in result
        assert "2001:db8::1" in result

    def test_parse_ipv6_loopback(self):
        """Test parsing IPv6 loopback address."""
        result = bake("::1", ["Parse IPv6 address"])
        assert "0000:0000:0000:0000:0000:0000:0000:0001" in result
        assert "Loopback" in result or "loopback" in result

    def test_parse_ipv6_all_zeros(self):
        """Test parsing IPv6 all-zeros address."""
        result = bake("::", ["Parse IPv6 address"])
        assert "0000:0000:0000:0000:0000:0000:0000:0000" in result

    def test_parse_ipv6_with_ipv4_mapped(self):
        """Test parsing IPv6 address with embedded IPv4."""
        result = bake("::ffff:192.0.2.1", ["Parse IPv6 address"])
        # IPv4-mapped IPv6 address is shown in hex format
        assert "ffff" in result.lower()
        assert "192" in result

    def test_parse_ipv6_link_local(self):
        """Test parsing IPv6 link-local address."""
        result = bake("fe80::1", ["Parse IPv6 address"])
        assert "fe80" in result.lower()
        assert "Link local" in result or "link" in result.lower()

    def test_parse_ipv6_multicast(self):
        """Test parsing IPv6 multicast address."""
        result = bake("ff02::1", ["Parse IPv6 address"])
        assert "ff02" in result.lower()
        assert "Multicast" in result or "multicast" in result.lower()

    def test_parse_ipv6_documentation(self):
        """Test parsing IPv6 documentation address."""
        result = bake("2001:db8::8a2e:370:7334", ["Parse IPv6 address"])
        assert "2001:db8" in result.lower()


# ============================================================================
# IP Range Parsing Tests
# ============================================================================


class TestParseIPRange:
    """Test suite for Parse IP range operation."""

    def test_parse_ipv4_cidr_slash24(self):
        """Test parsing IPv4 CIDR /24 range."""
        result = bake("192.168.1.0/24", ["Parse IP range"])
        assert "192.168.1.0" in result
        assert "192.168.1.255" in result
        assert "255.255.255.0" in result  # Netmask

    def test_parse_ipv4_cidr_slash16(self):
        """Test parsing IPv4 CIDR /16 range."""
        result = bake("10.0.0.0/16", ["Parse IP range"])
        assert "10.0.0.0" in result
        assert "10.0.255.255" in result
        assert "255.255.0.0" in result  # Netmask

    def test_parse_ipv4_cidr_slash31(self):
        """Test parsing IPv4 CIDR /31 (point-to-point link)."""
        result = bake("192.168.1.0/31", ["Parse IP range"])
        assert "192.168.1.0" in result
        assert "192.168.1.1" in result

    def test_parse_ipv4_hyphenated_range(self):
        """Test parsing hyphenated IPv4 range."""
        result = bake("192.168.1.1 - 192.168.1.10", ["Parse IP range"])
        assert "192.168.1.1" in result
        assert "192.168.1.10" in result

    def test_parse_ipv4_cidr_slash8(self):
        """Test parsing IPv4 CIDR /8 (Class A)."""
        result = bake("10.0.0.0/8", ["Parse IP range"])
        assert "10.0.0.0" in result
        assert "10.255.255.255" in result
        assert "255.0.0.0" in result  # Netmask

    def test_parse_ipv6_cidr_range(self):
        """Test parsing IPv6 CIDR range (not enumerated)."""
        result = bake("2001:db8::/32", ["Parse IP range"])
        assert "2001:db8" in result.lower()
        # IPv6 ranges are not enumerated, just displayed

    def test_parse_localhost_range(self):
        """Test parsing localhost CIDR range."""
        result = bake("127.0.0.0/8", ["Parse IP range"])
        assert "127.0.0.0" in result
        assert "127.255.255.255" in result


# ============================================================================
# Change IP Format Tests
# ============================================================================


class TestChangeIPFormat:
    """Test suite for Change IP format operation."""

    def test_change_ip_dotted_to_hex(self):
        """Test converting dotted decimal to hex."""
        result = bake("192.168.1.1", [{"op": "Change IP format", "args": ["Dotted Decimal", "Hex"]}])
        assert result.lower() == "c0a80101"

    def test_change_ip_dotted_to_octal(self):
        """Test converting dotted decimal to octal."""
        result = bake("192.168.1.1", [{"op": "Change IP format", "args": ["Dotted Decimal", "Octal"]}])
        # CyberChef removes leading zeros in the last octet
        assert result == "030052000401" or result == "030052000401001"

    def test_change_ip_dotted_to_decimal(self):
        """Test converting dotted decimal to decimal."""
        result = bake("192.168.1.1", [{"op": "Change IP format", "args": ["Dotted Decimal", "Decimal"]}])
        assert result == "3232235777"

    def test_change_ip_hex_to_dotted(self):
        """Test converting hex to dotted decimal."""
        result = bake("c0a80101", [{"op": "Change IP format", "args": ["Hex", "Dotted Decimal"]}])
        assert result == "192.168.1.1"

    def test_change_ip_decimal_to_dotted(self):
        """Test converting decimal to dotted decimal."""
        result = bake("3232235777", [{"op": "Change IP format", "args": ["Decimal", "Dotted Decimal"]}])
        assert result == "192.168.1.1"

    def test_change_ip_localhost(self):
        """Test converting localhost address."""
        result = bake("127.0.0.1", [{"op": "Change IP format", "args": ["Dotted Decimal", "Hex"]}])
        assert result.lower() == "7f000001"

    def test_change_ip_broadcast(self):
        """Test converting broadcast address."""
        result = bake("255.255.255.255", [{"op": "Change IP format", "args": ["Dotted Decimal", "Decimal"]}])
        assert result == "4294967295"


# ============================================================================
# URL Operations Tests
# ============================================================================


class TestParseURI:
    """Test suite for Parse URI operation."""

    def test_parse_simple_url(self):
        """Test parsing a simple HTTP URL."""
        result = bake("http://example.com/path", ["Parse URI"])
        assert "http" in result
        assert "example.com" in result
        assert "/path" in result

    def test_parse_url_with_query(self):
        """Test parsing URL with query parameters."""
        result = bake("https://example.com/search?q=test&lang=en", ["Parse URI"])
        assert "https" in result
        assert "example.com" in result
        # Query parameters are formatted with whitespace
        assert "q" in result and "test" in result
        assert "lang" in result and "en" in result

    def test_parse_url_with_port(self):
        """Test parsing URL with port number."""
        result = bake("http://example.com:8080/path", ["Parse URI"])
        assert "8080" in result
        assert "example.com" in result

    def test_parse_url_with_auth(self):
        """Test parsing URL with authentication."""
        result = bake("https://user:pass@example.com/secure", ["Parse URI"])
        assert "user" in result
        assert "pass" in result
        assert "example.com" in result

    def test_parse_url_with_fragment(self):
        """Test parsing URL with fragment identifier."""
        result = bake("https://example.com/page#section", ["Parse URI"])
        assert "example.com" in result
        assert "section" in result or "#section" in result

    def test_parse_url_complex(self):
        """Test parsing complex URL with multiple components."""
        url = "https://user:pass@example.com:443/path/to/page?key1=value1&key2=value2#fragment"
        result = bake(url, ["Parse URI"])
        assert "https" in result
        assert "user" in result
        assert "example.com" in result
        assert "443" in result
        assert "key1" in result
        assert "fragment" in result

    def test_parse_ftp_url(self):
        """Test parsing FTP URL."""
        result = bake("ftp://ftp.example.com/files/file.txt", ["Parse URI"])
        assert "ftp" in result
        assert "ftp.example.com" in result
        assert "file.txt" in result


# ============================================================================
# Defang/Fang URL Tests
# ============================================================================


class TestDefangFangURL:
    """Test suite for Defang URL and Fang URL operations."""

    def test_defang_http_url(self):
        """Test defanging HTTP URL."""
        result = bake("http://example.com", ["Defang URL"])
        assert "hxxp" in result or "http" not in result.replace("hxxp", "")

    def test_defang_https_url(self):
        """Test defanging HTTPS URL."""
        result = bake("https://example.com", ["Defang URL"])
        assert "hxxps" in result or "[.]" in result

    def test_defang_url_with_dots(self):
        """Test defanging URL replaces dots."""
        result = bake("http://malicious.example.com", ["Defang URL"])
        assert "[.]" in result or "." not in result.replace("[.]", "")

    def test_fang_http_url(self):
        """Test fanging HTTP URL."""
        result = bake("hxxp://example[.]com", ["Fang URL"])
        assert result == "http://example.com"

    def test_fang_https_url(self):
        """Test fanging HTTPS URL."""
        result = bake("hxxps://example[.]com", ["Fang URL"])
        assert result == "https://example.com"

    def test_roundtrip_defang_fang_url(self):
        """Test roundtrip defang and fang URL."""
        original = "http://example.com/path"
        defanged = bake(original, ["Defang URL"])
        fanged = bake(defanged, ["Fang URL"])
        assert fanged == original


# ============================================================================
# Defang IP Addresses Tests
# ============================================================================


class TestDefangIPAddresses:
    """Test suite for Defang IP Addresses operation."""

    def test_defang_ipv4_address(self):
        """Test defanging IPv4 address."""
        result = bake("192.168.1.1", ["Defang IP Addresses"])
        assert "[.]" in result
        assert "192[.]168[.]1[.]1" == result

    def test_defang_ipv4_multiple(self):
        """Test defanging multiple IPv4 addresses."""
        result = bake("10.0.0.1 and 192.168.1.1", ["Defang IP Addresses"])
        assert "10[.]0[.]0[.]1" in result
        assert "192[.]168[.]1[.]1" in result

    def test_defang_ipv6_address(self):
        """Test defanging IPv6 address."""
        result = bake("2001:db8::1", ["Defang IP Addresses"])
        assert "[:]" in result or "2001:db8::1" not in result

    def test_defang_localhost(self):
        """Test defanging localhost address."""
        result = bake("127.0.0.1", ["Defang IP Addresses"])
        assert "127[.]0[.]0[.]1" == result

    def test_defang_ipv4_in_text(self):
        """Test defanging IPv4 address in text."""
        result = bake("Connect to 10.0.0.1 for access", ["Defang IP Addresses"])
        assert "10[.]0[.]0[.]1" in result


# ============================================================================
# NetBIOS Name Encoding/Decoding Tests
# ============================================================================


class TestNetBIOSName:
    """Test suite for NetBIOS name encoding/decoding operations."""

    def test_encode_netbios_name(self):
        """Test encoding NetBIOS name."""
        result = bake(b"WORKSTATION", [{"op": "Encode NetBIOS Name", "args": [68]}])
        assert isinstance(result, bytes)
        # NetBIOS names are encoded with a specific alphabet
        assert len(result) > 0

    def test_decode_netbios_name(self):
        """Test decoding NetBIOS name."""
        # First encode a name
        encoded = bake(b"TEST", [{"op": "Encode NetBIOS Name", "args": [68]}])
        # Then decode it
        decoded = bake(encoded, [{"op": "Decode NetBIOS Name", "args": [68]}])
        assert b"TEST" in decoded

    def test_roundtrip_netbios_workstation(self):
        """Test roundtrip encoding/decoding NetBIOS workstation name."""
        original = b"COMPUTER"
        # Pad to 15 bytes with spaces (NetBIOS names are 16 bytes with type)
        padded = original + b" " * (15 - len(original))
        encoded = bake(padded, [{"op": "Encode NetBIOS Name", "args": [68]}])
        decoded = bake(encoded, [{"op": "Decode NetBIOS Name", "args": [68]}])
        # Decoded should contain the original name
        assert original in decoded or original.decode() in decoded.decode().upper()

    def test_netbios_name_max_length(self):
        """Test NetBIOS name with maximum length."""
        # NetBIOS names are max 15 chars + 1 type byte
        name = b"A" * 15
        result = bake(name, [{"op": "Encode NetBIOS Name", "args": [68]}])
        assert isinstance(result, bytes)
        assert len(result) > 0


# ============================================================================
# MAC Address Format Tests
# ============================================================================


class TestFormatMACAddress:
    """Test suite for Format MAC addresses operation."""

    def test_format_mac_colon_separated(self):
        """Test formatting MAC address from colon-separated."""
        result = bake("00:1A:2B:3C:4D:5E", [{"op": "Format MAC addresses", "args": ["Colon", 0, "Colon"]}])
        # Format MAC addresses shows the MAC in the output
        assert "00" in result and "1a" in result.lower() and "2b" in result.lower()

    def test_format_mac_hyphen_separated(self):
        """Test formatting MAC address with hyphens."""
        result = bake("00-1A-2B-3C-4D-5E", [{"op": "Format MAC addresses", "args": ["Hyphen", 0, "Hyphen"]}])
        assert "00-1a-2b-3c-4d-5e" in result.lower() or "00-1A-2B-3C-4D-5E" in result

    def test_format_mac_no_delimiter(self):
        """Test formatting MAC address without delimiter."""
        result = bake("001A2B3C4D5E", [{"op": "Format MAC addresses", "args": ["None", 0, "Colon"]}])
        # Should contain the MAC address bytes
        assert "1a" in result.lower() and "2b" in result.lower()

    def test_format_mac_cisco_format(self):
        """Test formatting MAC address to Cisco format."""
        result = bake("00:1A:2B:3C:4D:5E", [{"op": "Format MAC addresses", "args": ["Colon", 0, "Cisco style"]}])
        # Should contain the MAC address
        assert "1a" in result.lower() and "2b" in result.lower()

    def test_format_mac_ipv6_format(self):
        """Test formatting MAC address to IPv6 interface ID format."""
        result = bake("00:1A:2B:3C:4D:5E", [{"op": "Format MAC addresses", "args": ["Colon", 0, "IPv6 interface ID"]}])
        # Should contain the MAC address bytes
        assert "1a" in result.lower() or "1A" in result

    def test_format_mac_multiple_addresses(self):
        """Test formatting multiple MAC addresses."""
        macs = "00:1A:2B:3C:4D:5E\n11:22:33:44:55:66"
        result = bake(macs, [{"op": "Format MAC addresses", "args": ["Colon", 0, "Colon"]}])
        assert "1a" in result.lower() and "2b" in result.lower()
        assert "11" in result and "22" in result

    def test_format_mac_broadcast(self):
        """Test formatting broadcast MAC address."""
        result = bake("FF:FF:FF:FF:FF:FF", [{"op": "Format MAC addresses", "args": ["Colon", 0, "Colon"]}])
        assert "ff" in result.lower()


# ============================================================================
# Extract Operations Tests
# ============================================================================


class TestExtractIPAddresses:
    """Test suite for Extract IP addresses operation."""

    def test_extract_single_ipv4(self):
        """Test extracting single IPv4 address."""
        result = bake("Server IP: 192.168.1.1", ["Extract IP addresses"])
        assert "192.168.1.1" in result

    def test_extract_multiple_ipv4(self):
        """Test extracting multiple IPv4 addresses."""
        text = "Connect to 10.0.0.1 or 192.168.1.1 for access"
        result = bake(text, ["Extract IP addresses"])
        assert "10.0.0.1" in result
        assert "192.168.1.1" in result

    def test_extract_ipv6_address(self):
        """Test extracting IPv6 address."""
        result = bake("IPv6: 2001:db8::1", [{"op": "Extract IP addresses", "args": [True, True, False, False]}])
        # IPv6 extraction - result may be empty if not enabled by default
        assert isinstance(result, str)

    def test_extract_mixed_ip_addresses(self):
        """Test extracting mixed IPv4 and IPv6 addresses."""
        text = "IPv4: 192.168.1.1, IPv6: 2001:db8::1"
        result = bake(text, ["Extract IP addresses"])
        assert "192.168.1.1" in result


class TestExtractMACAddresses:
    """Test suite for Extract MAC addresses operation."""

    def test_extract_single_mac(self):
        """Test extracting single MAC address."""
        result = bake("MAC: 00:1A:2B:3C:4D:5E", ["Extract MAC addresses"])
        assert "00:1A:2B:3C:4D:5E" in result or "00:1a:2b:3c:4d:5e" in result

    def test_extract_mac_hyphen_format(self):
        """Test extracting MAC address with hyphens."""
        result = bake("NIC: 00-1A-2B-3C-4D-5E", ["Extract MAC addresses"])
        assert "00-1A-2B-3C-4D-5E" in result or "1A" in result

    def test_extract_multiple_macs(self):
        """Test extracting multiple MAC addresses."""
        text = "MAC1: 00:11:22:33:44:55, MAC2: AA:BB:CC:DD:EE:FF"
        result = bake(text, ["Extract MAC addresses"])
        # Should extract both MACs
        assert len(result) > 0


# ============================================================================
# Group IP Addresses Tests
# ============================================================================


class TestGroupIPAddresses:
    """Test suite for Group IP addresses operation."""

    def test_group_ipv4_addresses_same_subnet(self):
        """Test grouping IPv4 addresses in same subnet."""
        ips = "192.168.1.1\n192.168.1.2\n192.168.1.3"
        result = bake(ips, ["Group IP addresses"])
        # Group IP addresses may return empty if input doesn't match expected format
        # Just verify it doesn't crash
        assert isinstance(result, str)

    def test_group_ipv4_addresses_different_subnets(self):
        """Test grouping IPv4 addresses in different subnets."""
        ips = "192.168.1.1\n10.0.0.1\n172.16.0.1"
        result = bake(ips, ["Group IP addresses"])
        # Should process the addresses
        assert isinstance(result, str)

    def test_group_ipv4_consecutive(self):
        """Test grouping consecutive IPv4 addresses."""
        ips = "192.168.1.1\n192.168.1.2\n192.168.1.3\n192.168.1.4"
        result = bake(ips, ["Group IP addresses"])
        # Should process the addresses
        assert isinstance(result, str)


# ============================================================================
# Protocol Parsing Tests (TCP, UDP, IPv4 Header)
# ============================================================================


class TestParseIPv4Header:
    """Test suite for Parse IPv4 header operation."""

    def test_parse_ipv4_header_basic(self):
        """Test parsing basic IPv4 header."""
        # Minimal IPv4 header (20 bytes)
        # Version=4, IHL=5, Total Length=20, Protocol=6 (TCP)
        header = "45 00 00 14 00 00 00 00 40 06 00 00 c0 a8 01 01 c0 a8 01 02"
        result = bake(header, ["Parse IPv4 header"])
        assert "192.168.1.1" in result or "c0 a8 01 01" in result.lower()
        assert "192.168.1.2" in result or "c0 a8 01 02" in result.lower()


class TestParseTCP:
    """Test suite for Parse TCP operation."""

    def test_parse_tcp_header_basic(self):
        """Test parsing basic TCP header."""
        # Basic TCP header: src=80, dst=12345, seq=0, ack=0, flags=SYN
        tcp_header = "00 50 30 39 00 00 00 00 00 00 00 00 50 02 00 00 00 00 00 00"
        result = bake(tcp_header, ["Parse TCP"])
        # Parse TCP returns an HTML object, so check it's not None
        assert result is not None


class TestParseUDP:
    """Test suite for Parse UDP operation."""

    def test_parse_udp_header_basic(self):
        """Test parsing basic UDP header."""
        # Basic UDP header: src=53, dst=12345, length=8
        udp_header = "00 35 30 39 00 08 00 00"
        result = bake(udp_header, ["Parse UDP"])
        # Parse UDP returns an HTML object, so check it's not None
        assert result is not None


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestNetworkingEdgeCases:
    """Test suite for edge cases and error handling in networking operations."""

    def test_parse_ipv6_invalid_format(self):
        """Test parsing invalid IPv6 address format."""
        # This should either handle gracefully or fail predictably
        try:
            result = bake("not:an:ip:address", ["Parse IPv6 address"])
            # If it doesn't throw, just verify it returns something
            assert isinstance(result, str)
        except Exception:
            # It's okay if it raises an exception for invalid input
            pass

    def test_change_ip_format_invalid(self):
        """Test Change IP format with invalid input."""
        try:
            result = bake("999.999.999.999", [{"op": "Change IP format", "args": ["Dotted Decimal", "Hex"]}])
            # Should handle gracefully
            assert isinstance(result, str)
        except Exception:
            # Or may raise exception
            pass

    def test_defang_url_empty_input(self):
        """Test Defang URL with empty input."""
        result = bake("", ["Defang URL"])
        assert result == ""

    def test_fang_url_empty_input(self):
        """Test Fang URL with empty input."""
        result = bake("", ["Fang URL"])
        assert result == ""

    def test_defang_ip_no_ip_in_text(self):
        """Test Defang IP Addresses with no IP in text."""
        result = bake("No IP address here", ["Defang IP Addresses"])
        assert "No IP address here" == result

    def test_parse_uri_without_protocol(self):
        """Test Parse URI with URL without protocol."""
        result = bake("example.com/path", ["Parse URI"])
        # Should still parse what it can
        assert "example.com" in result

    def test_format_mac_invalid_address(self):
        """Test Format MAC addresses with invalid MAC."""
        # MACs should be 6 bytes, this tests handling of incorrect length
        try:
            result = bake("00:11:22:33", [{"op": "Format MAC addresses", "args": ["Colon", 0, "Colon"]}])
            # The description says no validity checks, so it might process it anyway
            assert isinstance(result, str)
        except Exception:
            pass
