import { SearchResponse } from 'algoliasearch'
import { AlgoliaRequestType, AlgoliaResponseType } from 'types/algolia'
import { ENVIRONMENT } from 'utils/credentials'
import { client } from 'utils/helpers/algoliaClient'

import { getParamsForIndexName } from 'utils/paramsMapping'
import { AppError } from 'wrappers/ErrorWrapper'
import { removeIdxPrefix } from './utility'

export const fetchAlgoliaData = async <T>(
  indexName: string,
  query = '',
  currentPage = 0,
  filterKey?: string,
  activeOnly = false,
  hitsPerPage = 25
): Promise<AlgoliaResponseType<T>> => {
  if (!client) {
    throw new AppError(500, 'Search client not initialized')
  }
  try {
    const params = getParamsForIndexName(indexName.split('_')[0])
    const request: AlgoliaRequestType = {
      attributesToHighlight: [],
      hitsPerPage: hitsPerPage,
      indexName: `${ENVIRONMENT}_${indexName}`,
      page: currentPage - 1,
      query: query,
      removeWordsIfNoResults: 'allOptional',
      ...params,
    }
    request.filters =
      filterKey && activeOnly
        ? `idx_key:${filterKey} AND idx_is_active:true`
        : activeOnly
          ? `idx_is_active:true`
          : filterKey
            ? `idx_key:${filterKey}`
            : ''

    const { results } = await client.search({
      requests: [request],
    })
    if (!results?.length) {
      throw new AppError(404, 'No results found')
    }
    if (results && results.length > 0) {
      const { hits, nbPages } = results[0] as SearchResponse<T>
      const cleanedHits = hits.map((hit) => removeIdxPrefix(hit)) as T[]

      return {
        hits: cleanedHits,
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
