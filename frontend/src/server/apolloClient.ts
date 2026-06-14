import { ApolloClient, InMemoryCache, HttpLink, NormalizedCacheObject } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { cookies } from 'next/headers'
import { mergeApolloHeadersWithCsrf } from 'server/apolloCookieHeader'
import { fetchCsrfTokenServer } from 'server/fetchCsrfTokenServer'

async function createApolloClient() {
  const authLink = setContext(async (_, { headers }) => {
    const csrfToken = await getCsrfTokenOnServer()
    const requestCookieHeader = await getRequestCookieHeaderOnServer()
    const mergedHeaders = mergeApolloHeadersWithCsrf(
      {
        ...headers,
        Cookie: requestCookieHeader,
      },
      csrfToken
    )

    return {
      headers: mergedHeaders,
    }
  })
  const httpLink = new HttpLink({
    credentials: 'same-origin',
    uri: process.env.NEXT_SERVER_GRAPHQL_URL,
  })

  return new ApolloClient({
    cache: new InMemoryCache().restore(
      (globalThis as unknown as { __APOLLO_STATE__?: NormalizedCacheObject }).__APOLLO_STATE__ ?? {}
    ),
    link: authLink.concat(httpLink),
    ssrMode: true,
  })
}

// This is a no-op Apollo client for end-to-end tests.
const noopApolloClient = {
  mutate: async () => ({ data: null }),
  query: async () => ({ data: null }),
}
export const apolloClient =
  process.env.NEXT_SERVER_DISABLE_SSR === 'true' ? noopApolloClient : await createApolloClient()

export const getCsrfTokenOnServer = async () => {
  const cookieStore = await cookies()
  const csrfCookie = cookieStore.get('csrftoken')

  return csrfCookie ? csrfCookie.value : await fetchCsrfTokenServer()
}

export const getRequestCookieHeaderOnServer = async () => {
  const cookieStore = await cookies()

  return cookieStore
    .getAll()
    .map(({ name, value }) => `${name}=${value}`)
    .join('; ')
}
