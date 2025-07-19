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
    throw new Error(`Failed to fetch PDF: ${response.statusText}`)
  }
  try {
    const blob = await response.blob()
    if (!blob) {
      throw new Error('No PDF data received')
    }
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    handleAppError(error)
  }
}
