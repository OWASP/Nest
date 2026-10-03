import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'

import { GRAPHQL_URL } from 'utils/env.client'
import { getCsrfToken } from 'utils/utility'

const createApolloClient = () => {
  if (!GRAPHQL_URL) {
    // Only create the error for logging or throwing, do not emit a toast here
    return null
  }

  const httpLink = new HttpLink({
    credentials: 'include',
    uri: GRAPHQL_URL,
  })

  const authLink = setContext(async (_, { headers }) => {
    const csrfToken = await getCsrfToken()

    return {
      headers: {
        ...headers,
        'X-CSRFToken': csrfToken || '',
      },
    }
  })

  return new ApolloClient({
    cache: new InMemoryCache(),
    link: authLink.concat(httpLink),
  })
}
const apolloClient = createApolloClient()

export default apolloClient
