import { SearchResponse } from 'algoliasearch'
import { API_URL } from 'utils/credentials'
import { NEST_ENV } from 'utils/credentials'

import { getParamsForIndexName } from 'utils/paramsMapping'

import { client } from 'lib/algoliaClient'
import { AlgoliaResponseType } from 'lib/types'

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
    const error = new Error('API request failed')
    error.name = response.status === 429 ? 'RATE_LIMIT' : 'NETWORK_ERROR'
    throw error
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
    if (error instanceof Error && error.message.includes('timeout')) {
      const timeoutError = new Error('Search operation timed out')
      timeoutError.name = 'SEARCH_TIMEOUT'
      throw timeoutError
    }
    throw error
  }
}
