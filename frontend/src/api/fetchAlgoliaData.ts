import { AlgoliaResponseType } from 'types/algolia'
import { API_URL } from 'utils/credentials'
import { AppError } from 'wrappers/ErrorWrapper'
import { removeIdxPrefix } from './utility'

export const fetchAlgoliaData = async <T>(
  indexName: string,
  query = '',
  currentPage = 0,
  hitsPerPage = 25
): Promise<AlgoliaResponseType<T>> => {
  try {
    const response = await fetch(`${API_URL}/idx`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        indexName,
        query,
        page: currentPage,
        hitsPerPage,
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
