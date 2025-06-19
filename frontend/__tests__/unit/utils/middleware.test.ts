import authenticationMiddleware from 'middleware'
import { NextRequest, NextResponse } from 'next/server'
import { getToken } from 'next-auth/jwt'

// Mock the external dependencies
jest.mock('next-auth/jwt', () => ({
  getToken: jest.fn(),
}))

jest.mock('next/server', () => ({
  NextResponse: {
    redirect: jest.fn((url) => ({
      type: 'redirect',
      url: url, // Keep as URL object
    })),
    next: jest.fn(() => ({ type: 'next' })),
  },
}))

describe('Authentication Middleware', () => {
  const mockRequest = (url = 'http://localhost/'): NextRequest =>
    ({
      url,
      headers: new Headers(),
      cookies: {},
    }) as unknown as NextRequest

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('When no authentication token exists', () => {
    const testCases = [
      { description: 'root path', url: 'http://localhost/' },
      { description: 'protected path', url: 'http://localhost/protected' },
      { description: 'with query params', url: 'http://localhost/dashboard?page=1' },
    ]

    testCases.forEach(({ description, url }) => {
      it(`should redirect to login from ${description}`, async () => {
        ;(getToken as jest.Mock).mockResolvedValue(null)
        const request = mockRequest(url)
        const expectedRedirectUrl = new URL('/auth/login', url)

        const result = await authenticationMiddleware(request)

        expect(getToken).toHaveBeenCalledWith({ req: request })
        expect(NextResponse.redirect).toHaveBeenCalledWith(expectedRedirectUrl)

        expect(result.url.toString()).toBe(expectedRedirectUrl.toString())
        expect(result).toEqual({
          type: 'redirect',
          url: expectedRedirectUrl,
        })
      })
    })
  })

  describe('When authentication token exists', () => {
    const testUser = { name: 'Test User', email: 'user@example.com' }

    it('should allow access to protected routes', async () => {
      ;(getToken as jest.Mock).mockResolvedValue(testUser)
      const request = mockRequest('http://localhost/dashboard')

      const result = await authenticationMiddleware(request)

      expect(getToken).toHaveBeenCalledWith({ req: request })
      expect(NextResponse.next).toHaveBeenCalled()
      expect(result).toEqual({ type: 'next' })
    })

    it('should allow access to root path', async () => {
      ;(getToken as jest.Mock).mockResolvedValue(testUser)
      const request = mockRequest()

      const result = await authenticationMiddleware(request)

      expect(NextResponse.next).toHaveBeenCalled()
      expect(result).toEqual({ type: 'next' })
    })
  })
})
