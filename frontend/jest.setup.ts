import '@testing-library/jest-dom'
import { TextEncoder } from 'util'
import dotenv from 'dotenv'
dotenv.config()
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
import React from 'react'

global.React = React
global.TextEncoder = TextEncoder
