import { gql, InMemoryCache } from '@apollo/client'
import { createApolloCache } from 'utils/helpers/apolloCache'

const QUERY = gql`
  query GetMySnapshotSubscriptions {
    mySnapshotSubscriptions {
      id
      projects {
        id
        key
        name
      }
      chapters {
        id
        key
        name
      }
      committees {
        id
        key
        name
      }
    }
  }
`

// A project, a chapter and a committee that share the same raw primary key.
const DATA = {
  mySnapshotSubscriptions: [
    {
      __typename: 'SnapshotSubscriptionNode',
      id: btoa('SnapshotSubscriptionNode:1'),
      projects: [{ __typename: 'SubscribedEntityNode', id: 1, key: 'nest', name: 'OWASP Nest' }],
      chapters: [
        { __typename: 'SubscribedEntityNode', id: 1, key: 'aarhus', name: 'OWASP Aarhus' },
      ],
      committees: [
        {
          __typename: 'SubscribedEntityNode',
          id: 1,
          key: 'projects',
          name: 'Projects Committee',
        },
      ],
    },
  ],
}

const writeAndReadNames = (cache: InMemoryCache) => {
  cache.writeQuery({ query: QUERY, data: DATA })
  const subscription = cache.readQuery<typeof DATA>({ query: QUERY })?.mySnapshotSubscriptions[0]

  return [
    subscription?.projects[0].name,
    subscription?.chapters[0].name,
    subscription?.committees[0].name,
  ]
}

describe('createApolloCache', () => {
  it('keeps subscribed entities with the same id apart', () => {
    const cache = createApolloCache()

    expect(writeAndReadNames(cache)).toEqual(['OWASP Nest', 'OWASP Aarhus', 'Projects Committee'])
    expect(cache.extract()).not.toHaveProperty('SubscribedEntityNode:1')
  })

  it('would merge them without the SubscribedEntityNode type policy', () => {
    const names = writeAndReadNames(new InMemoryCache())

    expect(new Set(names).size).toBe(1)
  })
})
