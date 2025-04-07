import { CSRF_URL } from 'utils/credentials'
import { AppError } from 'wrappers/ErrorWrapper'

export const fetchCsrfToken = async (): Promise<string> => {
  try {
    const response = await fetch(CSRF_URL, {
      credentials: 'include',
      method: 'GET',
    })

    if (!response.ok) {
      const message = `Failed to fetch CSRF token: ${response.status} ${response.statusText}`
      throw new AppError(response.status, message)
    }

    const data = await response.json()

    if (!data?.csrftoken) {
      throw new AppError(500, 'CSRF token missing in response')
    }

    return data.csrftoken
  } catch (error) {
    if (error instanceof AppError) {
      throw error
    }

    const message = error?.message || 'Unexpected error while fetching CSRF token'
    throw new AppError(500, message)
  }
}
