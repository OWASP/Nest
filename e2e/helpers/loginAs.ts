import crypto from 'node:crypto'
import { Page } from '@playwright/test'
import { EncryptJWT } from 'jose'

const E2E_ALLOWED_USERS = new Set(['e2e-user', 'e2e-mentor', 'e2e-mentee'])
const DEFAULT_MAX_AGE = 30 * 24 * 60 * 60

async function getDerivedEncryptionKey(secret: string, salt = ''): Promise<Uint8Array> {
  const info = `NextAuth.js Generated Encryption Key${salt ? ` (${salt})` : ''}`
  return new Promise<Uint8Array>((resolve, reject) => {
    crypto.hkdf('sha256', secret, salt, info, 32, (err, derivedKey) => {
      if (err) reject(err)
      else resolve(new Uint8Array(derivedKey))
    })
  })
}

async function postJson(page: Page, url: string, data: object, errorLabel: string) {
  const response = await page.request.post(url, {
    data,
    headers: { 'Content-Type': 'application/json' },
  })
  if (!response.ok()) {
    throw new Error(`${errorLabel}: ${response.status()} ${await response.text()}`)
  }
}

export async function loginAs(page: Page, username: string) {
  await postJson(page, '/e2e/login/', { username }, 'e2e login failed')
}

export async function setNextAuthSession(page: Page, username: string, maxAge?: number) {
  const trimmed = username.trim()
  if (!trimmed || !E2E_ALLOWED_USERS.has(trimmed)) {
    throw new Error(`Invalid or disallowed e2e user: ${username}`)
  }

  const secret = process.env.NEXTAUTH_SECRET || 'your-nextauth-secret'
  const encryptionSecret = await getDerivedEncryptionKey(secret)
  const tokenDuration =
    typeof maxAge === 'number' && Number.isFinite(maxAge)
      ? maxAge > 0
        ? maxAge
        : -60
      : DEFAULT_MAX_AGE

  const now = Math.floor(Date.now() / 1000)
  const token = await new EncryptJWT({
    email: `${trimmed}@example.com`,
    isLeader: trimmed === 'e2e-user',
    isMentee: trimmed === 'e2e-mentee',
    isMentor: trimmed === 'e2e-mentor',
    login: trimmed,
    name: trimmed,
    sub: trimmed,
  })
    .setProtectedHeader({ alg: 'dir', enc: 'A256GCM' })
    .setIssuedAt()
    .setExpirationTime(now + tokenDuration)
    .encrypt(encryptionSecret)

  const frontend = new URL(process.env.FRONTEND_URL || 'http://localhost:3000')
  await page.context().addCookies([
    {
      domain: frontend.hostname,
      httpOnly: true,
      name: 'next-auth.session-token',
      path: '/',
      sameSite: 'Lax',
      secure: false,
      value: token,
    },
  ])
}

export async function setInvalidNextAuthSession(page: Page) {
  const frontend = new URL(process.env.FRONTEND_URL || 'http://localhost:3000')
  await page.context().addCookies([
    {
      domain: frontend.hostname,
      name: 'next-auth.session-token',
      path: '/',
      value: 'invalid-session-token',
    },
  ])
}

export async function loginAsPage(page: Page, username: string) {
  await loginAs(page, username)
  await setNextAuthSession(page, username)
}
