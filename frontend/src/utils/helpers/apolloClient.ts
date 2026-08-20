import { AppError, handleAppError } from 'app/global-error'
import { createApolloClient } from 'lib/apolloClient'
import { GRAPHQL_URL } from 'utils/env.client'
import { getCsrfToken } from 'utils/utility'

const createClientApolloClient = () => {
  if (!GRAPHQL_URL) {
    const error = new AppError(500, 'Missing GraphQL URL')
    handleAppError(error)
    return null
  }

  return createApolloClient({
    uri: GRAPHQL_URL,
    credentials: 'include',
    getCsrfToken,
  })
}
const apolloClient = createClientApolloClient()

export default apolloClient