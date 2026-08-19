import { encode } from 'next-auth/jwt'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  if (!process.env.NEXT_PUBLIC_E2E_BACKEND_BASE_URL) {
    return new NextResponse(null, { status: 404 })
  }

  let username = ''
  try {
    const body = (await request.json()) as { username?: string }
    username = (body.username ?? '').trim()
  } catch {
    return NextResponse.json({ ok: false }, { status: 400 })
  }

  if (!username) {
    return NextResponse.json({ ok: false }, { status: 400 })
  }

  const token = await encode({
    secret: process.env.NEXTAUTH_SECRET ?? '',
    token: {
      email: `${username}@example.com`,
      isLeader: false,
      isMentee: username === 'e2e-mentee',
      isMentor: username === 'e2e-mentor',
      login: username,
      name: username,
      sub: username,
    },
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
