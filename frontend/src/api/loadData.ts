import { API_URL } from 'utils/credentials'
import { AppError } from 'wrappers/ErrorWrapper'

export const loadData = async <T>(
  endpoint: string,
  query: string,
  currentPage: number
): Promise<T> => {
  const response = await fetch(
    `${API_URL}/${endpoint}?` +
      new URLSearchParams({
        q: query,
        page: currentPage.toString(),
      }).toString()
  )
  if (!response.ok) {
    throw new AppError(
      response.status === 404 ? 404 : 500,
      response.status === 404 ? 'Resource not found' : 'Server error occurred'
    )
  }
  return await response.json()
}
