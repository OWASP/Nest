import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { cookies } from 'next/headers'
import { fetchCsrfTokenServer } from 'server/fetchCsrfTokenServer'

async function createApolloClient() {
  const authLink = setContext(async (_, { headers }) => {
    const { csrfToken, sessionId } = await getRequiredCookies()

    const cookieParts = []
    if (csrfToken) cookieParts.push(`csrftoken=${csrfToken}`)
    if (sessionId) cookieParts.push(`sessionid=${sessionId}`)

    return {
      headers: {
        ...headers,
        'X-CSRFToken': csrfToken ?? '',
        Cookie: cookieParts.join('; '),
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

const noopApolloClient = {
  mutate: async () => ({ data: null }),
  query: async () => ({ data: null }),
}

export const apolloClient =
  process.env.NEXT_SERVER_DISABLE_SSR === 'true' ? noopApolloClient : await createApolloClient()

export const getRequiredCookies = async () => {
  const cookieStore = await cookies()

  const csrfCookie = cookieStore.get('csrftoken')
  const sessionCookie = cookieStore.get('sessionid')
  const csrfToken = csrfCookie?.value ?? (await fetchCsrfTokenServer())
  const sessionId = sessionCookie?.value

  return { csrfToken, sessionId }
}
