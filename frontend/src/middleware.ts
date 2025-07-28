import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { getToken } from 'next-auth/jwt'

export default async function authenticationMiddleware(request: NextRequest) {
  const token = await getToken({ req: request })
  if (!token) {
    return NextResponse.redirect(new URL('/auth/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  //protected route
  matcher: [
    '/mentorship',
    '/mentorship/programs',
    '/mentorship/programs/create',
    '/mentorship/programs/:programId',
    '/mentorship/programs/:programId/modules/create',
    '/mentorship/programs/:programId/edit',
    '/mentorship/programs/:programId/modules/:moduleId',
    '/mentorship/programs/:programId/modules/:moduleId/edit',
    '/my/mentorship',
  ],
}
