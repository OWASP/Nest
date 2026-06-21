import js from '@eslint/js'
import globals from 'globals'
import tseslint from 'typescript-eslint'
import { defineConfig } from 'eslint/config'
import playwright from 'eslint-plugin-playwright'
import eslintConfigPrettier from 'eslint-config-prettier'

export default defineConfig([
  { ignores: ['node_modules', 'playwright-report', 'test-results'] },
  tseslint.configs.recommended,
  js.configs.recommended,
  {
    files: ['**/*.{js,ts}'],
    languageOptions: { globals: { ...globals.node } },
    rules: {
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
    },
  },
  {
    files: ['**/*.{ts}'],
    extends: [playwright.configs['flat/recommended']],
  },
  eslintConfigPrettier,
])
