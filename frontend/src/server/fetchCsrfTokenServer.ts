import { CSRF_URL, CSRF_URL_DOCKER, ENVIRONMENT } from 'utils/credentials'

export const fetchCsrfTokenServer = async (): Promise<string> => {
  const csrfUrl = ENVIRONMENT === 'docker' ? CSRF_URL_DOCKER : CSRF_URL
  try {
    const response = await fetch(csrfUrl, {
      credentials: 'include',
      method: 'GET',
    })

    if (!response.ok) {
      throw new Error(`Failed to fetch CSRF token: ${response.status} ${response.statusText}`)
    }

    const data = await response.json()
    return data.csrftoken
  } catch (error) {
    if (error) {
      throw error
    }
  }
}
