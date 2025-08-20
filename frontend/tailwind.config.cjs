// tailwind.config.cjs
// This file exists to support tools that don't support ESM or TypeScript.
// It imports the real config from tailwind.config.ts via a generated .js file.

module.exports = require('./tailwind.config.generated.js');