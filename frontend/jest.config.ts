export default {
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/components/**',
    '!src/index.tsx',
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
    '^@src/(.*)$': '<rootDir>/src/$1',
    '^components/(.*)$': '<rootDir>/src/components/$1',
    '^utils/(.*)$': '<rootDir>/src/utils/$1',
    '^lib/(.*)$': '<rootDir>/src/lib/$1',
    '^pages/(.*)$': '<rootDir>/src/pages/$1',
    '^@test/(.*)$': '<rootDir>__tests__/src/$1',
  },

}
