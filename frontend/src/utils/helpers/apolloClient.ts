import { ApolloClient, InMemoryCache } from '@apollo/client'
import { GRAPHQL_URI } from 'utils/credentials'
import { AppError, handleAppError } from 'wrappers/ErrorWrapper'

const createApolloClient = () => {
  const GRAPHQL_URL = GRAPHQL_URI
  if (!GRAPHQL_URL) {
    const error = new AppError(500, 'Missing GraphQL URI')
    handleAppError(error)
    return null
  }

  return new ApolloClient({
    uri: GRAPHQL_URL,
    cache: new InMemoryCache(),
  })
}
const apolloClient = createApolloClient()

export default apolloClient
