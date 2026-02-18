import { mergeApolloHeadersWithCsrf, mergeCookieHeader } from 'server/apolloCookieHeader'

describe('apolloCookieHeader', () => {
  test('preserves incoming session and auth cookies while appending csrftoken', () => {
    const headers = mergeApolloHeadersWithCsrf(
      {
        cookie: 'sessionid=session123; auth_token=auth456',
      },
      'csrf789'
    )

    expect(headers.cookie).toBe('sessionid=session123; auth_token=auth456; csrftoken=csrf789')
    expect(headers['X-CSRFToken']).toBe('csrf789')
  })

  test('sets csrftoken cookie and X-CSRFToken when no incoming cookie header exists', () => {
    const headers = mergeApolloHeadersWithCsrf(undefined, 'csrf123')

    expect(headers.Cookie).toBe('csrftoken=csrf123')
    expect(headers['X-CSRFToken']).toBe('csrf123')
  })

  test('replaces existing csrftoken cookie without creating duplicates', () => {
    const mergedCookie = mergeCookieHeader(
      'sessionid=session123; csrftoken=old1; auth_token=auth456; csrftoken=old2',
      'newcsrf'
    )

    expect(mergedCookie).toBe('sessionid=session123; auth_token=auth456; csrftoken=newcsrf')
    expect((mergedCookie.match(/csrftoken=/g) ?? []).length).toBe(1)
  })

  test('handles Cookie and cookie header casing by keeping a single cookie header', () => {
    const headers = mergeApolloHeadersWithCsrf(
      {
        Cookie: 'sessionid=session123',
        cookie: 'auth_token=auth456; csrftoken=old',
      },
      'newcsrf'
    )

    expect(headers.Cookie).toBe('sessionid=session123; auth_token=auth456; csrftoken=newcsrf')
    expect(headers).not.toHaveProperty('cookie')
  })

  test('preserves incoming cookies when csrf token is missing', () => {
    const headers = mergeApolloHeadersWithCsrf(
      {
        Cookie: 'sessionid=session123; auth_token=auth456',
      },
      null
    )

    expect(headers.Cookie).toBe('sessionid=session123; auth_token=auth456')
    expect(headers['X-CSRFToken']).toBe('')
  })

  test('preserves non-cookie headers while merging cookies and csrf', () => {
    const headers = mergeApolloHeadersWithCsrf(
      {
        authorization: 'Bearer token123',
        cookie: 'sessionid=session123',
      },
      'csrf789'
    )

    expect(headers.authorization).toBe('Bearer token123')
    expect(headers.cookie).toBe('sessionid=session123; csrftoken=csrf789')
    expect(headers['X-CSRFToken']).toBe('csrf789')
  })
})
