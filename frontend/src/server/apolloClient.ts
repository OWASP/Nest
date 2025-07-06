import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { cookies } from 'next/headers'
import { getSession } from 'next-auth/react'
import { fetchCsrfTokenServer } from 'server/fetchCsrfTokenServer'
import { SessionWithRole } from 'types/program'

async function createApolloClient() {
  const authLink = setContext(async (_, { headers }) => {
    let csrfToken = null
    const cookieValue = await getCsrfTokenOnServer()
    const session = await getSession()
    const accessToken = (session as SessionWithRole)?.accessToken
    csrfToken = cookieValue
    return {
      headers: {
        ...headers,
        'X-CSRFToken': csrfToken ?? '',
        Cookie: csrfToken ? `csrftoken=${csrfToken}` : '',
        // eslint-disable-next-line @typescript-eslint/naming-convention
        Authorization: accessToken ? `Bearer ${accessToken}` : '',
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
