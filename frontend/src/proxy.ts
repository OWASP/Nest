// proxy.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { getToken } from 'next-auth/jwt'

export default async function proxy(request: NextRequest) {
  const token = await getToken({ req: request })

  if (!token) {
    return NextResponse.redirect(new URL('/auth/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  // Protected routes.
  matcher: ['/my/mentorship/:path*'],
}
