import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { getToken } from 'next-auth/jwt'
import crypto from 'crypto'

export async function proxy(request: NextRequest) {

  const nonce = crypto.randomBytes(16).toString('base64')

  // --- Build CSP header ---
  const cspHeader = [
    "default-src 'self'",
    `script-src 'self' 'strict-dynamic' 'nonce-${nonce}' https:`,
    "style-src 'self' 'unsafe-inline'", // required for Next.js styled-jsx
    "img-src 'self' data: https:",
    "font-src 'self'",
    "connect-src 'self' https:",
  ].join('; ')

  // --- Create initial response ---
  const response = NextResponse.next()
  response.headers.set('Content-Security-Policy', cspHeader)
  response.headers.set('x-nonce', nonce) // optional, expose nonce to frontend if needed

  // --- JWT Auth protection for mentorship routes ---
  const protectedPaths = ['/my/mentorship']
  if (protectedPaths.some(path => request.nextUrl.pathname.startsWith(path))) {
    const token = await getToken({ req: request })
    if (!token) {
      const loginUrl = request.nextUrl.clone()
      loginUrl.pathname = '/auth/login'
      return NextResponse.redirect(loginUrl)
    }
  }

  return response
}

// --- Configure which routes this middleware runs on ---
export const config = {
  matcher: ['/(.*)'], // run for all routes to apply CSP
}
