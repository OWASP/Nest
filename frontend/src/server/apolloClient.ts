import { ApolloClient, InMemoryCache, HttpLink, NormalizedCacheObject } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { cookies } from 'next/headers'
import { fetchCsrfTokenServer } from 'server/fetchCsrfTokenServer'

declare global {
  var __APOLLO_STATE__: NormalizedCacheObject | undefined
}

async function createApolloClient() {
  const authLink = setContext(
    async (_: unknown, { headers }: { headers?: Record<string, string> }) => {
      const csrfToken = await getCsrfTokenOnServer()
      return {
        headers: {
          ...headers,
          'X-CSRFToken': csrfToken ?? '',
          Cookie: csrfToken ? `csrftoken=${csrfToken}` : '',
        },
      }
    }
  )
  const httpLink = new HttpLink({
    credentials: 'same-origin',
    uri: process.env.NEXT_SERVER_GRAPHQL_URL,
  })

  return new ApolloClient({
    cache: new InMemoryCache().restore(globalThis.__APOLLO_STATE__ || {}),
    link: authLink.concat(httpLink),
    ssrMode: true,
  })
}

// This is a no-op Apollo client for end-to-end tests.
const noopApolloClient = {
  mutate: async (): Promise<{ data: unknown }> => ({ data: null }),
  query: async (): Promise<{ data: unknown }> => ({ data: null }),
}
export const apolloClient =
  process.env.NEXT_SERVER_DISABLE_SSR === 'true' ? noopApolloClient : await createApolloClient()

export const getCsrfTokenOnServer = async () => {
  const cookieStore = await cookies()
  const csrfCookie = cookieStore.get('csrftoken')

  return csrfCookie ? csrfCookie.value : await fetchCsrfTokenServer()
}
