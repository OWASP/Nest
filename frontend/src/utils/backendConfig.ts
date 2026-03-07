/**
 * Search backend configuration
 * Supports switching between Algolia and GraphQL search handlers
 */

export const SEARCH_BACKENDS = {
  algolia: {
    name: 'Algolia',
    description: 'Fast, real-time search powered by Algolia',
    features: ['Full-text search', 'Faceted filtering', 'Real-time updates'],
  },
  graphql: {
    name: 'GraphQL',
    description: 'Dynamic queries with precise filtering',
    features: ['Precise filtering', 'Structured data', 'Flexible queries'],
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
