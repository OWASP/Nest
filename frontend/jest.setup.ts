import '@testing-library/jest-dom'
import { TextEncoder } from 'util'
import dotenv from 'dotenv'
import React from 'react'
import 'core-js/actual/structured-clone'

dotenv.config()

global.React = React
global.TextEncoder = TextEncoder

if (!global.structuredClone) {
  global.structuredClone = (val) => JSON.parse(JSON.stringify(val))
}

const originalWarn = console.warn;

console.warn = (...args) => {
  if (typeof args[0] === "string" && args[0].includes("[@zag-js/dismissable] node is `null` or `undefined`")) {
    return;
  }
  originalWarn(...args);
};

beforeEach(() => {
  jest.spyOn(console, 'error').mockImplementation((...args) => {
    throw new Error(`Console error: ${args.join(' ')}`)
  })

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
