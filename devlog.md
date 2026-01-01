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
- **132 passed, 5 failed (96.4%)**
- Created `test_operations_comprehensive.py` with 116 new tests

### Working Operations
All major categories work:
- Encodings (Base64, Hex, URL, HTML, Binary, Octal)
- Hashing (MD5, SHA family, BLAKE2, CRC, HMAC)
- String manipulation (Reverse, Case, Split, Sort)
- Logic operations (XOR, AND, OR, bit shifts)
- Classical ciphers (ROT13, Vigenère, Atbash)
- Network parsing (IP, URL extraction)
- JSON/XML formatting

### Known Issues

1. **Compression ops fail** (Zlib, Gzip) - `out-of-bound numeric index` error
   - Likely typed array handling issue in QuickJS
   - Workaround: Use Python's `zlib` module instead

2. **AES/RC4 roundtrip** - argument format mismatch
   - Encryption works, decryption needs investigation
   - Args structure differs from web UI

3. **Some conversions** (distance, mass) - wrong arg names
   - Need to check operation_schema.json for correct parameter names

### Files Changed
- `pyproject.toml`: `stpyv8` → `quickjs`
- `ida_cyberchef/cyberchef.py`: Complete rewrite
- `ida_cyberchef/__init__.py`: Optional Qt imports
- `tests/test_cyberchef.py`: Updated to use `bake()` API
- `tests/test_operations_comprehensive.py`: New comprehensive test suite

### Future Work
- [ ] Fix compression operations (may need custom polyfill)
- [ ] Debug AES/RC4 argument handling
- [ ] Add more edge case tests
- [ ] Performance comparison vs STPyV8
