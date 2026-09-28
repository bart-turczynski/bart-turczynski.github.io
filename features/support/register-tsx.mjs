// Registers the tsx ESM loader so Cucumber can import the TypeScript step
// definitions (and their `../src/*.js` -> `*.ts` imports) under NodeNext.
//
// Listed first in cucumber.json's `import` so it runs before any `.ts` file is
// loaded. This replaces the legacy `requireModule: ["tsx"]` (CommonJS) hook,
// which is deprecated and, on Node 24+, loses the resolution race to Node's
// native type-stripping — native stripping does not rewrite `.js` -> `.ts`, so
// `import "../../src/index.js"` fails. Registering tsx's loader explicitly puts
// its resolver in front. No NODE_OPTIONS needed, so it stays cross-platform.
import { register } from "tsx/esm/api";

register();
