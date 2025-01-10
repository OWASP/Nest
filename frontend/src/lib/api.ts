import { SearchResponse } from 'algoliasearch'
import { AlgoliaRequestType, AlgoliaResponseType } from 'types/algolia'
import { API_URL } from 'utils/credentials'
import { ENVIRONMENT } from 'utils/credentials'

import { getParamsForIndexName } from 'utils/paramsMapping'

import { client } from 'lib/algoliaClient'
import { AppError } from 'lib/ErrorWrapper'

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
    throw new AppError(
      response.status === 404 ? 404 : 500,
      response.status === 404 ? 'Resource not found' : 'Server error occurred'
    )
  }
  return await response.json()
}

export const fetchAlgoliaData = async <T>(
  indexName: string,
  query = '',
  currentPage = 0,
  filterKey?: string
): Promise<AlgoliaResponseType<T>> => {
  if (!client) {
    throw new AppError(500, 'Search client not initialized')
  }
  try {
    const params = getParamsForIndexName(indexName)
    const request: AlgoliaRequestType = {
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
    if (!results?.length) {
      throw new AppError(404, 'No results found')
    }
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
    if (error instanceof AppError) {
      throw error
    }
    throw new AppError(500, 'Search service error')
  }
}
