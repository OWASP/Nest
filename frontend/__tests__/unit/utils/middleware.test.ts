import { middleware } from 'middleware'
import { NextResponse } from 'next/server'
import { getToken } from 'next-auth/jwt'

jest.mock('next-auth/jwt', () => ({
    getToken: jest.fn(),
}))

jest.mock('next/server', () => {
    return {
        NextResponse: {
            redirect: jest.fn((url) => ({ redirect: url })),
            next: jest.fn(() => ({ next: true })),
        },
    }
})

describe('middleware', () => {
    const createRequest = (url = 'http://localhost/') => ({ url } as any)

    beforeEach(() => {
        jest.clearAllMocks()
    })

    test('should redirect to /login if no token is found', async () => {
        (getToken as jest.Mock).mockResolvedValue(null)
        const request = createRequest()
        const result = await middleware(request)

        expect(getToken).toHaveBeenCalledWith({ req: request })
        expect(NextResponse.redirect).toHaveBeenCalledWith(new URL('/login', request.url))
        expect(result).toEqual({ redirect: new URL('/login', request.url) })
    })

    test('should call NextResponse.next if token is present', async () => {
        (getToken as jest.Mock).mockResolvedValue({ name: 'User' })
        const request = createRequest()
        const result = await middleware(request)

        expect(getToken).toHaveBeenCalledWith({ req: request })
        expect(NextResponse.next).toHaveBeenCalled()
        expect(result).toEqual({ next: true })
    })
})
