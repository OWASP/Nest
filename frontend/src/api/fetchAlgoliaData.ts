import { SearchResponse } from 'algoliasearch'
import { AlgoliaRequestType, AlgoliaResponseType } from 'types/algolia'
import { ENVIRONMENT } from 'utils/credentials'
import { getParamsForFilters } from 'utils/filterMapping'
import { client } from 'utils/helpers/algoliaClient'

import { getParamsForIndexName } from 'utils/paramsMapping'
import { AppError } from 'wrappers/ErrorWrapper'

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

    let filters = ''
    let searchQuery = query

    const filterRegex = /(\w+)([:><=!]+)([^ ]+)/g
    let match

    while ((match = filterRegex.exec(query)) !== null) {
      const [fullMatch, attribute, operator, value] = match
      filters += `${attribute}${operator}${value} AND `
      searchQuery = searchQuery.replace(fullMatch, '').trim()
    }

    filters = filters.trim().replace(/AND$/, '')
    filters = getParamsForFilters(indexName, filters)

    if (filterKey) {
      filters = filters ? `(${filters}) AND idx_key:${filterKey}` : `idx_key:${filterKey}`
    }

    const request: AlgoliaRequestType = {
      attributesToHighlight: [],
      hitsPerPage: 25,
      indexName: `${ENVIRONMENT}_${indexName}`,
      page: currentPage - 1,
      query: searchQuery,
      removeWordsIfNoResults: 'allOptional',
      ...params,
    }
    if (filters) {
      request.filters = filters
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
