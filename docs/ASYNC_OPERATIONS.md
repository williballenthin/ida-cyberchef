# Async Operations in STPyV8: Understanding Promise Resolution Limitations

This document explains the technical challenges of running JavaScript async operations
in STPyV8 (Python V8 bindings), and the solutions implemented for ida-cyberchef.

## The Problem

CyberChef operations can be synchronous or asynchronous. Async operations return JavaScript
Promises, which require the V8 event loop to resolve. However, STPyV8 doesn't provide a
traditional event loop - `ctx.eval()` executes JavaScript and returns immediately.

### How Promises Work in Normal JavaScript

```javascript
// In Node.js or browser:
const result = await someAsyncOperation();
// The event loop pumps microtasks until the Promise resolves
```

The JavaScript runtime has an event loop that continuously processes:
1. Macrotasks (setTimeout, I/O callbacks)
2. Microtasks (Promise callbacks, queueMicrotask)

### How STPyV8 Differs

```python
# In STPyV8:
result = ctx.eval("someAsyncOperation()")  # Returns a Promise object
# The V8 microtask queue is NOT automatically pumped
# The Promise never resolves!
```

## Types of Async Patterns

### Type 1: Microtask-based Promises

These Promises resolve via the microtask queue (Promise.resolve().then(), etc.):

```javascript
function asyncOp() {
    return new Promise(resolve => {
        Promise.resolve().then(() => resolve("done"));
    });
}
```

**Can be resolved in STPyV8** by repeatedly calling `ctx.eval("")` to pump microtasks.

### Type 2: Callback-based Libraries

Libraries that use internal callbacks (like `@blu3r4y/lzma`):

```javascript
// Original LZMA pattern:
lzma.compress(data, mode, (result) => {
    resolve(result);  // Callback fires via microtask
});
```

**Can be resolved** if the library supports synchronous mode:

```javascript
// LZMA supports sync mode when no callback is provided:
const result = lzma.compress(data, mode);  // Returns immediately
```

### Type 3: WebAssembly.instantiate() Promises

WASM compilation runs on a separate thread and requires the event loop:

```javascript
function bzip2Compress(data) {
    return new Promise(resolve => {
        Bzip2().then(bzip2 => {  // WebAssembly.instantiate() internally
            resolve(bzip2.compress(data));
        });
    });
}
```

**Cannot be resolved in STPyV8** - the WASM compilation completion never triggers
because it requires the V8 event loop, not just microtask pumping.

## Solutions Implemented

### LZMA Operations (Fixed)

The `@blu3r4y/lzma` library supports synchronous mode when called without callbacks.

**Original async code:**
```javascript
run(input, args) {
    return new Promise((resolve, reject) => {
        compress(new Uint8Array(input), mode, (result, error) => {
            if (error) reject(error);
            else resolve(new Int8Array(result).buffer);
        });
    });
}
```

**Fixed synchronous code:**
```javascript
run(input, args) {
    const mode = Number(args[0]);
    const result = compress(new Uint8Array(input), mode);  // No callback = sync
    return new Int8Array(result).buffer;
}
```

### Bzip2 Operations (Not Fixable)

The `libbzip2-wasm` library is Emscripten-compiled WebAssembly that requires async
initialization via `WebAssembly.instantiate()`:

```javascript
run(input, args) {
    return new Promise((resolve, reject) => {
        Bzip2().then(bzip2 => {  // This Promise NEVER resolves in STPyV8
            resolve(bzip2.compress(data));
        });
    });
}
```

**Why it can't be easily fixed:**

1. `WebAssembly.instantiate()` returns a Promise that requires the event loop
2. Synchronous WASM instantiation (`new WebAssembly.Module()`) works, but:
   - The Emscripten runtime uses async patterns for memory setup
   - The generated glue code expects Promise-based initialization
3. Fixing would require:
   - Rebuilding libbzip2-wasm with `-s WASM_ASYNC_COMPILATION=0`
   - Or pre-initializing the WASM module at load time with complex caching
   - Or replacing with a pure JavaScript bzip2 implementation

## CyberChef's Wrapper Architecture

CyberChef's Node API wraps operations in `_wrap()` (api.mjs):

```javascript
function _wrap(OpClass) {
    const opInstance = new OpClass();
    const isAsync = opInstance.run.constructor.name === "AsyncFunction";

    if (isAsync) {
        // Async wrapper uses await
        wrapped = async (input, args) => {
            const result = await opInstance.run(input, args);
            return new NodeDish({ value: result, ... });
        };
    } else {
        // Sync wrapper - PROBLEM: doesn't handle Promise returns!
        wrapped = (input, args) => {
            const result = opInstance.run(input, args);  // If this is a Promise...
            return new NodeDish({ value: result, ... }); // ...it gets stored as-is
        };
    }
}
```

**The gap:** Operations like Bzip2 that return Promises but aren't declared `async`
get the sync wrapper, which packages the Promise object directly into a NodeDish
instead of awaiting it.

## Alternative Approach: Async Wrapping (Explored but Not Used)

We experimented with making all wrappers async:

```javascript
var isAsync = true;  // Force async for all operations
```

And making NodeRecipe.execute async:

```javascript
async execute(dish) {
    for (const op of this.opList) {
        dish = await op(dish);  // Await each operation
    }
    return dish;
}
```

**Why this wasn't adopted:**
1. Breaks direct API usage (`chef.MD5()` returns Promise instead of result)
2. Still doesn't fix WebAssembly-based operations
3. Adds complexity without solving the core issue

## Summary

| Operation Type | Pattern | STPyV8 Support | Solution |
|---------------|---------|----------------|----------|
| Synchronous | Returns value directly | Works | N/A |
| Async (microtask) | Promise via callbacks | Can work | Pump microtasks |
| Async (sync mode) | Library supports sync | Works | Use sync mode (LZMA) |
| Async (WASM) | WebAssembly.instantiate | **Doesn't work** | None simple (Bzip2) |

## Files Modified

- `deps/CyberChef/src/core/operations/LZMACompress.mjs` - Use sync mode
- `deps/CyberChef/src/core/operations/LZMADecompress.mjs` - Use sync mode
- `ida_cyberchef/data/CyberChef.js` - Bundled changes
- `tests/data/operations/compression/lzma.json` - Tests enabled
- `tests/data/operations/compression/bzip2.json` - Tests skipped with explanation
