import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { getCsrfToken, getFilteredIcons } from 'utils/utility'

dayjs.extend(relativeTime)

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

describe('getFilteredIcons', () => {
  const baseIssue = {
    url: 'https://github.com/test/issue/1',
    title: 'Test issue',
    commentsCount: 5,
  }

  test('does not set createdAt icon for malformed date strings', () => {
    const issue = { ...baseIssue, createdAt: 'not-a-date' }
    const result = getFilteredIcons(issue as never, ['createdAt'])
    expect(result['createdAt']).toBeUndefined()
  })

  test('does not set createdAt icon when timestamp is 0', () => {
    const issue = { ...baseIssue, createdAt: 0 }
    const result = getFilteredIcons(issue as never, ['createdAt', 'commentsCount'])
    expect(result['createdAt']).toBeUndefined()
  })

  test('does not set createdAt icon when timestamp is null', () => {
    const issue = { ...baseIssue, createdAt: null }
    const result = getFilteredIcons(issue as never, ['createdAt', 'commentsCount'])
    expect(result['createdAt']).toBeUndefined()
  })

  test('sets createdAt icon with relative time for a valid timestamp', () => {
    const validTimestamp = Math.floor(Date.now() / 1000) - 3600
    const issue = { ...baseIssue, createdAt: validTimestamp }
    const result = getFilteredIcons(issue as never, ['createdAt', 'commentsCount'])
    expect(result['createdAt']).toBe(dayjs.unix(validTimestamp).fromNow())
  })

  test('sets createdAt icon with relative time for a valid ISO string', () => {
    const validIsoString = new Date(Date.now() - 3600000).toISOString()
    const issue = { ...baseIssue, createdAt: validIsoString }
    const result = getFilteredIcons(issue as never, ['createdAt', 'commentsCount'])
    expect(result['createdAt']).toBe(dayjs(validIsoString).fromNow())
  })

  test('still sets other icon fields when createdAt is 0', () => {
    const issue = { ...baseIssue, createdAt: 0 }
    const result = getFilteredIcons(issue as never, ['createdAt', 'commentsCount'])
    expect(result['commentsCount']).toBe(5)
  })
})
