# Development Log

## 2026-01-01: QuickJS Migration

### Goal
Replace STPyV8 (V8 bindings) with QuickJS as the JavaScript engine for CyberChef execution.

### Why QuickJS?
- **STPyV8 pain points**: Large binary (~50MB), complex build requirements, platform-specific issues
- **QuickJS benefits**: ~300KB, pure Python wheel, ES2023 support, memory/time limits

### Key Decisions

1. **Used `quickjs` PyPI package** (v1.19.4) - thin wrapper by Petter Strandmark
   - Alternative `pyquickjs` exists but `quickjs` has better docs and is more maintained

2. **Rewrote `cyberchef.py` to use Context API**
   - QuickJS returns a Context, not an object with methods like STPyV8
   - All JS execution goes through `ctx.eval()` with JSON serialization for data passing
   - Dish objects serialized to/from JSON rather than crossing Python/JS boundary directly

3. **Made Qt imports optional** in `__init__.py`
   - Enables headless usage (tests, CLI) without Qt dependencies
   - Qt widgets only imported if available

4. **Standardized on `bake()` API**
   - Old tests used direct method calls (`chef.fromBase64()`)
   - New approach: everything goes through `bake(input, recipe)`

### Technical Details

```python
# Old (STPyV8):
ctx = STPyV8.JSContext()
ctx.enter()
chef = ctx.eval("module.exports")
result = chef.fromBase64(input)  # Direct method call

# New (QuickJS):
ctx = quickjs.Context()
ctx.eval(cyberchef_code)
result_json = ctx.eval(f"""
    const result = _cyberchef.bake(dish, recipe);
    JSON.stringify(result);
""")
result = json.loads(result_json)
```

### Test Results
- **140 passed, 0 failed (100%)**
- Created `test_operations_comprehensive.py` with 119 tests

### Working Operations
All major categories work:
- Encodings (Base64, Hex, URL, HTML, Binary, Octal)
- Hashing (MD5, SHA family, BLAKE2, CRC, HMAC)
- String manipulation (Reverse, Case, Split, Sort)
- Logic operations (XOR, AND, OR, bit shifts)
- Classical ciphers (ROT13, Vigenère, Atbash)
- Network parsing (IP, URL extraction)
- JSON/XML formatting
- Modern crypto (AES, RC4, Blowfish)
- Unit conversions (data, distance, mass)

### Files Changed
- `pyproject.toml`: `stpyv8` → `quickjs`
- `ida_cyberchef/cyberchef.py`: Complete rewrite
- `ida_cyberchef/__init__.py`: Optional Qt imports
- `tests/test_cyberchef.py`: Updated to use `bake()` API
- `tests/test_operations_comprehensive.py`: New comprehensive test suite

---

## 2026-01-01: Issue Investigation & Resolution

### Issues Investigated

#### 1. Compression Operations (Zlib/Gzip) - KNOWN LIMITATION
**Root Cause**: QuickJS has stricter typed array bounds checking than V8. CyberChef's embedded zlib library uses complex Huffman tree operations that trigger `out-of-bound numeric index` errors.

**Location**: `CyberChef.js` lines 477257 (`Ka`) and 477429 (`Da`) - Huffman encoding functions

**Recommended Fix**: Use Python's built-in `zlib`/`gzip` modules instead:
```python
PYTHON_OPERATION_OVERRIDES = {
    'Zlib Deflate': lambda data, args: zlib.compress(data),
    'Zlib Inflate': lambda data, args: zlib.decompress(data),
    'Gzip': lambda data, args: gzip.compress(data),
    'Gunzip': lambda data, args: gzip.decompress(data),
}
```

#### 2. AES/RC4 Crypto - RESOLVED ✓
**Root Cause**: Test assertions expected `bytes` but operations return `str` (per schema: `outputType: "string"`)

**Fix**: Changed assertions from `assert result == b"hello"` to `assert result == "hello"`

#### 3. Unit Conversions - RESOLVED ✓
**Root Cause**: Argument values must match schema exactly, including abbreviations

**Examples**:
```python
# WRONG: "Bytes" → Returns "NaN"
# RIGHT: "Bytes (B)" → Works correctly

# WRONG: "Word length": 4
# RIGHT: "Word length (bytes)": 4
```

#### 4. From Quoted Printable - RESOLVED ✓
**Root Cause**: Operation returns `byteArray` per schema, test expected string

**Fix**: Changed `assert "hello" in result` to `assert result == b"hello=world"`

### Lessons Learned

1. **Schema is source of truth** - Always check `operation_schema.json` for exact argument names/values
2. **Check output types** - Schema's `outputType` determines if result is string or bytes
3. **Unit names need abbreviations** - e.g., `"Bytes (B)"` not `"Bytes"`
4. **Argument names are literal** - Include suffixes like `"(bytes)"`

### Future Work
- [ ] Implement Python fallbacks for compression operations
- [ ] Add schema validation helper for test writing
- [ ] Performance benchmark vs STPyV8
