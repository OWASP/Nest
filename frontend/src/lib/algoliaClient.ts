import { algoliasearch } from 'algoliasearch'
import { ALGOLIA_APP_ID, ALGOLIA_SEARCH_API_KEY } from 'utils/credentials'
import { handleError } from 'lib/ErrorHandler'

export const createAlgoliaClient = () => {
  if (!ALGOLIA_APP_ID || !ALGOLIA_SEARCH_API_KEY) {
    handleError(new Error('something went wrong'))
  }

  return algoliasearch(ALGOLIA_APP_ID, ALGOLIA_SEARCH_API_KEY)
}

export const client = createAlgoliaClient()
