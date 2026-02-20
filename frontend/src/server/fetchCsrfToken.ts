export const fetchCsrfToken = async (): Promise<string> => {
  if (typeof window !== 'undefined') {
    throw new AppError(500, 'fetchCsrfToken must only be called on the server')
  }
  try {
    if (!CSRF_URL) {
      throw new AppError(500, 'CSRF_URL is not configured')
    }
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
  } catch (error: unknown) {
    if (error instanceof AppError) {
      throw error
    }

    const message =
      (error instanceof Error ? error.message : String(error)) ||
      'Unexpected error while fetching CSRF token'
    throw new AppError(500, message)
  }
// End of file
}
