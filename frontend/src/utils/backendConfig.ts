export const SEARCH_BACKENDS = {
  algolia: {
    name: 'Algolia',
    description: 'Cloud-hosted full-text search with real-time indexing',
  },
  graphql: {
    name: 'GraphQL',
    description: 'Structured queries against the local database with fine-grained control',
  },
} as const

export type SearchBackend = keyof typeof SEARCH_BACKENDS

export function getSearchBackendPreference(): SearchBackend {
  const envBackend = process.env.NEXT_PUBLIC_SEARCH_BACKEND
  if (envBackend && Object.hasOwn(SEARCH_BACKENDS, envBackend)) {
    return envBackend as SearchBackend
  }
  return 'algolia'
}
