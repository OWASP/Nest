import { getCSRFToken } from 'utils/utility'

describe('utility tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: '',
    })
  })

  test('returns CSRF token when it exists in cookies', () => {
    document.cookie = 'csrftoken=abc123; otherkey=xyz789'
    expect(getCSRFToken()).toBe('abc123')
  })

  test('returns undefined when no cookies are present', () => {
    document.cookie = ''
    expect(getCSRFToken()).toBeUndefined()
  })

  test('returns undefined when csrftoken cookie is not present', () => {
    document.cookie = 'someid=xyz789; othercookie=123'
    expect(getCSRFToken()).toBeUndefined()
  })

  test('returns first csrftoken value when multiple cookies exist', () => {
    document.cookie = 'csrftoken=first; csrftoken=second; otherid=xyz789'
    expect(getCSRFToken()).toBe('first')
  })

  test('handles cookie with no value', () => {
    document.cookie = 'csrftoken=; otherid=xyz789'
    expect(getCSRFToken()).toBe('')
  })

  test('handles malformed cookie string', () => {
    document.cookie = 'csrftoken; otherid=xyz789'
    expect(getCSRFToken()).toBeUndefined()
  })
})
