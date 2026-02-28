import { AppError } from 'app/global-error'
import type { AlgoliaResponse } from 'types/algolia'
import { IDX_URL } from 'utils/env.client'
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
      let errorMessage = 'Search service error'
      try {
        const errorData = await response.json()
        errorMessage = errorData?.error || errorMessage
      } catch {
        // Fallback to default error message if parsing fails
      }
      throw new AppError(response.status, errorMessage)
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
    if (error instanceof AppError || (error instanceof Error && error.name === 'AppError')) {
      throw error
    }
    throw new AppError(500, 'Search service error')
  }
}
