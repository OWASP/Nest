/**
 * Formats a breadcrumb title by protecting dates, splitting by hyphens,
 * and capitalizing each segment.
 * * @param text - The raw breadcrumb string (ex: "2026-01-10-project-updates")
 * @returns The formatted title (ex: "2026-01-10 Project Updates")
 */
export function formatBreadcrumbTitle(text: string): string {
  if (!text) return ''

  const DATE_TOKEN = '__DATE_HYPHEN__'
  const datePattern = /\d{4}-\d{1,2}(?:-\d{1,2})?/g

  const protectedText = text.replace(datePattern, (match) => match.replaceAll('-', DATE_TOKEN))

  return protectedText
    .split('-')
    .map((segment) => {
      const restored = segment.replaceAll(DATE_TOKEN, '-')
      return restored ? restored[0].toUpperCase() + restored.slice(1) : ''
    })
    .join(' ')
}
