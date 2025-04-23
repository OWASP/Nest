import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { cookies } from 'next/headers'
import { fetchCsrfTokenServer } from 'server/fetchCsrfTokenServer'
import { ENVIRONMENT, GRAPHQL_URL, GRAPHQL_URL_DOCKER } from 'utils/credentials'

async function createApolloServerClient() {
  const url = (ENVIRONMENT == 'docker') ? GRAPHQL_URL_DOCKER : GRAPHQL_URL

  const httpLink = createHttpLink({
    uri: url,
    credentials: 'same-origin',
  })

  const authLink = setContext(async (_, { headers }) => {
    let csrfToken = null
    const cookieValue = await getCsrfTokenOnServer()
    csrfToken = cookieValue
    return {
      headers: {
        ...headers,
        'X-CSRFToken': csrfToken || '',
        Cookie: csrfToken ? `csrftoken=${csrfToken}` : '',
      },
    }
  })

  return new ApolloClient({
    cache: new InMemoryCache().restore(globalThis.__APOLLO_STATE__ || {}),
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
