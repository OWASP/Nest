import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { cookies } from 'next/headers'
import { fetchCsrfTokenServer } from 'server/fetchCsrfTokenServer'

async function createApolloServerClient() {
  const authLink = setContext(async (_, { headers }) => {
    let csrfToken = null
    const cookieValue = await getCsrfTokenOnServer()
    csrfToken = cookieValue
    return {
      headers: {
        ...headers,
        'X-CSRFToken': csrfToken ?? '',
        Cookie: csrfToken ? `csrftoken=${csrfToken}` : '',
      },
    }
  })

  const httpLink = createHttpLink({
    credentials: 'same-origin',
    uri: process.env.NEXT_SERVER_GRAPHQL_URL,
  })

  return new ApolloClient({
    cache: new InMemoryCache().restore(globalThis.__APOLLO_STATE__ ?? {}),
    link: authLink.concat(httpLink),
    ssrMode: true,
  })
}

// This is a no-op Apollo client for end-to-end tests.
const noopApolloClient = { query: async () => ({ data: null }) }

export const apolloServerClient =
  process.env.NEXT_SERVER_DISABLE_SSR === 'true'
    ? noopApolloClient
    : await createApolloServerClient()

export const getCsrfTokenOnServer = async () => {
  const cookieStore = await cookies()
  const csrfCookie = cookieStore.get('csrftoken')

  return csrfCookie ? csrfCookie.value : await fetchCsrfTokenServer()
}
