import { ApolloClient, createHttpLink, InMemoryCache } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { AppError, handleAppError } from 'app/global-error'
import { GRAPHQL_URL } from 'utils/credentials'
import { getCsrfToken } from 'utils/utility'
const createApolloClient = () => {
  if (!GRAPHQL_URL) {
    const error = new AppError(500, 'Missing GraphQL URL')
    handleAppError(error)
    return null
  }

  const httpLink = createHttpLink({
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
