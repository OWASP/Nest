import { algoliasearch } from 'algoliasearch'
import { ALGOLIA_APP_ID, ALGOLIA_SEARCH_API_KEY } from 'utils/credentials'

export const createAlgoliaClient = () => {
  if (!ALGOLIA_APP_ID || !ALGOLIA_SEARCH_API_KEY) {
    const error = new Error('Algolia keys not found')
    error.name = 'ALGOLIA_CONFIG_ERROR'
    throw error
  }

  return algoliasearch(ALGOLIA_APP_ID, ALGOLIA_SEARCH_API_KEY)
}

export const client = createAlgoliaClient()
