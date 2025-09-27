import '@testing-library/jest-dom'
import { TextEncoder } from 'util'
import React from 'react'
import 'core-js/actual/structured-clone'

global.React = React
global.TextEncoder = TextEncoder

// Add fetch polyfill for jsdom test environment
// Node.js 18+ has native fetch, but jsdom doesn't include it
if (typeof global.fetch === 'undefined') {
  // Use a simple mock fetch for testing
  global.fetch = jest.fn().mockResolvedValue({
    ok: true,
    status: 200,
    statusText: 'OK',
    headers: new Headers(),
    url: '',
    redirected: false,
    type: 'basic' as const,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(''),
    blob: () => Promise.resolve(new Blob()),
    arrayBuffer: () => Promise.resolve(new ArrayBuffer(0)),
    formData: () => Promise.resolve(new FormData()),
    clone: () => ({}) as Response,
    body: null,
    bodyUsed: false,
  } as Response)
}

jest.mock('next-auth/react', () => {
  return {
    ...jest.requireActual('next-auth/react'),
    useSession: () => ({
      data: {
        user: { name: 'Test User', email: 'test@example.com', login: 'testuser', isLeader: true },
        expires: '2099-01-01T00:00:00.000Z',
      },
      status: 'authenticated',
      loading: false,
    }),
  }
})

jest.mock('next/navigation', () => {
  const actual = jest.requireActual('next/navigation')
  const push = jest.fn()
  const replace = jest.fn()
  const prefetch = jest.fn()
  const back = jest.fn()
  const forward = jest.fn()
  const mockRouter = { push, replace, prefetch, back, forward }
  return {
    ...actual,
    useRouter: jest.fn(() => mockRouter),
    useSearchParams: jest.fn(() => new URLSearchParams()),
    useParams: jest.fn(() => ({})),
  }
})

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
