import upperFirst from 'lodash/upperFirst'

export function formatBreadcrumbTitle(text: string): string {
  if (!text) return ''
  return text
    .split('-')
    .map((word) => upperFirst(word))
    .join(' ')
}
