export default {
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/components/**',
    '!src/**/index.ts',
    '!src/lib/**',
    '!src/main.tsx',
    '!src/reportWebVitals.ts',
    '!src/setupTests.ts',
    '!src/utils/**',
    '!src/ErrorWrapper.tsx',
    '!src/sentry.config.ts',
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
  preset: 'ts-jest',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  testEnvironment: 'jest-environment-jsdom',
  testPathIgnorePatterns: ['<rootDir>/__tests__/src/data/'],
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
  moduleNameMapper: {
    '^@tests/(.*)$': '<rootDir>/__tests__/src/$1',
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(scss|sass|css)$': 'identity-obj-proxy',
  },
  moduleDirectories: ['node_modules', 'src'],
}
