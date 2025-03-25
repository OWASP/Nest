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

beforeAll(() => {
  if (typeof window !== 'undefined') {
    jest.spyOn(window, 'requestAnimationFrame').mockImplementation((cb) => {
      return setTimeout(cb, 0)
    })

    Object.defineProperty(window, 'runAnimationFrameCallbacks', {
      value: () => {},
      configurable: true,
      writable: true,
    })
  }

  global.ResizeObserver = class {
    disconnect() {}
    observe() {}
    unobserve() {}
  }
})

beforeEach(() => {
  jest.spyOn(console, 'error').mockImplementation((...args) => {
    throw new Error(`Console error: ${args.join(' ')}`)
  })

  jest.spyOn(global.console, 'warn').mockImplementation((message) => {
    if (
      typeof message === 'string' &&
      message.includes('[@zag-js/dismissable] node is `null` or `undefined`')
    ) {
      return
    }
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
  global.runAnimationFrameCallbacks = jest.fn()
  global.removeAnimationFrameCallbacks = jest.fn()
})
