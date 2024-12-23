import { algoliasearch, SearchResponse } from 'algoliasearch'

import { AlgoliaResponseType } from './types'
import { APPLICATION_ENV, ALGOLIA_APP_ID, ALGOLIA_API_KEY } from '../utils/credentials'
import logger from '../utils/logger'

if (!ALGOLIA_APP_ID || !ALGOLIA_API_KEY) {
  throw new Error('Algolia api not found.')
}
const client = algoliasearch(ALGOLIA_APP_ID, ALGOLIA_API_KEY)

export const loadAlgoliaData = async <T>(
  indexName: string,
  query: string,
  currentPage: number
): Promise<AlgoliaResponseType<T>> => {
  try {
    const { results } = await client.search({
      requests: [
        {
          indexName: `${APPLICATION_ENV}_${indexName}`,
          query,
          hitsPerPage: 25,
          page: currentPage - 1,
          attributesToHighlight: [],
        },
      ],
    })
    if (results && results.length > 0) {
      const { hits, nbPages } = results[0] as SearchResponse<T>
      return {
        hits: hits as T[],
        pages: nbPages || 0,
      }
    } else {
      return { hits: [], pages: 0 }
    }
  } catch (error) {
    logger.error('Error fetching data from Algolia', error)
    return { hits: [], pages: 0 }
  }
}
