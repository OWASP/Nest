export function formatBreadcrumbTitle(text: string): string {
  if (!text) return ''

  const datePattern = /(\d{4})-(\d{1,2})(-\d{1,2})?/g
  const withPlaceholders = text.replace(datePattern, (match) => match.replace(/-/g, '###HYPHEN###'))

  return withPlaceholders
    .split('-')
    .map((segment) => {
      const restored = segment.replace(/###HYPHEN###/g, '-')
      return restored.charAt(0).toUpperCase() + restored.slice(1)
    })
    .join(' ')
}
