import type { Config } from 'jest'

const config: Config = {
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/app/api/**',
    '!src/app/**/layout.tsx',
    '!src/components/**',
    '!src/hooks/**',
    '!src/instrumentation.ts',
    '!src/instrumentation-client.ts',
    '!src/reportWebVitals.ts',
    '!src/sentry.server.config.ts',
    '!src/server/**',
    '!src/setupTests.ts',
    '!src/types/**',
    '!src/utils/**',
    '!src/wrappers/**',
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html', 'json-summary'],
  coverageThreshold: {
    global: {
      branches: 75,
      functions: 75,
      lines: 75,
      statements: 75,
    },
  },
  globals: {},
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  testEnvironment: 'jest-environment-jsdom',
  testPathIgnorePatterns: [
    '<rootDir>/__tests__/unit/data/',
    '<rootDir>/__tests__/e2e/',
    '<rootDir>/__tests__/testUtils/',
  ],
  transform: {
    '^.+\\.tsx?$': '@swc/jest',
  },
  moduleNameMapper: {
    '^@unit/(.*)$': '<rootDir>/__tests__/unit/$1',
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(scss|sass|css)$': 'identity-obj-proxy',
  },
  moduleDirectories: ['node_modules', 'src'],
  transformIgnorePatterns: ['<rootDir>/node_modules/(?!@zag-js)'],
}

export default config
