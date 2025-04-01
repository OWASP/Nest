import { ApolloClient, createHttpLink, InMemoryCache } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { GRAPHQL_URL } from 'utils/credentials'
import { getCSRFToken } from 'utils/utility'
import { AppError, handleAppError } from 'wrappers/ErrorWrapper'

const createApolloClient = () => {
  if (!GRAPHQL_URL) {
    const error = new AppError(500, 'Missing GraphQL URL')
    handleAppError(error)
    return null
  }

  const httpLink = createHttpLink({
    uri: GRAPHQL_URL,
    credentials: 'include',
  })

  const authLink = setContext((_, { headers }) => {
    return {
      headers: {
        ...headers,
        'X-CSRFToken': getCSRFToken() || '',
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
