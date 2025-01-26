import { ApolloClient, InMemoryCache } from '@apollo/client'
import { GRAPHQL_URL } from 'utils/credentials'
import { AppError, handleAppError } from 'wrappers/ErrorWrapper'

const createApolloClient = () => {
  if (!GRAPHQL_URL) {
    const error = new AppError(500, 'Missing GraphQL URL')
    handleAppError(error)
    return null
  }

  return new ApolloClient({
    cache: new InMemoryCache(),
    uri: GRAPHQL_URL,
  })
}
const apolloClient = createApolloClient()

export default apolloClient
