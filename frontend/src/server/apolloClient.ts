import { NormalizedCacheObject } from '@apollo/client'
import { cookies } from 'next/headers'
import { createApolloClient } from 'lib/apolloClient'
import { fetchCsrfTokenServer } from 'server/fetchCsrfTokenServer'

export const getCsrfTokenOnServer = async () => {
  const cookieStore = await cookies()
  const csrfCookie = cookieStore.get('csrftoken')

  return csrfCookie ? csrfCookie.value : await fetchCsrfTokenServer()
}

// This is a no-op Apollo client for end-to-end tests.
const noopApolloClient = {
  mutate: async () => ({ data: null }),
  query: async () => ({ data: null }),
}
export const apolloClient =
  process.env.NEXT_SERVER_DISABLE_SSR === 'true'
    ? noopApolloClient
    : createApolloClient({
        uri: process.env.NEXT_SERVER_GRAPHQL_URL,
        credentials: 'same-origin',
        getCsrfToken: getCsrfTokenOnServer,
        ssrMode: true,
        includeCsrfCookie: true,
        cache: (globalThis as unknown as { __APOLLO_STATE__?: NormalizedCacheObject }).__APOLLO_STATE__ ?? {},
      })