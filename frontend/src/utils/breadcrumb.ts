export function formatBreadcrumbTitle(text: string): string {
  if (!text) return ''

  const datePattern = /(\d{4})-(\d{1,2})(-\d{1,2})?/g
  const withPlaceholders = text.replaceAll(datePattern, (match) =>
    match.replaceAll('-', '###HYPHEN###')
  )

  return withPlaceholders
    .split('-')
    .map((segment) => {
      const restored = segment.replaceAll('###HYPHEN###', '-')
      return restored.charAt(0).toUpperCase() + restored.slice(1)
    })
    .join(' ')
}
