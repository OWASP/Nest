import '@testing-library/jest-dom'
import { toHaveNoViolations } from 'jest-axe'
import React from 'react'

globalThis.React = React

// Mock framer-motion due to how Jest 30 ESM resolution treats
// motion-dom's internal .mjs imports as "outside test scope".
jest.mock('framer-motion', () => {
  return {
    ...jest.requireActual('framer-motion'),
    LazyMotion: ({ children }) => children,
  }
})

jest.mock('next-auth/react', () => {
  return {
    ...jest.requireActual('next-auth/react'),
    useSession: () => ({
      data: {
        expires: '2099-01-01T00:00:00.000Z',
        user: { name: 'Test User', email: 'test@example.com', login: 'testuser', isLeader: true },
      },
      loading: false,
      status: 'authenticated',
    }),
  }
})

jest.mock('next/navigation', () => {
  const actual = jest.requireActual('next/navigation')
  const back = jest.fn()
  const forward = jest.fn()
  const prefetch = jest.fn()
  const push = jest.fn()
  const replace = jest.fn()

  const mockRouter = { push, replace, prefetch, back, forward }

  return {
    ...actual,
    useParams: jest.fn(() => ({})),
    usePathname: jest.fn(() => '/'),
    useRouter: jest.fn(() => mockRouter),
    useSearchParams: jest.fn(() => new URLSearchParams()),
  }
})

jest.mock('next/link', () => ({
  __esModule: true,
  default: function MockedLink({
    children,
    href,
    className,
    onClick,
    ...props
  }: {
    children: React.ReactNode
    href?: string
    className?: string
    onClick?: (e: React.MouseEvent<HTMLAnchorElement>) => void
    [key: string]: unknown
  }) {
    return React.createElement(
      'a',
      {
        href,
        className,
        ...props,
        onClick: (e) => {
          e.preventDefault()
          onClick?.(e as React.MouseEvent<HTMLAnchorElement>)
        },
      },
      children
    )
  },
}))

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({
    src,
    alt,
    fill,
    objectFit,
    ...props
  }: {
    src: string
    alt: string
    fill?: boolean
    objectFit?: 'fill' | 'contain' | 'cover' | 'none' | 'scale-down'
    [key: string]: unknown
  }) =>
    React.createElement('img', {
      src,
      alt,
      style: fill ? { objectFit: objectFit as React.CSSProperties['objectFit'] } : undefined,
      ...props,
    }),
}))

beforeAll(() => {
  if (globalThis !== undefined) {
    jest.spyOn(globalThis, 'requestAnimationFrame').mockImplementation((cb) => {
      return setTimeout(cb, 0)
    })

    Object.defineProperty(globalThis, 'runAnimationFrameCallbacks', {
      value: () => {},
      configurable: true,
      writable: true,
    })
  }

  globalThis.ResizeObserver = class {
    disconnect() {} // NOSONAR: empty mock implementation for test environment.
    observe() {} // NOSONAR: empty mock implementation for test environment.
    unobserve() {} // NOSONAR: empty mock implementation for test environment.
  }
})

beforeEach(() => {
  jest.spyOn(console, 'error').mockImplementation((...args) => {
    throw new Error(`Console error: ${args.join(' ')}`)
  })

  jest.spyOn(globalThis.console, 'warn').mockImplementation((message) => {
    if (
      typeof message === 'string' &&
      message.includes('[@zag-js/dismissable] node is `null` or `undefined`')
    ) {
      return
    }
  })

  Object.defineProperty(globalThis, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation((query) => ({
      matches: false,
      media: query,
      onchange: null,
      addEventListener: jest.fn(),
      addListener: jest.fn(),
      dispatchEvent: jest.fn(),
      removeEventListener: jest.fn(),
      removeListener: jest.fn(),
    })),
  })

  globalThis.removeAnimationFrameCallbacks = jest.fn()
  globalThis.runAnimationFrameCallbacks = jest.fn()
})

jest.mock('ics', () => {
  return {
    __esModule: true,
    createEvent: jest.fn(),
  }
})

expect.extend(toHaveNoViolations)
