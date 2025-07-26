import { handleAppError } from 'app/global-error'
import { API_URL } from 'utils/credentials'
export const fetchMetricsPDF = async (path: string, fileName: string): Promise<void> => {
  const response = await fetch(`${API_URL}${path}`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/pdf',
    },
  })
  if (!response.ok) {
    handleAppError(new Error(`Failed to fetch PDF: ${response.status} ${response.statusText}`))
    return
  }
  try {
    const blob = await response.blob()
    if (!blob) {
      handleAppError(new Error('No data received from the server'))
      return
    }
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    handleAppError(error)
  }
}
