import { NextResponse } from 'next/server'
import { encode } from 'next-auth/jwt'

export async function POST(request: Request) {
  if (!process.env.NEXT_PUBLIC_E2E_BACKEND_BASE_URL) {
    return new NextResponse(null, { status: 404 })
  }

  let username = ''
  let maxAge: number | undefined
  try {
    const body = (await request.json()) as { maxAge?: number; username?: string }
    username = (body.username ?? '').trim()
    if (typeof body.maxAge === 'number' && Number.isFinite(body.maxAge)) {
      maxAge = body.maxAge
    }
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
    ...(maxAge === undefined ? {} : { maxAge }),
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
