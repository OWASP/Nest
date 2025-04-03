import { AppError } from 'wrappers/ErrorWrapper'

export const getInitialCsrfToken = async () => {
  try {
    const response = await fetch('http://localhost:8000/csrf', {
      method: 'GET',
    })

    if (!response.ok) {
      throw new AppError(response.status, 'Failed to fetch CSRF token')
    }

    const data = await response.json()
    document.cookie = `csrftoken=${data.csrftoken}; path=/; SameSite=Lax`
    return data.csrftoken
  } catch (error) {
    if (error instanceof AppError) {
      throw error
    }
    throw new AppError(500, 'Internal server error')
  }
}
