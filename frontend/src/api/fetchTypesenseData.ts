import { TYPESENSE_URL } from 'utils/credentials'
import { AppError } from 'wrappers/ErrorWrapper'
import { removeIdxPrefix } from './utility'

export interface TypesenseResponseType<T> {
  hits: T[]
  totalPages: number
}

export const fetchTypesenseData = async <T>(
  indexName: string,
  query = '*',
  currentPage = 1,
  hitsPerPage = 25,
  sortBy = '',
): Promise<TypesenseResponseType<T>> => {
  try {
    const response = await fetch(TYPESENSE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        hitsPerPage,
        indexName,
        page: currentPage,
        query,
        sortBy,
      }),
    })

    if (!response.ok) {
      throw new AppError(response.status, 'Search service error')
    }

    const results = await response.json()
    if (results && results?.hits.length > 0) {
      const { hits, nbPages } = results
      const cleanedHits = hits.map((hit) => removeIdxPrefix(hit))
      return {
        hits: cleanedHits as T[],
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
