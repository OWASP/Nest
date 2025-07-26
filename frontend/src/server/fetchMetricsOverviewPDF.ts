import { AppError } from 'app/global-error'
import { API_URL } from 'utils/credentials'

export const fetchMetricsOverviewPDF = async (): Promise<void> => {
  try {
    const response = await fetch(`${API_URL}owasp/project-health-metrics/overview-pdf`, {
      method: 'GET',
      headers: {
        accept: 'application/pdf',
      },
      credentials: 'include',
    })

    if (!response.ok) {
      const message = `Failed to fetch metrics overview PDF: ${response.status} ${response.statusText}`
      throw new AppError(response.status, message)
    }

    const pdfBlob = await response.blob()
    if (!pdfBlob) {
      throw new AppError(500, 'PDF blob is empty or undefined')
    }
    const pdfUrl = window.URL.createObjectURL(pdfBlob)
    const link = document.createElement('a')
    link.href = pdfUrl
    link.setAttribute('download', 'owasp-project-health-metrics-overview.pdf')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    if (error instanceof AppError) {
      throw error
    }

    const message = error?.message || 'Unexpected error while fetching metrics overview PDF'
    throw new AppError(500, message)
  }
}
