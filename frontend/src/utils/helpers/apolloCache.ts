import { InMemoryCache } from '@apollo/client'

export const createApolloCache = () =>
  new InMemoryCache({
    typePolicies: {
      // Projects, chapters and committees share this type and use raw (overlapping) primary
      // keys as `id`, so they must not be normalized by `__typename:id`.
      // eslint-disable-next-line @typescript-eslint/naming-convention
      SubscribedEntityNode: { keyFields: false },
    },
  })
