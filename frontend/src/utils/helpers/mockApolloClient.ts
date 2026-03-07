import { ApolloClient, ApolloLink, InMemoryCache, Observable } from '@apollo/client'
export const createMockApolloClient = () => {
  const mockLink = new ApolloLink(() => {
    return new Observable((observer) => {
      observer.next({ data: {} })
      observer.complete()
    })
  })

  return new ApolloClient({
    cache: new InMemoryCache(),
    link: mockLink,
    defaultOptions: {
      watchQuery: { fetchPolicy: 'no-cache', errorPolicy: 'all' },
      query: { fetchPolicy: 'no-cache', errorPolicy: 'all' },
    },
  })
}
