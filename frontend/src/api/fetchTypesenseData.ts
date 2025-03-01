import { AppError } from 'wrappers/ErrorWrapper'

export interface TypesenseResponseType<T> {
  hits: T[]
  totalPages: number
}

const TYPESENSE_URL = 'http://localhost:8000/search/'

export const fetchTypesenseData = async <T>(
  indexName: string,
  query = '*',
  currentPage = 1,
  hitsPerPage = 25
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
      }),
    })

    if (!response.ok) {
      throw new AppError(response.status, 'Search service error')
    }

    const results = await response.json()
    if (results && results.hits && results.hits.length > 0) {
      const { hits, nbPages } = results

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
