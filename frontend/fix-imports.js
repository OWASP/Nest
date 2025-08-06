const fs = require('fs');
const glob = require('glob');

// Files that need import reordering
const files = [
  '__tests__/unit/components/BreadCrumbs.test.tsx',
  '__tests__/unit/components/Footer.test.tsx',
  '__tests__/unit/components/MetricsCard.test.tsx',
  '__tests__/unit/components/NavButton.test.tsx',
  '__tests__/unit/components/ProjectsDashboardNavBar.test.tsx',
  '__tests__/unit/pages/Header.test.tsx',
  '__tests__/unit/pages/OrganizationDetails.test.tsx'
];

files.forEach(file => {
  const fullPath = file;
  if (fs.existsSync(fullPath)) {
    console.log(`Processing ${file}...`);
    const content = fs.readFileSync(fullPath, 'utf8');
    const lines = content.split('\n');

    // Find import lines and separate them by type
    const reactImports = [];
    const typeImports = [];
    const utilImports = [];
    const otherImports = [];
    const nonImportLines = [];

    let inImportSection = true;

    lines.forEach((line, index) => {
      if (line.trim().startsWith('import ')) {
        if (line.includes('from \'react\'') || line.includes('from "react"')) {
          reactImports.push(line);
        } else if (line.includes('import type ') || line.includes('import { type ')) {
          typeImports.push(line);
        } else if (line.includes('wrappers/testUtil')) {
          utilImports.push(line);
        } else {
          otherImports.push(line);
        }
      } else if (line.trim() === '' && inImportSection) {
        // Continue - empty lines in import section
      } else {
        inImportSection = false;
        nonImportLines.push(line);
      }
    });

    // Reorder: react -> type imports -> test utils -> other imports
    const reorderedImports = [
      ...reactImports,
      ...typeImports,
      ...utilImports,
      ...otherImports
    ];

    // Join with proper empty line
    const newContent = reorderedImports.join('\n') + '\n\n' + nonImportLines.join('\n');

    fs.writeFileSync(fullPath, newContent);
    console.log(`Fixed imports in ${file}`);
  } else {
    console.log(`File not found: ${file}`);
  }
});

console.log('Import reordering complete!');
