import { SearchResponse } from 'algoliasearch'

import { client } from './algoliaClient'
import { AlgoliaResponseType } from './types'
import { API_URL } from '../utils/credentials'
import { NEST_ENV } from '../utils/credentials'
import logger from '../utils/logger'
import { getParamsForIndexName } from '../utils/paramsMapping'
export const loadData = async <T>(
  endpoint: string,
  query: string,
  currentPage: number
): Promise<T> => {
  const response = await fetch(
    `${API_URL}/${endpoint}?` +
      new URLSearchParams({
        q: query,
        page: currentPage.toString(),
      }).toString()
  )
  if (!response.ok) {
    throw new Error(`Failed to fetch data: ${response.statusText}`)
  }
  return await response.json()
}

export const fetchAlgoliaData = async <T>(
  indexName: string,
  query = '',
  currentPage = 0
): Promise<AlgoliaResponseType<T>> => {
  try {
    const params = getParamsForIndexName(indexName)
    const { results } = await client.search({
      requests: [
        {
          indexName: `${NEST_ENV}_${indexName}`,
          query,
          hitsPerPage: 25,
          page: currentPage - 1,
          attributesToHighlight: [],
          ...params,
        },
      ],
    })
    if (results && results.length > 0) {
      const { hits, nbPages } = results[0] as SearchResponse<T>
      return {
        hits: hits as T[],
        totalPages: nbPages || 0,
      }
    } else {
      return { hits: [], totalPages: 0 }
    }
  } catch (error) {
    logger.error('Error fetching data from Algolia', error)
    return { hits: [], totalPages: 0 }
  }
}
