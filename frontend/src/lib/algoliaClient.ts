import { algoliasearch } from 'algoliasearch'
import { ALGOLIA_APP_ID, ALGOLIA_SEARCH_KEY } from 'utils/credentials'

export const createAlgoliaClient = () => {
  if (!ALGOLIA_APP_ID || !ALGOLIA_SEARCH_KEY) {
    throw new Error('Algolia keys not found.')
  }

  return algoliasearch(ALGOLIA_APP_ID, ALGOLIA_SEARCH_KEY)
}

export const client = createAlgoliaClient()
