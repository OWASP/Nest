export const fetchCsrfTokenServer = async (): Promise<string> => {
  const url = process.env.NEXT_SERVER_CSRF_URL

  if (!url) {
    throw new Error('NEXT_SERVER_CSRF_URL is not defined in the environment variables.')
  }
  const response = await fetch(url, {
    credentials: 'include',
    method: 'GET',
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch CSRF token: ${response.status} ${response.statusText}`)
  }
  const data = await response.json()

  return data.csrftoken
}
