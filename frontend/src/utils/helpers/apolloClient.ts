import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { AppError, handleAppError } from 'app/global-error'
import { GRAPHQL_URL } from 'utils/env.client'
import { getCsrfToken } from 'utils/utility'
const createApolloClient = () => {
  if (!GRAPHQL_URL) {
    const error = new AppError(500, 'Missing GraphQL URL')
    handleAppError(error)
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
    cache: new InMemoryCache({
      typePolicies: {
        // Projects, chapters and committees share this type and use raw (overlapping) primary
        // keys as `id`, so they must not be normalized by `__typename:id`.
        // eslint-disable-next-line @typescript-eslint/naming-convention
        SubscribedEntityNode: { keyFields: false },
      },
    }),
    link: authLink.concat(httpLink),
  })
}
const apolloClient = createApolloClient()

export default apolloClient
