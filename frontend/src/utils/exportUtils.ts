/**
 * Export utilities for downloading issue data in CSV/JSON formats.
 *
 * This module provides functions to trigger GraphQL export queries
 * and download the resulting data as files.
 */

export type ExportFormat = 'CSV' | 'JSON'

export interface ExportOptions {
    programKey: string
    moduleKey: string
    format: ExportFormat
    label?: string | null
}

export interface ExportResult {
    content: string
    filename: string
    mimeType: string
    count: number
}

/**
 * Triggers a file download in the browser.
 *
 * @param content - The file content as a string
 * @param filename - The name for the downloaded file
 * @param mimeType - The MIME type of the file
 */
export function downloadFile(content: string, filename: string, mimeType: string): void {
    const blob = new Blob([content], { type: mimeType })
    const url = window.URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()

    // Cleanup
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
}

/**
 * Builds the GraphQL query for exporting issues.
 *
 * @param options - Export options including format and filters
 * @returns GraphQL query string
 */
export function buildExportQuery(options: ExportOptions): string {
    const { programKey, moduleKey, format, label } = options
    const labelArg = label && label !== 'all' ? `, label: "${label}"` : ''

    return `
    query ExportModuleIssues {
      getModule(programKey: "${programKey}", moduleKey: "${moduleKey}") {
        exportIssues(format: ${format}${labelArg}) {
          content
          filename
          mimeType
          count
        }
      }
    }
  `
}

/**
 * Parse the GraphQL response to extract export result.
 *
 * @param data - GraphQL response data
 * @returns ExportResult or null if not found
 */
export function parseExportResponse(data: unknown): ExportResult | null {
    if (!data || typeof data !== 'object') return null

    const responseData = data as { getModule?: { exportIssues?: ExportResult } }

    if (!responseData.getModule?.exportIssues) return null

    return responseData.getModule.exportIssues
}

/**
 * Get user-friendly error message for export failures.
 *
 * @param error - The error object
 * @returns Human-readable error message
 */
export function getExportErrorMessage(error: unknown): string {
    if (error instanceof Error) {
        if (error.message.includes('network')) {
            return 'Network error. Please check your connection and try again.'
        }
        if (error.message.includes('timeout')) {
            return 'Export timed out. Try exporting fewer issues.'
        }
        return error.message
    }
    return 'An unexpected error occurred during export.'
}
