import { AppError } from 'utils/appError'
import type { AlgoliaResponse } from 'types/algolia'
import { IDX_URL } from 'utils/env.client'
import { fetchCsrfToken } from 'server/fetchCsrfToken'

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

    const csrfToken = await fetchCsrfToken();
    // Debug log CSRF token
    // eslint-disable-next-line no-console
    console.log('fetchAlgoliaData: CSRF token:', csrfToken);
    const response = await fetch(IDX_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      credentials: 'include',
      body: JSON.stringify({
        facetFilters,
        hitsPerPage,
        indexName,
        page: currentPage,
        query,
      }),
    });
    // Debug log IDX_URL response status
    // eslint-disable-next-line no-console
    console.log('fetchAlgoliaData: IDX_URL response status:', response.status);
    if (!response.ok) {
      throw new AppError(response.status, 'Search service error');
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
