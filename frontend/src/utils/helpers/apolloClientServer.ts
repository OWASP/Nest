import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { cookies } from 'next/headers'
import { fetchCsrfTokenServer } from 'server/fetchCsrfTokenServer'
import { GRAPHQL_URL } from 'utils/credentials'

async function createApolloServerClient() {
  const httpLink = createHttpLink({
    uri: GRAPHQL_URL,
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

export const apolloServerClient = await createApolloServerClient()

export const getCsrfTokenOnServer = async () => {
  const cookieStore = await cookies()
  const csrfCookie = cookieStore.get('csrftoken')
  if (!csrfCookie) {
    return await fetchCsrfTokenServer()
  }
  return csrfCookie?.value
}
