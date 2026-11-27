import { AppError } from 'app/global-error'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

jest.mock('utils/env.client', () => ({
  IDX_URL: 'https://idx.test/',
}))

jest.mock('utils/utility', () => ({
  getCsrfToken: jest.fn().mockResolvedValue('csrf-token'),
}))

describe('fetchAlgoliaData', () => {
  const originalFetch = globalThis.fetch
  const mockFetch = jest.fn()

  beforeEach(() => {
    mockFetch.mockReset()
    globalThis.fetch = mockFetch as unknown as typeof fetch
  })

  afterAll(() => {
    globalThis.fetch = originalFetch
  })

  it('passes the abort signal through to fetch', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ hits: [{ objectID: '1' }], nbPages: 2 }),
    })
    const { signal } = new AbortController()

    const result = await fetchAlgoliaData('users', 'nest', 1, 25, [], signal)

    expect(result).toEqual({ hits: [{ objectID: '1' }], totalPages: 2 })
    expect(mockFetch).toHaveBeenCalledWith('https://idx.test/', expect.objectContaining({ signal }))
  })

  it('rethrows the original error, not an AppError, when the request is aborted', async () => {
    const controller = new AbortController()
    const abortError = new DOMException('Aborted', 'AbortError')
    mockFetch.mockImplementation(async () => {
      controller.abort()
      throw abortError
    })

    await expect(fetchAlgoliaData('users', 'nest', 1, 25, [], controller.signal)).rejects.toBe(
      abortError
    )
  })

  it('still wraps a genuine network failure in an AppError', async () => {
    mockFetch.mockRejectedValue(new TypeError('Failed to fetch'))
    const { signal } = new AbortController()

    await expect(fetchAlgoliaData('users', 'nest', 1, 25, [], signal)).rejects.toMatchObject({
      statusCode: 500,
      message: 'Search service error',
    })
  })

  it('keeps surfacing non-OK responses as an AppError without a signal', async () => {
    mockFetch.mockResolvedValue({ ok: false, status: 503 })

    await expect(fetchAlgoliaData('users', 'nest')).rejects.toBeInstanceOf(AppError)
  })
})
