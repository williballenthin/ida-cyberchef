# Test Implementation Plan

## Overview
- **Total Operations:** 445
- **Currently Tested:** 70 (15.7%)
- **Target:** Systematic expansion prioritizing importance and feasibility
- **Phase Duration:** 10-15 minutes each (suitable for subagent implementation)

---

## Phase 1: Simple Ciphers (High Priority, Easy)
**Category:** Encryption / Encoding
**Rationale:** Core security operations, deterministic, no external dependencies

| Operation | Test File | Notes |
|-----------|-----------|-------|
| Bacon Cipher Encode/Decode | `encryption/bacon.json` | Binary encoding of text |
| Bifid Cipher Encode/Decode | `encryption/bifid.json` | Grid-based cipher |
| Rail Fence Cipher Encode/Decode | `encryption/rail_fence.json` | Transposition cipher |
| Caesar Box Cipher | `encryption/caesar_box.json` | Simple transposition |
| Substitute | `encryption/substitute.json` | Character substitution |

**Test cases per file:** 4-6 (encode, decode, edge cases, empty input)

---

## Phase 2: Morse Code & Simple Encodings
**Category:** Encryption / Encoding
**Rationale:** Well-defined standards, easy test vectors

| Operation | Test File | Notes |
|-----------|-----------|-------|
| To Morse Code | `encryption/morse.json` | ITU standard |
| From Morse Code | `encryption/morse.json` | Same file, both directions |
| Cetacean Cipher Encode/Decode | `encryption/cetacean.json` | Whale-speak encoding |
| Citrix CTX1 Encode/Decode | `encryption/citrix_ctx1.json` | Citrix password encoding |

---

## Phase 3: Remaining Hashing Operations
**Category:** Hashing
**Rationale:** Critical for integrity verification, have RFC/standard test vectors

| Operation | Test File | Notes |
|-----------|-----------|-------|
| MD2, MD4 | `hashing/md2_md4.json` | Legacy hashes, RFC 1319/1320 |
| SHA0 | `hashing/sha0.json` | Historical SHA |
| Keccak | `hashing/keccak.json` | SHA-3 foundation |
| Shake | `hashing/shake.json` | Extendable output |
| SM3 | `hashing/sm3.json` | Chinese standard |
| Snefru | `hashing/snefru.json` | Merkle hash |
| Streebog | `hashing/streebog.json` | Russian GOST hash |

---

## Phase 4: More Hashing (Part 2)
**Category:** Hashing
**Rationale:** Fuzzy hashing and specialized checksums

| Operation | Test File | Notes |
|-----------|-----------|-------|
| SSDEEP / CTPH | `hashing/fuzzy_hash.json` | Fuzzy hashing |
| Compare SSDEEP/CTPH | `hashing/fuzzy_hash.json` | Similarity comparison |
| MurmurHash3 | `hashing/murmurhash.json` | Non-cryptographic hash |
| LM Hash / NT Hash | `hashing/windows_hash.json` | Windows password hashes |
| XOR Checksum | `hashing/xor_checksum.json` | Simple checksum |
| Luhn Checksum | `hashing/luhn.json` | Credit card validation |

---

## Phase 5: Language Operations (Zero Coverage Category)
**Category:** Language
**Rationale:** 0% coverage, simple text transformations, quick wins

| Operation | Test File | Notes |
|-----------|-----------|-------|
| Convert Leet Speak | `language/leet_speak.json` | Text to 1337 and back |
| Convert to NATO alphabet | `language/nato.json` | A → Alpha, B → Bravo |
| Remove Diacritics | `language/diacritics.json` | café → cafe |
| Unicode Text Format | `language/unicode_format.json` | Styled text (bold, italic) |

---

## Phase 6: Date/Time Operations
**Category:** Date / Time
**Rationale:** Essential for log analysis, deterministic transformations

| Operation | Test File | Notes |
|-----------|-----------|-------|
| DateTime Delta | `datetime/delta.json` | Add/subtract time |
| Parse DateTime | `datetime/parse.json` | String to datetime |
| Translate DateTime Format | `datetime/translate.json` | Format conversion |
| Windows Filetime ↔ UNIX | `datetime/filetime.json` | Timestamp conversion |
| Get Time | Skip | Non-deterministic, skip |

---

## Phase 7: String Utilities (Part 1)
**Category:** Utils
**Rationale:** Common operations, pure functions

| Operation | Test File | Notes |
|-----------|-----------|-------|
| Reverse | `utils/reverse.json` | Reverse string/bytes |
| Head / Tail | `utils/head_tail.json` | First/last N items |
| Split | `utils/split.json` | Split by delimiter |
| Sort | `utils/sort.json` | Alphabetical/numeric sort |
| Unique | `utils/unique.json` | Remove duplicates |
| Filter | `utils/filter.json` | Regex filtering |

---

## Phase 8: String Utilities (Part 2)
**Category:** Utils
**Rationale:** More string operations

| Operation | Test File | Notes |
|-----------|-----------|-------|
| Count occurrences | `utils/count.json` | Pattern counting |
| Diff | `utils/diff.json` | Text comparison |
| Pad lines | `utils/pad.json` | Add padding |
| Add/Remove line numbers | `utils/line_numbers.json` | Line numbering |
| Alternating Caps | `utils/alternating_caps.json` | aLtErNaTiNg |
| Swap case | `utils/swap_case.json` | Toggle case |

---

## Phase 9: Byte Operations
**Category:** Utils
**Rationale:** Binary manipulation primitives

| Operation | Test File | Notes |
|-----------|-----------|-------|
| Drop bytes | `utils/drop_bytes.json` | Remove first N bytes |
| Take bytes | `utils/take_bytes.json` | Keep first N bytes |
| Drop nth bytes | `utils/drop_nth.json` | Every Nth byte |
| Take nth bytes | `utils/take_nth.json` | Every Nth byte |
| Remove null bytes | `utils/null_bytes.json` | Strip \x00 |

---

## Phase 10: Data Format (Remaining Encodings)
**Category:** Data format
**Rationale:** Filling encoding gaps

| Operation | Test File | Notes |
|-----------|-----------|-------|
| To/From Base | `data_format/base.json` | Arbitrary base conversion |
| To/From Base92 | `data_format/base92.json` | High-density encoding |
| To/From Braille | `data_format/braille.json` | Braille patterns |
| To/From Modhex | `data_format/modhex.json` | Yubikey encoding |
| To/From Punycode | `data_format/punycode.json` | IDN encoding |
| To/From Quoted Printable | `data_format/quoted_printable.json` | Email encoding |

---

## Phase 11: Data Format (Hex/Binary Tools)
**Category:** Data format
**Rationale:** Common analysis operations

| Operation | Test File | Notes |
|-----------|-----------|-------|
| To/From Hexdump | `data_format/hexdump.json` | Classic hex dump |
| To/From Hex Content | `data_format/hex_content.json` | Escaped hex |
| Swap endianness | `data_format/endianness.json` | Byte order conversion |
| To/From BCD | `data_format/bcd.json` | Binary-coded decimal |
| To/From Float | `data_format/float.json` | IEEE 754 conversion |

---

## Phase 12: Regex-Based Extractors (Part 1)
**Category:** Extractors
**Rationale:** 0% coverage, regex-based = no external dependencies

| Operation | Test File | Notes |
|-----------|-----------|-------|
| Extract URLs | `extractors/urls.json` | URL pattern matching |
| Extract email addresses | `extractors/emails.json` | Email pattern matching |
| Extract IP addresses | `extractors/ips.json` | IPv4/IPv6 extraction |
| Extract domains | `extractors/domains.json` | Domain extraction |
| Extract hashes | `extractors/hashes.json` | MD5/SHA pattern matching |

---

## Phase 13: Regex-Based Extractors (Part 2)
**Category:** Extractors
**Rationale:** More extractors and query operations

| Operation | Test File | Notes |
|-----------|-----------|-------|
| Extract file paths | `extractors/file_paths.json` | Windows/Unix paths |
| Extract MAC addresses | `extractors/mac.json` | MAC address patterns |
| Strings | `extractors/strings.json` | ASCII string extraction |
| XPath expression | `extractors/xpath.json` | XML querying |
| JPath expression | `extractors/jpath.json` | JSON querying |
| CSS selector | `extractors/css_selector.json` | HTML querying |

---

## Phase 14: Code Tidy Operations
**Category:** Code tidy
**Rationale:** Language formatting, deterministic

| Operation | Test File | Notes |
|-----------|-----------|-------|
| CSS Beautify/Minify | `code_tidy/css.json` | CSS formatting |
| JavaScript Beautify/Minify | `code_tidy/javascript.json` | JS formatting |
| SQL Beautify/Minify | `code_tidy/sql.json` | SQL formatting |
| Strip HTML tags | `code_tidy/strip_html.json` | Remove HTML |
| Generic Code Beautify | `code_tidy/generic.json` | General formatting |

---

## Phase 15: Case Transformations
**Category:** Code tidy
**Rationale:** Simple string transformations

| Operation | Test File | Notes |
|-----------|-----------|-------|
| To Camel case | `code_tidy/case_transforms.json` | camelCase |
| To Kebab case | `code_tidy/case_transforms.json` | kebab-case |
| To Snake case | `code_tidy/case_transforms.json` | snake_case |
| PHP Serialize/Deserialize | `code_tidy/php.json` | PHP data format |
| Jq | `code_tidy/jq.json` | JSON processor |

---

## Phase 16: Arithmetic (Remaining Operations)
**Category:** Arithmetic / Logic
**Rationale:** Math operations, deterministic

| Operation | Test File | Notes |
|-----------|-----------|-------|
| Divide / Multiply | `arithmetic/math.json` | Basic arithmetic |
| Mean / Median / Sum | `arithmetic/stats.json` | Statistical functions |
| Standard Deviation | `arithmetic/stats.json` | Statistics |
| Power Set | `arithmetic/set_theory.json` | Set operations |
| Set Union/Intersection/Difference | `arithmetic/set_theory.json` | Set operations |
| Cartesian Product | `arithmetic/set_theory.json` | Set operations |

---

## Phase 17: Networking (Parsing Only)
**Category:** Networking
**Rationale:** Parsing operations that don't require network access

| Operation | Test File | Notes |
|-----------|-----------|-------|
| Parse URI | `networking/parse_uri.json` | URL component parsing |
| Parse User Agent | `networking/user_agent.json` | UA string parsing |
| Defang/Fang URL | `networking/url_defang.json` | Security obfuscation |
| Encode/Decode NetBIOS | `networking/netbios.json` | Name encoding |
| Format MAC addresses | `networking/mac_format.json` | MAC formatting |
| VarInt Encode/Decode | `networking/varint.json` | Variable-length integers |

---

## Phase 18: Networking (Protocol Headers)
**Category:** Networking
**Rationale:** Header parsing, requires crafted binary test data

| Operation | Test File | Notes |
|-----------|-----------|-------|
| Parse IPv4 header | `networking/ipv4_header.json` | Use hex-encoded packets |
| Parse TCP | `networking/tcp.json` | TCP header parsing |
| Parse UDP | `networking/udp.json` | UDP header parsing |
| Protobuf Decode/Encode | `networking/protobuf.json` | Protocol buffers |

---

## Phase 19: Symmetric Encryption (AES)
**Category:** Encryption / Encoding
**Rationale:** Critical crypto, use NIST test vectors

| Operation | Test File | Notes |
|-----------|-----------|-------|
| AES Encrypt/Decrypt | `encryption/aes.json` | NIST FIPS 197 vectors |
| AES Key Wrap/Unwrap | `encryption/aes_wrap.json` | RFC 3394 vectors |

---

## Phase 20: Symmetric Encryption (DES/Blowfish)
**Category:** Encryption / Encoding
**Rationale:** Legacy but still encountered, standard test vectors

| Operation | Test File | Notes |
|-----------|-----------|-------|
| DES Encrypt/Decrypt | `encryption/des.json` | FIPS 46-3 vectors |
| Triple DES Encrypt/Decrypt | `encryption/triple_des.json` | 3DES test vectors |
| Blowfish Encrypt/Decrypt | `encryption/blowfish.json` | Schneier test vectors |
| RC4 / RC4 Drop | `encryption/rc4.json` | RC4 stream cipher |

---

## Phase 21: Stream Ciphers
**Category:** Encryption / Encoding
**Rationale:** Modern stream ciphers

| Operation | Test File | Notes |
|-----------|-----------|-------|
| ChaCha | `encryption/chacha.json` | RFC 8439 test vectors |
| Salsa20 / XSalsa20 | `encryption/salsa.json` | DJB test vectors |
| Rabbit | `encryption/rabbit.json` | eSTREAM cipher |

---

## Phase 22: Other Category (Simple Operations)
**Category:** Other
**Rationale:** Miscellaneous utilities

| Operation | Test File | Notes |
|-----------|-----------|-------|
| Entropy | `other/entropy.json` | Calculate entropy |
| Frequency distribution | `other/frequency.json` | Character frequency |
| Generate/Analyse UUID | `other/uuid.json` | UUID operations |
| Index of Coincidence | `other/ioc.json` | Cryptanalysis metric |
| Generate Lorem Ipsum | `other/lorem.json` | Placeholder text |
| Chi Square | `other/chi_square.json` | Statistical test |

---

## Phase 23: Compression (Remaining)
**Category:** Compression
**Rationale:** Archive formats

| Operation | Test File | Notes |
|-----------|-----------|-------|
| LZNT1 Decompress | `compression/lznt1.json` | Windows compression |
| Tar / Untar | `compression/tar.json` | Archive format |

---

## Phase 24: Key Derivation
**Category:** Encryption / Encoding
**Rationale:** Password hashing and key derivation

| Operation | Test File | Notes |
|-----------|-----------|-------|
| Derive PBKDF2 key | `encryption/pbkdf2.json` | RFC 6070 vectors |
| Derive HKDF key | `encryption/hkdf.json` | RFC 5869 vectors |
| Derive EVP key | `encryption/evp.json` | OpenSSL EVP |
| Scrypt | `encryption/scrypt.json` | RFC 7914 vectors |
| Bcrypt | `encryption/bcrypt.json` | Password hashing |
| Argon2 | `hashing/argon2.json` | Modern password hash |

---

## Phase 25: Simple Forensics
**Category:** Forensics
**Rationale:** Operations that work on simple binary data

| Operation | Test File | Notes |
|-----------|-----------|-------|
| Detect File Type | `forensics/file_type.json` | Magic byte detection |
| YARA Rules | `forensics/yara.json` | Pattern matching |

---

## Deferred Phases (Complex Dependencies)

### Phase 26+: Public Key Operations
**Complexity:** Require key generation and management
- RSA Encrypt/Decrypt/Sign/Verify
- ECDSA operations
- PGP operations
- JWK/PEM conversions

### Phase 27+: Multimedia Operations
**Complexity:** Require image files as test fixtures
- Image manipulation (blur, crop, rotate, etc.)
- OCR
- Charts

### Phase 28+: Network-Dependent Operations
**Complexity:** Require network access or mocking
- DNS over HTTPS
- HTTP request

### Phase 29+: Flow Control Operations
**Complexity:** Require recipe chain testing infrastructure
- Fork, Merge, Jump, Label, etc.

### Phase 30+: Complex Binary Analysis
**Complexity:** Require complex binary test fixtures
- ELF Info
- Disassemble x86
- Extract embedded files

---

## Implementation Guidelines

### Test File Format
```json
{
  "operation": "Operation Name",
  "category": "category_name",
  "description": "Description of what is being tested",
  "tests": [
    {
      "name": "descriptive_test_name",
      "comment": "Explanation of test case",
      "input": {
        "type": "bytes",
        "encoding": "hex",
        "value": "48656c6c6f"
      },
      "operations": ["Operation Name"],
      "expected": {
        "type": "bytes",
        "encoding": "hex",
        "value": "expected_output"
      },
      "tags": ["tag1", "tag2"]
    }
  ]
}
```

### Test Case Requirements
1. **Minimum 4 test cases per operation:**
   - Basic functionality
   - Edge case (empty input)
   - Different input types
   - Error handling (if applicable)

2. **Use standard test vectors where available:**
   - RFC test vectors for crypto
   - Known-answer tests from specifications

3. **Input/Output formats:**
   - Use `"type": "bytes", "encoding": "hex"` for binary data
   - Use `"type": "string"` for text data

### Directory Structure
```
tests/data/operations/
├── encryption/
├── hashing/
├── data_format/
├── networking/
├── utils/
├── extractors/
├── code_tidy/
├── arithmetic/
├── compression/
├── datetime/
├── language/
├── forensics/
├── other/
└── public_key/
```

---

## Progress Tracking

| Phase | Status | Operations | Coverage Added |
|-------|--------|------------|----------------|
| 1 | Pending | 5 | +1.1% |
| 2 | Pending | 4 | +0.9% |
| 3 | Pending | 7 | +1.6% |
| 4 | Pending | 6 | +1.3% |
| 5 | Pending | 4 | +0.9% |
| 6 | Pending | 4 | +0.9% |
| 7 | Pending | 6 | +1.3% |
| 8 | Pending | 6 | +1.3% |
| 9 | Pending | 5 | +1.1% |
| 10 | Pending | 6 | +1.3% |
| 11 | Pending | 5 | +1.1% |
| 12 | Pending | 5 | +1.1% |
| 13 | Pending | 6 | +1.3% |
| 14 | Pending | 5 | +1.1% |
| 15 | Pending | 5 | +1.1% |
| 16 | Pending | 6 | +1.3% |
| 17 | Pending | 6 | +1.3% |
| 18 | Pending | 4 | +0.9% |
| 19 | Pending | 2 | +0.4% |
| 20 | Pending | 4 | +0.9% |
| 21 | Pending | 3 | +0.7% |
| 22 | Pending | 6 | +1.3% |
| 23 | Pending | 2 | +0.4% |
| 24 | Pending | 6 | +1.3% |
| 25 | Pending | 2 | +0.4% |
| **Total (Phases 1-25)** | | **~120** | **~27%** |

**After Phase 25:** ~190 operations tested (~43% coverage)
