import { dirname } from 'path'
import { fileURLToPath } from 'url'
import path from 'path'

import js from '@eslint/js'
import tseslint from 'typescript-eslint'
import prettierConfig from 'eslint-config-prettier'
import importPlugin from 'eslint-plugin-import'
import jest from 'eslint-plugin-jest'
import jsxA11y from 'eslint-plugin-jsx-a11y'
import prettier from 'eslint-plugin-prettier'
import react from 'eslint-plugin-react'
import reactHooks from 'eslint-plugin-react-hooks'
import nextPlugin from '@next/eslint-plugin-next'
import globals from 'globals'
import noGlobalIsFiniteRule from './eslint-rules/no-global-isfinite.mjs'
import noGlobalIsNaNRule from './eslint-rules/no-global-isnan.mjs'
import noGlobalNaNRule from './eslint-rules/no-global-nan.mjs'
import noGlobalParseFloatRule from './eslint-rules/no-global-parsefloat.mjs'
import noGlobalParseIntRule from './eslint-rules/no-global-parseint.mjs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const eslintConfig = [
  ...tseslint.configs.recommended,
  react.configs.flat['jsx-runtime'],
  {
    ignores: [
      '.cache',
      '.next',
      '.pnpm-store',
      'node_modules',
      'build',
      'dist',
      'next-env.d.ts',
      'src/types/__generated__/**/*',
      'tailwind.config.js',
      'lighthouserc.js',
      'postcss.config.js',
    ],
  },
  js.configs.recommended,
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.es2023,
        ...globals.jest,
        ...globals.node,
      },
      parserOptions: {
        project: './tsconfig.json',
        tsconfigRootDir: __dirname,
      },
    },
    plugins: {
      'react-hooks': reactHooks,
      import: importPlugin,
      jest,
      prettier,
      react,
      'jsx-a11y': jsxA11y,
      '@next/next': nextPlugin,
      nest: {
        rules: {
          'no-global-isfinite': noGlobalIsFiniteRule,
          'no-global-isnan': noGlobalIsNaNRule,
          'no-global-nan': noGlobalNaNRule,
          'no-global-parsefloat': noGlobalParseFloatRule,
          'no-global-parseint': noGlobalParseIntRule,
        },
      },
    },
    settings: {
      'import/resolver': {
        alias: {
          map: [
            ['@tests', path.resolve(__dirname, '__tests__')],
            ['@', path.resolve(__dirname, 'src')],
          ],
          extensions: ['.js', '.jsx', '.ts', '.tsx'],
        },
      },
      react: {
        version: 'detect',
      },
    },
    rules: {
      ...jest.configs.recommended.rules,
      ...prettierConfig.rules,
      ...nextPlugin.configs.recommended.rules,
      
      "@typescript-eslint/no-unnecessary-type-assertion": "error",
      "@typescript-eslint/no-non-null-assertion": "error",
"@typescript-eslint/no-unnecessary-condition": "off",

      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-inferrable-types': 'warn',
      '@typescript-eslint/no-unused-expressions': 'error',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/naming-convention': [
        'error',
        {
          selector: 'property',
          modifiers: ['requiresQuotes'],
          format: null,
        },
        {
          selector: 'property',
          filter: {
            regex: '^_{1,2}',
            match: true,
          },
          format: null,
        },
        {
          selector: 'property',
          filter: {
            regex: '^(NextResponse|Cookie)$',
            match: true,
          },
          format: null,
        },
        {
          selector: 'property',
          format: ['camelCase', 'UPPER_CASE'],
        },
      ],
      'react-hooks/exhaustive-deps': 'warn',
      'react-hooks/rules-of-hooks': 'error',
      'react/prop-types': 'off',
      'react/react-in-jsx-scope': 'off',
      'import/order': [
        'warn',
        {
          alphabetize: { order: 'asc', caseInsensitive: true },
          groups: ['builtin', 'external', 'internal', ['parent', 'sibling', 'index']],
          pathGroups: [
            { pattern: 'app/**', group: 'internal', position: 'before' },
            { pattern: 'lib/**', group: 'internal', position: 'after' },
            { pattern: 'server/**', group: 'internal', position: 'after' },
            { pattern: 'types/**', group: 'internal', position: 'after' },
            { pattern: 'utils/**', group: 'internal', position: 'after' },
            { pattern: 'components/**', group: 'internal', position: 'after' },
            { pattern: '@tests/**', group: 'internal', position: 'after' },
          ],
          pathGroupsExcludedImportTypes: ['builtin'],
        },
      ],
      'no-console': 'error',
      'no-restricted-imports': [
        'error',
        {
          patterns: ['.*'],
        },
      ],
      'no-unused-vars': 'off',
      ...jsxA11y.configs.recommended.rules,
      'jsx-a11y/anchor-is-valid': 'warn',
      'jsx-a11y/no-autofocus': 'warn',
      'jsx-a11y/no-distracting-elements': 'warn',
      'jsx-a11y/label-has-associated-control': 'error',
      'jsx-a11y/click-events-have-key-events': 'warn',
      'nest/no-global-isfinite': 'error',
      'nest/no-global-isnan': 'error',
      'nest/no-global-nan': 'error',
      'nest/no-global-parsefloat': 'error',
      'nest/no-global-parseint': 'error',
      quotes: ['error', 'single', { avoidEscape: true }],
    },
  },
  {
    files: ['src/utils/logger.ts'],
    rules: {
      'no-console': 'off',
    },
  },
  {
  files: ['**/*.test.ts', '**/*.test.tsx'],
  rules: {
    '@typescript-eslint/no-non-null-assertion': 'off',
  },
},
]

export default eslintConfig