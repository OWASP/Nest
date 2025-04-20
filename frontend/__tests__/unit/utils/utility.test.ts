import { getCsrfToken } from 'utils/utility'

jest.mock('server/fetchCsrfToken', () => ({
  fetchCsrfToken: jest.fn(() => Promise.resolve('abc123')),
}))

describe('utility tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: '',
    })
  })

  test('returns CSRF token when it exists in cookies', async () => {
    document.cookie = 'csrftoken=abc123; otherkey=xyz789'
    const result = await getCsrfToken()
    expect(result).toBe('abc123')
  })

  test('returns new token when no cookies are present', async () => {
    document.cookie = ''
    const result = await getCsrfToken()
    expect(result).toBe('abc123')
  })

  test('returns new csrftoken when csrftoken cookie is not present', async () => {
    document.cookie = 'someid=xyz789; othercookie=123'
    const result = await getCsrfToken()
    expect(result).toBe('abc123')
  })

  test('returns first csrftoken value when multiple cookies exist', async () => {
    document.cookie = 'csrftoken=first; csrftoken=second; otherid=xyz789'
    const result = await getCsrfToken()
    expect(result).toBe('first')
  })

  test('handles cookie with no value', async () => {
    document.cookie = 'csrftoken=; otherid=xyz789'
    const result = await getCsrfToken()
    expect(result).toBe('abc123')
  })

  test('handles malformed cookie string', async () => {
    document.cookie = 'csrftoken; otherid=xyz789'
    const result = await getCsrfToken()
    expect(result).toBe('abc123')
  })
})
