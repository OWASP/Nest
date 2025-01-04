import { SearchResponse } from 'algoliasearch'
import { API_URL } from 'utils/credentials'
import { ENVIRONMENT } from 'utils/credentials'

import { getParamsForIndexName } from 'utils/paramsMapping'

import { client } from 'lib/algoliaClient'
import { handleError } from 'lib/ErrorHandler'
import { AgloliaRequestType, AlgoliaResponseType } from 'lib/types'

export const loadData = async <T>(
  endpoint: string,
  query: string,
  currentPage: number
): Promise<T> => {
  try {
    const response = await fetch(
      `${API_URL}/${endpoint}?` +
        new URLSearchParams({
          q: query,
          page: currentPage.toString(),
        }).toString()
    )
    if (!response.ok) {
      const error = new Error('An unexpected error occurred.')
      handleError(error)
    }
    return await response.json()
  } catch (error) {
    handleError(error)
  }
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
    handleError(error)
    return { hits: [], totalPages: 0 }
  }
}
