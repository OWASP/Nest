const DATE_TOKEN = ':::DATE_HYPHEN:::'
const DATE_PATTERN = /\d{4}-\d{1,2}(?:-\d{1,2})?/g

/**
 * Formats a breadcrumb title by protecting dates, splitting by hyphens,
 * and capitalizing each segment.
 *
 * @param text - The raw breadcrumb string (ex: "2026-01-10-project-updates")
 * @returns The formatted title (ex: "2026-01-10 Project Updates")
 */
export function formatBreadcrumbTitle(text: string): string {
  if (!text) return ''

  const protectedText = text.replace(DATE_PATTERN, (match) => match.replaceAll('-', DATE_TOKEN))

  return protectedText
    .split('-')
    .map((segment) => {
      const restored = segment.replaceAll(DATE_TOKEN, '-')
      return restored ? restored[0].toUpperCase() + restored.slice(1) : ''
    })
    .join(' ')
}
