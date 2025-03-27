import { AlgoliaResponseType } from 'types/algolia'
import { IDX_URL } from 'utils/credentials'
import { AppError } from 'wrappers/ErrorWrapper'
import { removeIdxPrefix } from './utility'

export const fetchAlgoliaData = async <T>(
  indexName: string,
  query = '',
  currentPage = 0,
  hitsPerPage = 25,
  facetFilters = []
): Promise<AlgoliaResponseType<T>> => {
  try {
    if (['projects', 'chapters'].includes(indexName)) {
      facetFilters.push('idx_is_active:true')
    }

    const response = await fetch(IDX_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        facetFilters,
        hitsPerPage,
        indexName,
        page: currentPage,
        query,
      }),
    })

    if (!response.ok) {
      throw new AppError(response.status, 'Search service error')
    }

    const results = await response.json()
    if (results && results.hits.length > 0) {
      const { hits, nbPages } = results
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
