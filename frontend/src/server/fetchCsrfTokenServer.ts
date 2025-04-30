export const fetchCsrfTokenServer = async (): Promise<string> => {
  const response = await fetch(process.env.NEXT_SERVER_CSRF_URL, {
    credentials: 'include',
    method: 'GET',
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch CSRF token: ${response.status} ${response.statusText}`)
  }
  const data = await response.json()

  return data.csrftoken
}
