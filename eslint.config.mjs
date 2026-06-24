import { readFileSync } from 'node:fs'
import path, { dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

import js from '@eslint/js'
import nextPlugin from '@next/eslint-plugin-next'
import eslintConfigPrettier from 'eslint-config-prettier'
import importPlugin from 'eslint-plugin-import'
import jest from 'eslint-plugin-jest'
import jsxA11y from 'eslint-plugin-jsx-a11y'
import playwright from 'eslint-plugin-playwright'
import react from 'eslint-plugin-react'
import reactHooks from 'eslint-plugin-react-hooks'
import globals from 'globals'
import tseslint from 'typescript-eslint'

import noGlobalIsFiniteRule from './frontend/eslint-rules/no-global-isfinite.mjs'
import noGlobalIsNaNRule from './frontend/eslint-rules/no-global-isnan.mjs'
import noGlobalNaNRule from './frontend/eslint-rules/no-global-nan.mjs'
import noGlobalParseFloatRule from './frontend/eslint-rules/no-global-parsefloat.mjs'
import noGlobalParseIntRule from './frontend/eslint-rules/no-global-parseint.mjs'

const rootDir = dirname(fileURLToPath(import.meta.url))
const frontendDir = path.join(rootDir, 'frontend')
const frontendPackageJson = JSON.parse(readFileSync(path.join(frontendDir, 'package.json'), 'utf8'))
const jestMajorVersion = Number.parseInt(frontendPackageJson.devDependencies.jest.split('.')[0], 10)

export default [
  {
    ignores: [
      '**/node_modules/**',
      'e2e/playwright-report/**',
      'e2e/test-results/**',
      'frontend/.cache/**',
      'frontend/.next/**',
      'frontend/.pnpm-store/**',
      'frontend/build/**',
      'frontend/dist/**',
      'frontend/next-env.d.ts',
      'frontend/src/types/__generated__/**',
    ],
  },
  ...tseslint.configs.recommended,
  js.configs.recommended,
  {
    files: ['frontend/**/*.{js,jsx,ts,tsx}', 'e2e/**/*.{js,ts}'],
    rules: {
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
    },
  },
  {
    files: ['e2e/**/*.{js,ts}'],
    languageOptions: {
      globals: {
        ...globals.node,
        ...playwright.configs['flat/recommended'].languageOptions.globals,
      },
    },
    plugins: playwright.configs['flat/recommended'].plugins,
    rules: {
      ...playwright.configs['flat/recommended'].rules,
      'playwright/expect-expect': [
        'error',
        { assertFunctionNames: ['expectBreadCrumbsToBeVisible'] },
      ],
    },
  },
  {
    files: ['frontend/**/*.{js,jsx,ts,tsx}'],
    ...react.configs.flat['jsx-runtime'],
  },
  {
    files: ['frontend/**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.es2023,
        ...globals.jest,
        ...globals.node,
      },
    },
    plugins: {
      '@next/next': nextPlugin,
      import: importPlugin,
      jest,
      'jsx-a11y': jsxA11y,
      nest: {
        rules: {
          'no-global-isfinite': noGlobalIsFiniteRule,
          'no-global-isnan': noGlobalIsNaNRule,
          'no-global-nan': noGlobalNaNRule,
          'no-global-parsefloat': noGlobalParseFloatRule,
          'no-global-parseint': noGlobalParseIntRule,
        },
      },
      react,
      'react-hooks': reactHooks,
    },
    settings: {
      'import/resolver': {
        alias: {
          extensions: ['.js', '.jsx', '.ts', '.tsx'],
          map: [
            ['@tests', path.resolve(frontendDir, '__tests__')],
            ['@', path.resolve(frontendDir, 'src')],
          ],
        },
      },
      jest: {
        version: jestMajorVersion,
      },
      next: {
        rootDir: 'frontend/',
      },
      react: {
        version: 'detect',
      },
    },
    rules: {
      ...jest.configs.recommended.rules,
      ...nextPlugin.configs.recommended.rules,
      ...jsxA11y.configs.recommended.rules,
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/naming-convention': [
        'error',
        {
          format: null,
          modifiers: ['requiresQuotes'],
          selector: 'property',
        },
        {
          filter: {
            match: true,
            regex: '^_{1,2}',
          },
          format: null,
          selector: 'property',
        },
        {
          filter: {
            match: true,
            regex: '^(NextResponse|Cookie)$',
          },
          format: null,
          selector: 'property',
        },
        {
          format: ['camelCase', 'UPPER_CASE'],
          selector: 'property',
        },
      ],
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-inferrable-types': 'warn',
      '@typescript-eslint/no-unused-expressions': 'error',
      'import/no-duplicates': ['error', { considerQueryString: true }],
      'import/order': [
        'warn',
        {
          alphabetize: { caseInsensitive: true, order: 'asc' },
          groups: ['builtin', 'external', 'internal', ['parent', 'sibling', 'index']],
          pathGroups: [
            { group: 'internal', pattern: 'app/**', position: 'before' },
            { group: 'internal', pattern: 'lib/**', position: 'after' },
            { group: 'internal', pattern: 'server/**', position: 'after' },
            { group: 'internal', pattern: 'types/**', position: 'after' },
            { group: 'internal', pattern: 'utils/**', position: 'after' },
            { group: 'internal', pattern: 'components/**', position: 'after' },
            { group: 'internal', pattern: '@tests/**', position: 'after' },
          ],
          pathGroupsExcludedImportTypes: ['builtin'],
        },
      ],
      'jsx-a11y/anchor-is-valid': 'warn',
      'jsx-a11y/click-events-have-key-events': 'warn',
      'jsx-a11y/label-has-associated-control': 'error',
      'jsx-a11y/no-autofocus': 'warn',
      'jsx-a11y/no-distracting-elements': 'warn',
      'nest/no-global-isfinite': 'error',
      'nest/no-global-isnan': 'error',
      'nest/no-global-nan': 'error',
      'nest/no-global-parsefloat': 'error',
      'nest/no-global-parseint': 'error',
      'no-console': 'error',
      'no-restricted-imports': [
        'error',
        {
          patterns: ['.*'],
        },
      ],
      quotes: ['error', 'single', { avoidEscape: true }],
      'react-hooks/exhaustive-deps': 'warn',
      'react-hooks/rules-of-hooks': 'error',
      'react/no-array-index-key': 'error',
      'react/prop-types': 'off',
      'react/react-in-jsx-scope': 'off',
    },
  },
  {
    files: ['frontend/src/utils/logger.ts'],
    rules: {
      'no-console': 'off',
    },
  },
  {
    files: [
      'frontend/**/skeletons/**/*.{ts,tsx,js,jsx}',
      'frontend/**/*.skeleton.{ts,tsx,js,jsx}',
    ],
    rules: {
      'react/no-array-index-key': 'off',
    },
  },
  eslintConfigPrettier,
]
