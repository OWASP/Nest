import { NextResponse } from 'next/server'
import { encode } from 'next-auth/jwt'

const E2E_ALLOWED_USERS = new Set(['e2e-user', 'e2e-mentor', 'e2e-mentee'])

export async function POST(request: Request) {
  if (!process.env.NEXT_PUBLIC_E2E_BACKEND_BASE_URL || !process.env.NEXTAUTH_SECRET) {
    return new NextResponse(null, { status: 404 })
  }

  let body: { maxAge?: number; username?: string }
  try {
    body = (await request.json()) as { maxAge?: number; username?: string }
  } catch {
    return NextResponse.json({ ok: false }, { status: 400 })
  }

  const username = (body.username ?? '').trim()
  if (!username || !E2E_ALLOWED_USERS.has(username)) {
    return NextResponse.json({ ok: false }, { status: 400 })
  }

  const { maxAge } = body
  const token = await encode({
    secret: process.env.NEXTAUTH_SECRET,
    token: {
      email: `${username}@example.com`,
      isLeader: username === 'e2e-user',
      isMentee: username === 'e2e-mentee',
      isMentor: username === 'e2e-mentor',
      login: username,
      name: username,
      sub: username,
    },
    ...(typeof maxAge === 'number' && Number.isFinite(maxAge)
      ? { maxAge: maxAge > 0 ? maxAge : -60 }
      : {}),
  })

  const response = NextResponse.json({ ok: true })
  response.cookies.set('next-auth.session-token', token, {
    httpOnly: true,
    path: '/',
    sameSite: 'lax',
    secure: false,
  })
  return response
}
