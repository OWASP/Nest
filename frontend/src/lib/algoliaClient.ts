import { algoliasearch } from 'algoliasearch'
import { AppError, handleAppError } from 'ErrorWrapper'
import { ALGOLIA_APP_ID, ALGOLIA_SEARCH_API_KEY } from 'utils/credentials'

export const createAlgoliaClient = () => {
  if (!ALGOLIA_APP_ID || !ALGOLIA_SEARCH_API_KEY) {
    const error = new AppError(500, 'Missing Algolia credentials')
    handleAppError(error)
    throw error
  }

  return algoliasearch(ALGOLIA_APP_ID, ALGOLIA_SEARCH_API_KEY)
}

export const client = createAlgoliaClient()
