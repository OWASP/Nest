type ApolloHeaders = Record<string, string | undefined>

const COOKIE_HEADER_NAME = 'cookie'
const CSRF_COOKIE_NAME = 'csrftoken'

const splitCookieHeader = (cookieHeader: string) => {
  return cookieHeader
    .split(';')
    .map((cookie) => cookie.trim())
    .filter(Boolean)
}

const getCookieName = (cookie: string) => {
  return cookie.split('=')[0]?.trim().toLowerCase() ?? ''
}

export const mergeCookieHeader = (existingCookieHeader: string, csrfToken: string | null) => {
  const existingCookies = splitCookieHeader(existingCookieHeader)

  if (!csrfToken) {
    return existingCookies.join('; ')
  }

  const cookiesWithoutCsrf = existingCookies.filter(
    (cookie) => getCookieName(cookie) !== CSRF_COOKIE_NAME
  )
  cookiesWithoutCsrf.push(`${CSRF_COOKIE_NAME}=${csrfToken}`)

  return cookiesWithoutCsrf.join('; ')
}

export const mergeApolloHeadersWithCsrf = (
  headers: ApolloHeaders | undefined,
  csrfToken: string | null
): ApolloHeaders => {
  const mergedHeaders: ApolloHeaders = { ...(headers ?? {}) }
  const cookieHeaderKeys = Object.keys(mergedHeaders).filter(
    (key) => key.toLowerCase() === COOKIE_HEADER_NAME
  )
  const cookieHeaderKey =
    cookieHeaderKeys.find((key) => key === 'Cookie') ?? cookieHeaderKeys[0] ?? 'Cookie'
  const existingCookieHeader = cookieHeaderKeys
    .map((key) => mergedHeaders[key])
    .filter((value): value is string => typeof value === 'string')
    .join('; ')

  for (const key of cookieHeaderKeys) {
    delete mergedHeaders[key]
  }

  return {
    ...mergedHeaders,
    'X-CSRFToken': csrfToken ?? '',
    [cookieHeaderKey]: mergeCookieHeader(existingCookieHeader, csrfToken),
  }
}
