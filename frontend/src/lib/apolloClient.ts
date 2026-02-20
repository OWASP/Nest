import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { GRAPHQL_URL } from 'utils/env.client'
import { getCsrfToken } from 'utils/utility'
import { AppError, handleAppError } from 'utils/appError'

let getCsrfTokenOnServer: (() => Promise<string>) | undefined
let fetchCsrfTokenServer: (() => Promise<string>) | undefined
let cookies: (() => Promise<any>) | undefined

if (typeof window === 'undefined') {
  try {
    getCsrfTokenOnServer = async function () {
      if (!cookies) {
        cookies = (await import('next/headers')).cookies
      }
      if (!fetchCsrfTokenServer) {
        fetchCsrfTokenServer = (await import('server/fetchCsrfTokenServer')).fetchCsrfTokenServer
      }
      const cookieStore = await cookies()
      const csrfCookie = cookieStore.get('csrftoken')
      return csrfCookie ? csrfCookie.value : await fetchCsrfTokenServer()
    }
  } catch {
    getCsrfTokenOnServer = async function () { return '' }
  }
}

function createApolloClient(): ApolloClient {
  if (typeof window === 'undefined') {
    if (process.env.NEXT_SERVER_DISABLE_SSR === 'true') {
      return {
        mutate: async () => ({ data: null }),
        query: async () => ({ data: null })
      } as unknown as ApolloClient
    }
    const httpLink = new HttpLink({
      credentials: 'same-origin',
      uri: process.env.NEXT_SERVER_GRAPHQL_URL,
    })
    const authLink = setContext(function (_, { headers }) {
      return getCsrfTokenOnServer!().then(csrfToken => ({
        headers: {
          ...headers,
          'X-CSRFToken': csrfToken ?? '',
          Cookie: csrfToken ? `csrftoken=${csrfToken}` : '',
        },
      }))
    })
    return new ApolloClient({
      cache: new InMemoryCache().restore(
        (globalThis as any).__APOLLO_STATE__ ?? {}
      ),
      link: authLink.concat(httpLink),
      ssrMode: true,
    })
  }
  if (!GRAPHQL_URL) {
    const error = new AppError(500, 'Missing GraphQL URL')
    handleAppError(error)
    throw error
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

const apolloClient: ApolloClient = createApolloClient()

export { apolloClient }
export default apolloClient
