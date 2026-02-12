import type { AlgoliaResponse } from 'types/algolia'
import { IDX_URL } from 'utils/env.client'
import { getCsrfToken } from 'utils/utility'

export const fetchAlgoliaData = async <T>(
  indexName: string,
  query = '',
  currentPage = 0,
  hitsPerPage = 25,
  facetFilters: string[] = [],
  signal?: AbortSignal
): Promise<AlgoliaResponse<T>> => {
  try {
    const filters =
      ['projects', 'chapters'].includes(indexName)
        ? [...facetFilters, 'idx_is_active:true']
        : facetFilters

    if (!IDX_URL) {
      return { hits: [], totalPages: 0 }
    }

    const response = await fetch(IDX_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': (await getCsrfToken()) || '',
      },
      credentials: 'include',
      body: JSON.stringify({
        facetFilters: filters,
        hitsPerPage,
        indexName,
        page: currentPage,
        query,
      }),
      signal, 
    })

    if (!response.ok) {
      return { hits: [], totalPages: 0 }
    }

    const results = await response.json()

    return {
      hits: results?.hits || [],
      totalPages: results?.nbPages || 0,
    }
  } catch (error) {
    if ((error as Error).name === 'AbortError') {
      return { hits: [], totalPages: 0 }
    }

    return { hits: [], totalPages: 0 }
  }
}
