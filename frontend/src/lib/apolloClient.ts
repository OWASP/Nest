import { ApolloClient, HttpLink, InMemoryCache, NormalizedCacheObject } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'

interface CreateApolloClientOptions {
  uri: string | undefined
  credentials: RequestCredentials
  getCsrfToken: () => Promise<string | null>
  ssrMode?: boolean
  includeCsrfCookie?: boolean
  cache?: NormalizedCacheObject
}

export function createApolloClient({
  uri,
  credentials,
  getCsrfToken,
  ssrMode = false,
  includeCsrfCookie = false,
  cache = {},
}: CreateApolloClientOptions) {
  const httpLink = new HttpLink({
    credentials,
    uri,
  })

  const authLink = setContext(async (_, { headers }) => {
    const csrfToken = await getCsrfToken()

    return {
      headers: {
        ...headers,
        'X-CSRFToken': csrfToken ?? '',
        ...(includeCsrfCookie ? { Cookie: csrfToken ? `csrftoken=${csrfToken}` : '' } : {}),
      },
    }
  })

  return new ApolloClient({
    cache: new InMemoryCache().restore(cache),
    link: authLink.concat(httpLink),
    ssrMode,
  })
}