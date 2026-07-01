import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { AppError, handleAppError } from 'app/global-error'
import { GRAPHQL_URL } from 'utils/env.client'
import { getCsrfToken } from 'utils/utility'

let hasShownGraphQLConnectionError = false

const notifyGraphQLConnectionError = () => {
  if (hasShownGraphQLConnectionError) {
    return
  }

  hasShownGraphQLConnectionError = true
  handleAppError(
    new AppError(
      500,
      'Unable to reach the GraphQL backend. Ensure the backend service is running and NEXT_PUBLIC_GRAPHQL_URL points to a valid /graphql/ endpoint.'
    ),
    { timeout: 12000 }
  )
}

const createApolloClient = () => {
  if (!GRAPHQL_URL) {
    const error = new AppError(
      500,
      'Missing NEXT_PUBLIC_GRAPHQL_URL. Set it in frontend/.env and ensure the backend GraphQL service is running.'
    )
    handleAppError(error)
    return null
  }

  const httpLink = new HttpLink({
    credentials: 'include',
    fetch: async (uri, options) => {
      try {
        return await fetch(uri, options)
      } catch (error) {
        notifyGraphQLConnectionError()
        throw error
      }
    },
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
