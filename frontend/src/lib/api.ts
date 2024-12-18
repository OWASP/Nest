import { API_URL } from '../utils/credentials'
export const loadData = async <T>(
  endpoint: string,
  query: string,
  currentPage: number
): Promise<T> => {
  const response = await fetch(`${API_URL}/${endpoint}?q=${query}&page=${currentPage}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch data: ${response.statusText}`)
  }
  const data: T = await response.json()
  return data
}
