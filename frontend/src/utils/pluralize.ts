export const pluralize = (count?: number, forms = 's'): string => {
  if (!count) return ''

  const parts = forms.split(',')

  if (parts.length === 1) {
    return count === 1 ? '' : parts[0]
  }
  return count === 1 ? parts[0] : parts[1]
}
