import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { mockApolloClient } from '@e2e/data/mockApolloServerClient'
import { cookies } from 'next/headers'
import { fetchCsrfTokenServer } from 'server/fetchCsrfTokenServer'

async function createApolloServerClient() {
  const httpLink = createHttpLink({
    uri: process.env.NEXT_SERVER_GRAPHQL_URL,
    credentials: 'same-origin',
  })

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

  return new ApolloClient({
    cache: new InMemoryCache().restore(globalThis.__APOLLO_STATE__ ?? {}),
    link: authLink.concat(httpLink),
    ssrMode: true,
  })
}

export const apolloServerClient =
  process.env.IS_E2E === 'true' ? mockApolloClient : await createApolloServerClient()

export const getCsrfTokenOnServer = async () => {
  const cookieStore = await cookies()
  const csrfCookie = cookieStore.get('csrftoken')
  if (!csrfCookie) {
    return await fetchCsrfTokenServer()
  }
  return csrfCookie?.value
}
