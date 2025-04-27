import { CSRF_URL } from 'utils/credentials'

export const fetchCsrfTokenServer = async (): Promise<string> => {
  try {
    const response = await fetch(CSRF_URL, {
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
