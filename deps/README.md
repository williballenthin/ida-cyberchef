We're using a minor fork of CyberChef: https://github.com/williballenthin/CyberChef/tree/commonjs-minimal-interpeter

But in the event that this fork disappears for some reason, versus [CyberChef at commit 2a1294f1c089bb8e68d38d1803d08858907f352a](https://github.com/gchq/CyberChef/commit/2a1294f1c089bb8e68d38d1803d08858907f352a)
we've applied the patch in ./CyberChef.patch.


```
Author: Willi Ballenthin <wballenthin@hex-rays.com>
Date:   Sat Oct 11 22:28:56 2025 +0200

    fix: inject process.versions.node at build time

    This makes isNodeEnvironment() return true during webpack bundling,
    ensuring the Node.js code paths are included in the bundle.

    This allows the bundle to work in alternative JS runtimes like
    STPyV8 and PythonMonkey that provide Node.js polyfills.

    Without this, the webpack closure captures 'false' from the browser
    polyfill at build time, and runtime polyfills can't override it.
    better minimal runtime detection

commit 724c3c88f29cb7ae39e9eea2ce958f6767dda2b2
Author: Willi Ballenthin <wballenthin@hex-rays.com>
Date:   Fri Oct 10 17:22:50 2025 +0200

    add CommonJS build for a minimal JS interpreter

commit ca1cc19af97acf9c4feaff9743597299eb2ecd9b
Author: Willi Ballenthin <wballenthin@hex-rays.com>
Date:   Sat Oct 11 13:17:48 2025 +0200

    update JS import syntax
```

Basically: we fix the JS syntax and then make the NodeJS profile even more minimal - it relies on *very* little from the interpreter environment.
This way we can load it into a barebones SpiderMonkey/V8 interpreter.

