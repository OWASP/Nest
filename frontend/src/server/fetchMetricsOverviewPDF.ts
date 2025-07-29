import { handleAppError } from 'app/global-error'
import { API_URL } from 'utils/credentials'

export const fetchMetricsOverviewPDF = async (): Promise<void> => {
  try {
    const baseUrl = API_URL.split('/api')[0]
    const response = await fetch(`${baseUrl}/owasp/project-health-metrics/overview/pdf`, {
      method: 'GET',
      headers: {
        accept: 'application/pdf',
      },
    })

    if (!response.ok) {
      const message = `Failed to fetch metrics overview PDF: ${response.status} ${response.statusText}`
      handleAppError(new Error(message))
    }

    const pdfBlob = await response.blob()
    if (pdfBlob.size === 0) {
      handleAppError(new Error('PDF blob is empty or undefined'))
    }
    const pdfUrl = window.URL.createObjectURL(pdfBlob)
    const link = document.createElement('a')
    link.href = pdfUrl
    const fileName = `owasp_metrics_overview_${new Date().toISOString().split('T')[0]}.pdf`
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(pdfUrl)
  } catch (error) {
    handleAppError(
      error instanceof Error
        ? error
        : new Error('An unexpected error occurred while fetching the PDF')
    )
  }
}
