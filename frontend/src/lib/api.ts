import { SearchResponse } from 'algoliasearch'
import { API_URL } from 'utils/credentials'
import { NEST_ENV } from 'utils/credentials'

import { getParamsForIndexName } from 'utils/paramsMapping'

import { client } from 'lib/algoliaClient'
import { AgloliaRequestType, AlgoliaResponseType } from 'lib/types'

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
  currentPage = 0,
  filterKey?: string
): Promise<AlgoliaResponseType<T>> => {
  try {
    const params = getParamsForIndexName(indexName)

    const request: AgloliaRequestType = {
      attributesToHighlight: [],
      hitsPerPage: 25,
      indexName: `${ENVIRONMENT}_${indexName}`,
      page: currentPage - 1,
      query: query,
      removeWordsIfNoResults: 'allOptional',
      ...params,
    }
    if (filterKey) {
      request.filters = `idx_key: ${filterKey}`
    }

    const { results } = await client.search({
      requests: [request],
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
