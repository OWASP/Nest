import '@testing-library/jest-dom'
import { TextEncoder } from 'util'
beforeEach(() => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation((query) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    })),
  })
})
jest.mock('@algolia/autocomplete-theme-classic', () => ({}))

global.TextEncoder = TextEncoder
