import { AppError } from 'app/global-error'
import type { AlgoliaResponse } from 'types/algolia'
import { IDX_URL } from 'utils/credentials'
import { getCsrfToken } from 'utils/utility'

export const fetchAlgoliaData = async <T>(
  indexName: string,
  query = '',
  currentPage = 0,
  hitsPerPage = 25,
  facetFilters: string[] = []
): Promise<AlgoliaResponse<T>> => {
  try {
    if (['projects', 'chapters'].includes(indexName)) {
      facetFilters.push('idx_is_active:true')
    }

    if (!IDX_URL) {
      throw new Error('IDX_URL is not defined')
    }

    const response = await fetch(IDX_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': (await getCsrfToken()) || '',
      },
      credentials: 'include',
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

      return {
        hits: hits,
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
