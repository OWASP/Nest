import { test, expect } from '@playwright/test'

test.describe('Well-known security disclosure files', () => {
  test('serves security.txt', async ({ request }) => {
    const response = await request.get('/.well-known/security.txt')

    expect(response.status()).toBe(200)
    expect(response.headers()['content-type'] ?? '').toMatch(/text\/plain/)

    const body = await response.text()
    expect(body).toContain('Canonical: https://nest.owasp.org/.well-known/security.txt')
    expect(body).toContain('Contact: https://github.com/OWASP/Nest/security/advisories/new')
    expect(body).toContain('Contact: mailto:nest+security@owasp.org')
    expect(body).toContain('Encryption: https://nest.owasp.org/.well-known/pgp-key.txt')
    expect(body).toContain('Expires:')
    expect(body).toContain('Policy: https://github.com/OWASP/Nest/blob/main/SECURITY.md')
  })

  test('serves pgp-key.txt', async ({ request }) => {
    const response = await request.get('/.well-known/pgp-key.txt')

    expect(response.status()).toBe(200)
    expect(response.headers()['content-type'] ?? '').toMatch(/text\/plain/)

    const body = await response.text()
    expect(body).toContain('BEGIN PGP PUBLIC KEY BLOCK')
    expect(body).toContain('END PGP PUBLIC KEY BLOCK')
  })
})
