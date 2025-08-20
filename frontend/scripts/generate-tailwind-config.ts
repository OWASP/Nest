
// scripts/generate-tailwind-config.ts
import fs from 'fs';
import path from 'path';
import tailwindConfig from '../tailwind.config.js';  // ← now .js

const configStr = JSON.stringify(tailwindConfig, (key, value) => {
  if (typeof value === 'function') {
    return `Function:${value.name || 'anonymous'}`;
  }
  return value;
}, 2);

const cjsContent = `
// Auto-generated from tailwind.config.ts
// DO NOT EDIT MANUALLY
module.exports = ${configStr};
`;

const outputPath = path.resolve(__dirname, '../tailwind.config.generated.js');
fs.writeFileSync(outputPath, cjsContent);
console.log('✅ Generated: tailwind.config.generated.js');