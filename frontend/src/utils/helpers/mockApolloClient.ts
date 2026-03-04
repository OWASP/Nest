import { ApolloClient, InMemoryCache, ApolloLink, Observable } from '@apollo/client'

/**
 * Creates a mock Apollo Client for testing purposes.
 * This client returns empty results for all queries instead of making HTTP requests.
 */
export const createMockApolloClient = () => {
  const mockLink = new ApolloLink((_operation) => {
    return new Observable((observer) => {
      observer.next({
        data: {},
      })
      observer.complete()
    })
  })

  return new ApolloClient({
    cache: new InMemoryCache(),
    link: mockLink,
    defaultOptions: {
      watchQuery: {
        fetchPolicy: 'no-cache',
        errorPolicy: 'all',
      },
      query: {
        fetchPolicy: 'no-cache',
        errorPolicy: 'all',
      },
    },
  })
}
